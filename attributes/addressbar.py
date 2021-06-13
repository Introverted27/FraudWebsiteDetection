# Installed Modules
from bs4 import BeautifulSoup
import requests
import whois

# Machine Learning

# Python In-Built Modules
import datetime
import re

# Local Modules
from attributes.ip import contains_ipv4, contains_ipv6
from . import sslchk
from . import portchk
from .domain import get_domain_name


class AddressBar(object):
    """docstring for URL.

    """
    def __init__(self, link):
        # super(URL, self).__init__()
        self.link = link
        self.domain = get_domain_name(self.link)
        # print('URL:', self.link)
        # print('Domain', self.domain)

    def ip_in_url(self):
        # print('****************** IP in URL ******************')
        link = self.link
        # print(link)
        if contains_ipv4(link) or contains_ipv6(link):
            return -1
        else:
            return 1

    def length(self):
        # print('****************** Long URL ******************')
        # print('URL Length:', len(self.link))
        return (len(self.link))

    def tiny_url(self):
        # print('****************** Tiny URL ******************')
        link = self.link
        try:
            if 'http://' in link or 'https://' in link:
                response = requests.get(link).url
            else:
                link = 'http://' + link + '/'
                response = requests.get(link).url
        except Exception as e:
            # print('Tiny URL: Error:  ', e)
            return 0
        response = response.replace('https://', '', 1)
        response = response.replace('http://', '', 1)
        response = response.replace('www.', '', 1)
        response = response.replace('/', '', 1)
        link = link.replace('https://', '', 1)
        link = link.replace('http://', '', 1)
        link = link.replace('www.', '', 1)
        link = link.replace('/', '', 1)
        if response == link:
            return 1
        else:
            # print('Tiny URL: ', response, link)
            return -1

    def at_symbol(self):
        # print("****************** '@' Symbol ******************")
        if self.link.find('@') != -1:
            return -1
        else:
            return 1

    def redirects(self):
        # print("****************** '//' Redirecting ******************")
        if self.link.find('//', 7) != -1:
            return -1
        else:
            return 1

    def dash_symbol(self):
        # print("****************** '-' Symbol******************")
        if self.domain.find('@') != -1:
            return -1
        else:
            return 1

    def subdomain(self):
        # print("****************** Subdomains ******************")
        try:
            domain = get_domain_name(self.link)
        except Exception as e:
            # print('subdomain : Error:  ', e)
            return 0
        dots = [m.start() for m in re.finditer('[.]', domain)]
        # print(domain, len(dots))
        return (len(dots))

    def verify_ssl(self):
        # print("****************** SSl Certificate ******************")
        s = sslchk.get_ssl(self.link)
        # print('url ssl :', s)
        return s

    def domain_time(self):
        # print("****************** Domain Registration Time ******************")
        try:
            w = whois.whois(self.link)
        except:
            # print('domain time: exception', self.link)
            return 0
        create = w.creation_date
        expire = w.expiration_date
        # print(create, expire)
        if isinstance(create, list) and isinstance(expire, list):
            time = (expire[0] - create[0]).days
        elif isinstance(create, list) or isinstance(expire, list):
            if isinstance(create, list):
                time = (expire - create[0]).days
            else:
                time = (expire[0] - create).days
        elif isinstance(create, datetime.date) and isinstance(
                expire, datetime.date):
            time = (expire - create).days
        else:
            time = 0
        return time

    def favicon(self):
        # print("****************** Favicon ******************")
        try:
            if 'http://' in self.link or 'https://' in self.link:
                res = requests.get(self.link)
            else:
                link = 'http://' + self.link + '/'
                res = requests.get(link)
        except Exception as e:
            # print('favicon : Error:  ', e)
            return 0
        page = res.text
        soup = BeautifulSoup(page, features='html.parser')
        icon_link = soup.find("link", rel='icon')
        # print(self.link)
        if icon_link:
            if str(icon_link).find('http') != -1:
                domain = get_domain_name(self.link, tld=False, subdomain=False)
                if domain in str(icon_link):
                    return 1
                # print(icon_link)
                return -1
            else:
                return 1
        else:
            # print('favicon not found')
            return -1

    def ports(self):
        # print("****************** Port Check ******************")
        close = [21, 22, 23, 445, 1433, 1521, 3306, 3389]
        ports = portchk.ports_open(self.domain)
        # print(ports)
        if 80 in ports or 443 in ports:
            for p in close:
                if p in ports:
                    return -1
            return 1
        else:
            return -1

    def https(self):
        # print("****************** HTTPS in Domain ******************")
        # print('https: ', domain)
        if self.domain.find('https') != -1:
            return -1
        else:
            return 1


#
# arg = sys.argv[1]
# U = URL(arg)
# print(U.ip_in_url(), '\n')
# print(U.tiny(), '\n')
# print(U.long(), '\n')
# print(U.at_symbol(), '\n')
# print(U.redirect(), '\n')
# print(U.dash_symbol(), '\n')
# print(U.subdomain(), '\n')
# print(U.verify_ssl(), '\n')
# print(U.domain_time(), '\n')
# print(U.favicon(), '\n')
# print(U.port(), '\n')
# print(U.https(), '\n')
