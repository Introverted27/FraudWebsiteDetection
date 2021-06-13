# Python Modules
import os
import pickle
import pandas as pd

# Local Modules
from attributes.addressbar import URL
from attributes.abnormal import Abnormal


def data(link, **kwargs):
    port = kwargs.get('port', False)
    U = URL(link)
    A = Abnormal(link)
    d = {
        'Having_IP_Address': U.ip_in_url(),
        'URL_Length': U.length(),
        'Shortening_Service': U.tiny(),
        'Having_At_Symbol': U.at_symbol(),
        'Double_slash_redirecting': U.redirect(),
        'Prefix_Suffix': U.dash_symbol(),
        'Having_Sub_Domain': U.subdomain(),
        'SSLfinal_State': U.verify_ssl(),
        'Domain_registeration_length': U.domain_time(),
        'Favicon': U.favicon(),
        'HTTPS_token': U.https()
    }
    if port:
        d['Port'] = U.ports()
    else:
        d['Port'] = 0
        print('Port = ', d['Port'])
    df = pd.DataFrame([d])
    df = df.fillna(0)
    print(A)
    print(d)
    return df


def pred(link):
    filename = 'SVM_23Aug.sav'
    model = pickle.load(open(filename, 'rb'))
    df = data(link, port=False)
    return model.predict(df), model.predict_proba(df)


print('=== [ SVM Model Prediction ]  ===')
a = pred('www.google.com')
print(a)
# print(a[0], a[1][0][1])
