from pprint import pprint

category_keys = {'Genuine': {}, 'Fake': {}}
created = dict({'Train': category_keys, 'Test': category_keys})
pprint(created['Test'])
