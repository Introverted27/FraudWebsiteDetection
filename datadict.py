# import dask

# Local Modules
from attributes.addressbar import AddressBar
from attributes.abnormal import Abnormal

# # Addressbar Methods
# from attributes.addressbar import ip_in_url, length, tiny_url
# from attributes.addressbar import at_symbol redirects, dash_symbol
# from attributes.addressbar  import subdomain, verify_ssl, domain_time
# from attributes.addressbar  import favicon, https, ports
#
# # Attribute Methods
# from attributes.abnormal import req_url, url_anchor, links_in_tags
# from attributes.abnormal import sfh, email, abnormal_url


def data_dict(link, **kwargs):
    port = kwargs.get('port', False)
    AddressBarObj = AddressBar(link)
    AbnormalObj = Abnormal(link)
    tags = AbnormalObj.req_url()
    tag_links = AbnormalObj.links_in_tags()

    data = {
        'Having_IP_Address': AddressBarObj.ip_in_url(),
        'URL_Length': AddressBarObj.length(),
        'Shortening_Service': AddressBarObj.tiny_url(),
        'Having_At_Symbol': AddressBarObj.at_symbol(),
        'Double_Slash_Redirecting': AddressBarObj.redirects(),
        'Prefix_Suffix': AddressBarObj.dash_symbol(),
        'Having_Sub_Domain': AddressBarObj.subdomain(),
        'SSLfinal_State': AddressBarObj.verify_ssl(),
        'Domain_registeration_length': AddressBarObj.domain_time(),
        'Favicon': AddressBarObj.favicon(),
        'HTTPS_Token': AddressBarObj.https(),
        'PctImageTags': tags['img'],
        'PctAudioTags': tags['audio'],
        'PctVideoTags': tags['video'],
        'PctTrackTags': tags['embed'],
        'PctSourceTags': tags['source'],
        'PctIframeTags': tags['iframe'],
        'URL_of_Anchor': AbnormalObj.url_anchor(),
        'PctMetaTags': tag_links['meta'],
        'PctScriptTags': tag_links['script'],
        'PctLinkTags': tag_links['link'],
        'SFH': AbnormalObj.sfh(),
        'Submit_to_Email': AbnormalObj.email(),
        'Abnormal Url': AbnormalObj.abnormal_url()
    }
    if port:
        data['Port'] = AddressBarObj.ports()
    else:
        data['Port'] = 0
        # print('Port = ', data['Port'])
    return data
