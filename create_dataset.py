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
    print(datetime.now().time(), "Timeout: ALARM signal received")
    raise TimeOutException()


def _create_metadata(keys, dataset, filename, runtime):
    created = {}
    created[keys[0]] = {}
    created[keys[0]]['StartEnd'] = [keys[0], keys[1]]
    created[keys[0]]['Created'] = str(datetime.now())
    created[keys[0]]['Shape'] = dataset.shape
    created[keys[0]]['Columns'] = list(dataset.columns)
    created[keys[0]]['Filename'] = filename
    created[keys[0]]['Runtime'] = runtime
    # _metadata(action='save', metadata=created)
    return created


def _save_dataset(dataset, errors, filename):
    """Save the datset into CSV file."""
    path_dataset = os.path.join(os.path.abspath('.'), 'datasets', filename)
    path_errors = os.path.join(os.path.abspath('.'), 'datasets/errors',
                               filename)
    dataset.to_csv(path_dataset, index=False)
    print(datetime.now().time(), 'File Saved:\n', path_dataset)
    errors.to_csv(path_errors, index=False)
    print(datetime.now().time(), 'Error File Saved:\n', path_errors)


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
    for i, link in enumerate(tqdm(links, unit='URL ({})'.format(category))):
        # if i <= 1000:
        #     continue

        # if i > 0 and i % 1000 == 0:
        #     temp_filename = filename.replace(category,
        #                                      category + 'temp_' + str(i))
        #     _save_dataset(pd.DataFrame(dataset), pd.DataFrame(errors),
        #                   temp_filename)

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
    metadata = _create_metadata(keys, dataset, filename, runtime)

    return metadata


# metadata = {'Genuine': {}, 'Fake': {}}
files = {'Genuine': 'AlexaTop1m.csv', 'Fake': 'PhishTankMarch2021.csv'}
links_all = get_links(files, start=0, end=10000)

category = 'Genuine'
# category = 'Fake'
# keys = (0, 2500)
# keys = (2500, 5000)
# keys = (5000, 7500)
# keys = (7500, 10000)

keys = (0, 1000)
keys = (1000, 2000)
keys = (2000, 3000)
# keys = (3000, 4000)
# keys = (4000, 5000)
# keys = (5000, 6000)
# keys = (6000, 7000)
# keys = (7000, 8000)
# keys = (8000, 9000)
# keys = (9000, 10000)
print(keys)
links = links_all[category][keys[0]:keys[1]]
metadata = get_data(links=links, keys=keys, category=category)

filename = 'metadata_{}_{}_{}.json'.format(category.lower(), str(keys[0]),
                                           str(keys[1]))
path = os.path.join(os.path.abspath('.'), 'datasets', filename)
with open(path, 'w') as file:
    json.dump(metadata, file, indent=4)
