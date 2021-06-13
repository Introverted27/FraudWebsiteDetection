# Python Modules
import os
import json
import signal

from pprint import pprint
from datetime import datetime
from functools import partial

from multiprocessing import Pool
# from multiprocessing import Process
# from multiprocessing import Manager
from multiprocessing import cpu_count
from multiprocessing import set_start_method

import pandas as pd

from tqdm import tqdm

# Local Modules
from datadict import data_dict


class TimeOutException(Exception):
    pass


def alarm_handler(signum, frame):
    print("Timeout: ALARM signal received")
    raise TimeOutException()


def _metadata(action, metadata=None):
    filename = 'temp_metadata.json'
    path = os.path.join(os.path.abspath('.'), 'datasets', filename)
    if action == 'save':
        with open(path, 'wb') as file:
            json.dump(metadata, file, indent=4)
    elif action == 'read':
        with open(path, 'wb') as file:
            return json.load(file)


def _create_metadata(keys, dataset, filename, runtime):
    created = {}
    created[keys[0]] = {}
    created[keys[0]]['StartEnd'] = [keys[0], keys[1]]
    created[keys[0]]['Created'] = str(datetime.now())
    created[keys[0]]['Shape'] = dataset.shape
    created[keys[0]]['Columns'] = list(dataset.columns)
    created[keys[0]]['Filename'] = filename
    created[keys[0]]['Runtime'] = runtime
    _metadata(action='save', metadata=created)


def _save_dataset(dataset, errors, filename):
    """Save the datset into CSV file."""
    path_dataset = os.path.join(os.path.abspath('.'), 'datasets', filename)
    path_errors = os.path.join(os.path.abspath('.'), 'datasets/errors',
                               filename)
    dataset.to_csv(path_dataset, index=False)
    print(datetime.now().time(), 'File Saved:\n', path_dataset)
    errors.to_csv(path_errors, index=False)
    print(datetime.now().time(), 'Error File Saved:\n', path_errors)


# def get_datasets_parallel():
#     """Dataset Creation - Parallelization."""
#     files = {'Genuine': 'AlexaTop1m.csv', 'Fake': 'PhishTankMarch2021.csv'}
#     links_all = get_links(files, start=0, end=10000)
#
#     print(datetime.now().time(), 'Creating shared resources.')
#     category_keys = {'Genuine': {}, 'Fake': {}}
#     manager = Manager()
#     created = manager.dict()
#     processes = []
#
#     start_time = datetime.now()
#     print(datetime.now().time(), 'Starting the processes.')
#
#     for category, urls in links_all.items():
#         if category == 'Genuine':
#             continue
#         # print(category, type(urls), len(urls))
#         # Shared Resources
#
#         for i in range(50):
#             step = 200
#             keys = (i * step, (i + 1) * step)
#             # print(keys)
#             links_subset = urls[keys[0]:keys[1]]
#             print(
#                 datetime.now().time(),
#                 'Subset created: {}, Category: {}'.format(
#                     len(links_subset), category))
#             process = Process(target=get_data,
#                               args=(links_subset, keys, category))
#             processes.append(process)
#             process.start()
#
#     for process in processes:
#         process.join()
#
#     with open('datasets/metadata.json', 'w') as file:
#         json.dump(created.copy(), file, indent=4)
#
#     print(datetime.now().time(), 'Dataset extraction completed')
#     print('Total time taken:', datetime.now() - start_time)


def get_links(files, start=0, end=10000):
    """Load the data gathered form Alexa and PhishTank and get the links."""
    links = {'Genuine': None, 'Fake': None}
    for key, name in files.items():
        print(datetime.now().time(), 'Extracting {} links'.format(key.lower()))
        filename = os.path.join(os.path.abspath('.'), 'datasets', name)
        dataframe = pd.read_csv(filename, sep=",")
        print(datetime.now().time(), 'DataFrame created.', dataframe.shape)

        urls = dataframe.iloc[start:end, 1]
        print(datetime.now().time(),
              '{} to {} entries extracted.'.format(start, end), urls.shape)
        # print(urls.head(2))

        if key == 'Genuine':
            urls = 'http://' + urls
            links[key] = urls.tolist()
        else:
            links[key] = urls.tolist()

        print(key, links[key][:2])
    return links


def get_data(links, keys, category):
    """Get the links and create a dataset of the attributes."""
    dataset = []
    errors = []
    filename = '{}_{}_{}.csv'.format(category, keys[0], keys[1])

    start = datetime.now()
    for i, link in enumerate(tqdm(links, unit='{} URL'.format(category))):
        if i > 0 and i % 10 == 0:
            print(
                datetime.now().time(),
                '{} files processed (start:{} end:{})'.format(
                    str((i)), keys[0], keys[1]))

        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(60)
        try:
            data = data_dict(link)
            data['category'] = category
            dataset.append(data)
        except TimeOutException as ex:
            errors.append({'url': link, 'error': ex})
            print(datetime.now().time(), ex)
        except Exception as general_error:
            errors.append({'url': link, 'error': general_error})
            print(datetime.now().time(), 'Error found:\n', general_error)
        signal.alarm(0)
    end = datetime.now()

    dataset = pd.DataFrame(dataset)
    errors = pd.DataFrame(errors)
    _save_dataset(dataset, errors, filename)

    runtime = str(end - start)
    _create_metadata(keys, dataset, filename, runtime)

    return None


def create_dataset(metadata=False):
    files = {'Genuine': 'AlexaTop1m.csv', 'Fake': 'PhishTankMarch2021.csv'}
    links_all = get_links(files, start=0, end=10000)

    metadata = {'Genuine': {}, 'Fake': {}}
    for category, urls in links_all.items():
        step = 2000
        start = 0
        end = 10000
        keys = zip(range(start, end - step, step),
                   range(start + step, end, step))
        print(datetime.now().time(), 'Keys Created:\n', list(keys))
        keys = zip(range(start, end - step, step),
                   range(start + step, end, step))
        created = []
        for key in keys:
            if category == 'Genuine' and key[0] in [0]:
                continue
            # created = _extract_data(urls, category, key, step=100)
            print(datetime.now().time(),
                  'Creating Subset: Start {} End {}'.format(key[0], key[1]))
            links = urls[key[0]:key[1]]
            print(
                datetime.now().time(),
                'Subset created: {}, Category: {}'.format(
                    len(links), category))

            func = partial(get_data, keys=key, category=category)
            with Pool(processes=max(1, cpu_count() - 4)) as pool:
                pool.map(func, [links])
            if metadata:
                temp_metadata = _metadata(action='read')
                created.append(temp_metadata)
                metadata[category][key[0]] = created

    filename = 'metadata.json'
    path = os.path.join(os.path.abspath('.'), 'datasets', filename)
    with open(path, 'w') as file:
        json.dump(metadata, file, indent=4)


# def main():
#

if __name__ == '__main__':
    # set_start_method("spawn")
    create_dataset(metadata=True)
    # step = 2000
    # start = 0
    # end = 10000
    # keys = zip(range(start, end - step, step), range(start + step, end, step))
    # pprint(list(keys))

# get_datasets_parallel()

# link = sys.argv[1]
# print(datadict(link, port=False))

# filename = os.path.join(os.path.abspath('.'), 'datasets', 'AlexaTop1m.csv')
# dataframe = pd.read_csv(filename, sep=",", index_col = 0)
# print(dataframe.head(2))
# print(dataframe.describe)
# print(dataframe.iloc[0, 0])
