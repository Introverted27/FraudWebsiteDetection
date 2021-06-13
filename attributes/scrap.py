# Installed Modules
from bs4 import BeautifulSoup as BS

# Python In-Built Modules
import requests
import socket


def scrap(link):
    try:
        page = requests.get(link)
    except socket.error as exc:
        if 'CertificateError' in str(exc):
            return -1
        # print("socket.error : %s" % exc)
        return None
    except Exception as e:
        # print('Scraping Error:', e)
        return None
    html = page.text
    soup = BS(html, 'html.parser')
    return soup
