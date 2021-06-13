# Python Modules
import os
import json
import datetime
from multiprocessing import Process
from multiprocessing import Manager

import pandas as pd

from tqdm import tqdm

# Local Modules
from datadict import data_dict


def get_links(files, start, end):
    """Load the data gathered form Alexa and PhishTank and get the links."""
    links = {'Genuine': None, 'Fake': None}
    for key, name in files.items():
        filename = os.path.join(os.path.abspath('.'), 'datasets', name)
        dataframe = pd.read_csv(filename, sep=",", index_col=0)
        print(dataframe.head(2))
        if key == 'Genuine':
            links[key] = 'http://' + dataframe.iloc[start:end, 0]
        else:
            links[key] = dataframe.iloc[start:end, 0]

    return links


def create_dataset(links, key, category, created):
    """Get the links and create a dataset of the attributes."""
    dataset = []
    errors = []
    filename = 'Train/' + category + str(key) + '.csv'

    start = datetime.datetime.now()
    for i, link in enumerate(tqdm(links, unit='URL')):
        try:
            dataset.append(data_dict(link))
        except Exception as general_error:
            errors.append(link)
            print('Error', general_error)

        if i % 10 == 0:
            temp_dataset = pd.DataFrame(dataset)
            temp_errors = pd.DataFrame(errors)
            temp_key = str(key + i)
            temp_filename = 'Train/' + category + temp_key + 'Temp.csv'
            save_dataset(temp_dataset, temp_errors, temp_filename)
            print('Saved Dataset Till', i, 'Values')
    end = datetime.datetime.now()

    dataset = pd.DataFrame(dataset)
    errors = pd.DataFrame(errors)
    save_dataset(dataset, errors, filename)

    created[category][key]['Created'] = str(datetime.datetime.now())
    created[category][key]['Shape'] = dataset.shape
    created[category][key]['Columns'] = list(dataset.columns)
    created[category][key]['Filename'] = filename
    created[category][key]['Runtime'] = str(end - start)


def save_dataset(dataset, errors, filename):
    """Save the datset into CSV file."""
    path_dataset = os.path.join(os.path.abspath('.'), 'datasets', filename)
    path_errors = os.path.join(os.path.abspath('.'), 'datasets/errors',
                               filename)
    dataset.to_csv(path_dataset, index=False)
    errors.to_csv(path_errors, index=False)
    print('Files Saved:\n', path_dataset, '\n', path_errors)


def get_datasets():
    """Dataset Creation - Parallelization."""
    files = {'Genuine': 'AlexaTop1m.csv', 'Fake': 'PhishTankMarch1st.csv'}

    category_keys = {}
    url_data = {'Genuine': {}, 'Fake': {}}
    for i in [10, 12, 14]:
        start = i * 100
        end = (i + 1) * 100
        print('Start: ', start, 'End: ', end)
        links = get_links(files, start, end)

        url_data['Genuine'][end] = links['Genuine']
        # url_data['Fake'][end] = links['Fake']

        category_keys[end] = {}

    # Shared Resources
    manager = Manager()
    created = manager.dict({'Genuine': category_keys, 'Fake': category_keys})

    processes = []
    for category, data in tqdm(url_data.items(), unit='Class'):
        for key, links in tqdm(data.items(), unit='Cent'):
            process = Process(target=create_dataset,
                              args=(links, key, category, created))
            processes.append(process)
            process.start()

    for process in tqdm(processes, unit='Process'):
        process.join()

    with open('datasets/metadata.json', 'w') as file:
        json.dump(created.copy(), file, indent=4)

    print('Dataset Creation Completed')


get_datasets()
