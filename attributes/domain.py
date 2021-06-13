from tld import get_tld

from attributes.ip import contains_ipv4, contains_ipv6


def get_domain_name(link, **kwargs):
    tld = kwargs.get('tld', True)
    subdomain = kwargs.get('subdomain', True)
    if contains_ipv4(link) or contains_ipv6(link):
        if link[-1] == '/':
            link = link[:-1]
        return link.replace('https://', '').replace('http://', '')
    if 'http://' in link or 'https://' in link:
        obj = get_tld(link, as_object=True)
    else:
        link = 'http://' + link + '/'
        obj = get_tld(link, as_object=True)

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
