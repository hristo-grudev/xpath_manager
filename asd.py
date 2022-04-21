import requests

link = 'http://bulnews.info/feed/'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0',
}

list_of_proxies = (
    'http://ch.proxymesh.com:31280/',
    'http://au.proxymesh.com:31280/',
    'http://sg.proxymesh.com:31280/',
    'http://open.proxymesh.com:31280/',
    'http://jp.proxymesh.com:31280/',
    'http://us-ny.proxymesh.com:31280/',
    'http://us-ca.proxymesh.com:31280',
    'http://us.proxymesh.com:31280/',
    'http://us-fl.proxymesh.com:31280/',
    'http://us-wa.proxymesh.com:31280/',
)


def proxy_dict(proxy):
    return {'http': proxy}


for proxi in list_of_proxies:
    response = requests.get(link, headers=headers, proxies=proxy_dict(proxi))
    print(proxi, response.status_code)
