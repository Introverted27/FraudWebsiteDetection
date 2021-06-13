# Installed Modules
from tld import get_tld
from OpenSSL import crypto
from datetime import datetime
import requests

# Python In-Built Modules
import ssl
import socket


def get_domain_name(url, **kwargs):
    tld = kwargs.get('tld', True)
    subdomain = kwargs.get('subdomain', True)
    if 'http://' in url or 'https://' in url:
        obj = get_tld(url, as_object=True)
    else:
        url = 'http://' + url + '/'
        obj = get_tld(url, as_object=True)

    if tld is False:
        if obj.subdomain == '' or subdomain is False:
            domain = obj.domain
        else:
            domain = obj.subdomain + '.' + obj.domain
    else:
        if obj.subdomain == '' or subdomain is False:
            domain = obj.domain + '.' + obj.tld
        else:
            domain = obj.subdomain + '.' + obj.domain + '.' + obj.tld
    return domain


def get_ssl(url):
    trusted = [
        'Actalis', 'Buypass', 'Certum', 'Comodo', 'Cybertrust',
        'Deutsche Telekom', 'DigiCert', 'DigiCert Inc'
        'Entrust', 'Entrust Certification Authority', 'Gandi', 'GlobalSign',
        'GoDaddy', 'Go Daddy', 'GeoTrust', 'Google',
        'Google Internet Authority', 'Google', 'IdenTrust', 'InCommon',
        "Let's Encrypt", 'Microsoft', 'Network Solutions', 'QuoVadis',
        'RapidSSL', 'Secom', 'StartCom', 'Starfield', 'Thawte', 'SwissSign',
        'Symantec', 'Trustwave', 'Unizeto', 'Verizon', 'WISeKey Group'
    ]

    try:
        domain = get_domain_name(url)
        domain_name = get_domain_name(url, tld=False, Subdomain=False)
    except Exception as e:
        # print('ssl : exception:', e)
        return 0

    # print('--------------', domain, '--------------')

    try:
        raw_cert = ssl.get_server_certificate((domain, 443))
    except Exception as e:
        # print('ssl : exception:', e)
        return 0

    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, raw_cert)
    now = datetime.now()
    notAfterDecoded = x509.get_notAfter().decode('utf-8')
    not_after = datetime.strptime(notAfterDecoded, "%Y%m%d%H%M%SZ")
    notBeforerDecoded = x509.get_notBefore().decode('utf-8')
    not_before = datetime.strptime(notBeforerDecoded, "%Y%m%d%H%M%SZ")
    issuer = x509.get_issuer().CN
    # print('ssl: ', (not_after - not_before).days, domain_name, issuer)

    if (not_after - not_before).days >= 365:
        subject = x509.get_subject()
        issued_to = subject.CN
        for name in trusted:
            if name.lower() in issuer.lower():
                # print('ssl: ', name, issuer)
                return 1
    elif 'Google' in issuer or "Let's Encrypt" in issuer:
        # print("Google or Let's Encrypt: ", (not_after - not_before).days)
        return 1
    else:
        # print('ssl:  time < 365', (not_after - not_before).days, issuer)
        return -1


# print(get_ssl('https://www.cybervie.com'))
# print(get_ssl('http://www.pagebusiness.co.vu/'))
# print(get_ssl('https://www.github.com/'))
# print(get_ssl('https://www.microsoft.com/'))
# print(get_ssl('https://www.google.com/'))
