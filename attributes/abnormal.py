# Installed Modules
from bs4 import BeautifulSoup as BS
from tld import get_tld
import requests
import whois

# Machine Learning
import pandas as pd

# Python In-Built Modules
from html.parser import HTMLParser
import datetime
import socket
import ssl
import sys
import re

# Local Modules
from .domain import get_domain_name
from .scrap import scrap
from .host import hostname


class Abnormal(object):
    """docstring for Abnormal."""
    def __init__(self, link):
        self.link = link
        self.soup = scrap(link)
        self.domain = get_domain_name(link, tld=False, subdomain=False)
        self.host = hostname(link)
        self.ipv4 = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        # print('URL:', self.link)
        # print('Domain', self.domain, 'Host:', self.host)

    def req_url(self):
        # print('****************** Request URL ******************', '\n')
        tags = ['img', 'audio', 'video', 'track', 'embed', 'source', 'iframe']
        num = dict([(key, 0) for key in tags])
        total = dict([(key, 0) for key in tags])
        percent = dict([(key, 0) for key in tags])
        if self.ipv4.search(str(self.link)):
            # print('IP in url:', self.link)
            return dict([(key, 0) for key in tags])
        if self.soup is None:
            return dict([(key, 0) for key in tags])
        elif self.soup == -1:
            return dict([(key, -1) for key in tags])

        for tag in tags:
            values = self.soup.find_all(tag)
            for i, val in enumerate(values):
                if tag == 'source':
                    val = val.get('srcset', None)
                else:
                    val = val.get('src', None)

                if val is None:
                    pass
                elif self.domain in val:
                    total[tag] = total[tag] + 1
                elif (re.compile(r'^#').match(val)
                      or re.compile(r'^/').match(val)):
                    total[tag] = total[tag] + 1
                else:
                    total[tag] = total[tag] + 1
                    num[tag] = num[tag] + 1

            if total[tag] == 0:
                percent[tag] = 0
            else:
                percent[tag] = round((num[tag] / total[tag]) * 100, 2)
        return percent

    def url_anchor(self):
        # print('****************** URL of Anchor ******************', '\n')
        if self.ipv4.search(str(self.link)):
            # print('IP in url:', self.link)
            return 0
        if self.soup is None:
            return 0
        elif self.soup == -1:
            return -1
        anchors = self.soup.find_all('a')
        num = 0
        total = 0
        for i, anchor in enumerate(anchors):
            href = anchor.get('href', '')
            empty = [
                re.compile(r'^#$'),
                re.compile(r'^#skip$'),
                re.compile(r'^#content$'),
                re.compile(r'^javascript::void\(0\)$')
            ]

            if self.domain and self.domain in href:
                total += 1
            elif (empty[0].match(href) or empty[1].match(href)
                  or empty[2].match(href) or empty[3].match(href)):
                total += 1
                num += 1
            elif self.host and self.host in href and self.domain not in href:
                num = num + 1
            elif (re.compile(r'^#').match(href)
                  or re.compile(r'^/').match(href)):
                total += 1
            else:
                total += 1
                num += 1
        if total == 0:
            percent = 0
        else:
            percent = (num / total) * 100
        return round(percent, 3)

    def links_in_tags(self):
        # print('****** Links in <Meta>, <Script> and <Link> tags ******', '\n')
        tags = ['meta', 'script', 'link']
        num = dict([(key, 0) for key in tags])
        total = dict([(key, 0) for key in tags])
        percent = dict([(key, 0) for key in tags])
        urls = dict([(key, []) for key in tags])

        if self.ipv4.search(str(self.link)):
            # print('IP in url:', self.link)
            return dict([(key, 0) for key in tags])
        if self.soup is None:
            return dict([(key, 0) for key in tags])
        elif self.soup == -1:
            return dict([(key, -1) for key in tags])

        for tag in tags:
            values = self.soup.find_all(tag)
            total_url = 0
            for i, val in enumerate(values):
                if tag == 'link':
                    href = val.get('href', None)
                    if self.domain in str(href):
                        total_url += 1
                    else:
                        total_url += 1
                        num[tag] += 1
                else:
                    urls = re.findall(
                        'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', str(val))
                    for j, url in enumerate(urls):
                        if self.domain in url:
                            total_url += 1
                        else:
                            total_url += 1
                            num[tag] += 1
                total[tag] = total_url
            if total[tag] == 0:
                percent[tag] = 0
            else:
                percent[tag] = round((num[tag] / total[tag]) * 100, 3)

        return percent

    def sfh(self):
        # print('************** Server Form Handler(SFH) ************** ', '\n')
        if self.ipv4.search(str(self.link)):
            # print('IP in url:', self.link)
            return 0
        num = 0
        total = 0
        if self.soup is None:
            return 0
        forms = self.soup.find_all('form')
        empty = [
            re.compile(r'^#$'),
            re.compile(r'^about: blank$'),
            re.compile(r'^javascript:true$')
        ]
        for i, form in enumerate(forms):
            action = str(form.get('action', None))
            if (empty[0].match(action) or empty[1].match(action)
                    or empty[2].match(action)):
                num += 1
                total += 1
            elif self.domain in action or re.compile(r'^/').match(action):
                total += 1
            else:
                total += 1
        if total == 0:
            percent = 0
        else:
            percent = (num / total) * 100
            # if percent > 100:
            #     print('SFH: Percent Greater than 100 ->', percent)
        return percent

    def email(self):
        # print('************** Submitting Info to Email **************', '\n')
        if self.ipv4.search(str(self.link)):
            # print('IP in url:', self.link)
            return 0
        if self.soup is None:
            return 0
        elif self.soup == -1:
            return -1
        anchors = self.soup.find('a')
        if anchors is None:
            return 0
        href = anchors.get('href', 'None')
        pattern = re.compile(r'mail\s\(\$.[^\)]*\)|mail\(\$.[^\)]*\)|mail\(\)')
        if 'mailto:' in href:
            # print('P')
            return -1
        elif pattern.findall(str(self.soup)):
            # print('P')
            return -1
        else:
            # print('G')
            return 1

    def abnormal_url(self):
        # print('****************** Abnormal URL ******************')
        if self.host is None:
            return 0
        elif self.host in self.link.lower():
            return 1
        else:
            # print('Abnormal:', self.host, self.link)
            return -1


# arg = sys.argv[1]
# Ab = Abnormal(arg)
# print(Ab.req_url(), '\n')
# print(Ab.url_anchor(), '\n')
# print(Ab.links_in_tags(), '\n')
# print(Ab.sfh(), '\n')
# print(Ab.email(), '\n')
# print(Ab.abnormal_url(), '\n')
