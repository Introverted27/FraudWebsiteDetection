import requests

import whois


def hostname(webpg):
    try:
        who = whois.whois(webpg)
    except:
        try:
            webpg = requests.get(webpg).url
            who = whois.whois(webpg)
        except Exception as e:
            # print('Error:', webpg)
            # print(e)
            return None

    if who == None or who.domain_name == None:
        host = None
    elif isinstance(who.domain_name, list):
        host = who.domain_name[0].lower()
    else:
        host = who.domain_name.lower()
    return host
