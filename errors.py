import os
import json

from datetime import datetime

import pandas as pd

# Local Modules
from datadict import data_dict

filename = os.path.join(os.path.abspath('.'), 'datasets/errors',
                        'Fake_2000_3000.csv')
dataframe = pd.read_csv(filename, sep=",")
urls = dataframe.iloc[:, 0].tolist()
for link in urls:
    data_dict(link)
    print('\n')
    # try:
    #     print(datetime.now().time(), 'Processing:\n', link)
    #     data_dict(link)
    # except Exception as general_error:
    #     print(datetime.now().time(), 'Error found:\n', general_error)
