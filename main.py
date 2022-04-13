import requests
from requests.auth import HTTPProxyAuth
from lxml import html, etree

proxy = {
    "http": "http://vpn.aiidatapro.com:3128",
    "https": "http://hristo.grudev:Welcome1441@195.47.193.16:3128",
}


session = requests.Session()

session.proxies = proxy
session.auth = HTTPProxyAuth("hristo.grudev", "Welcome1441")
login_link = "http://dashbeta.aiidatapro.net/"

headers = {'Connection': 'close',
           'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0"}
session_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml',
    'user-agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0"
}
session.get(login_link, headers=session_headers)
if 'csrftoken' in session.cookies:
    # Django 1.6 and up
    csrftoken = session.cookies['csrftoken']
else:
    csrftoken = session.cookies['csrf']
session_headers['cookie'] = '; '.join([x.name + '=' + x.value for x in session.cookies])
session_headers['content-type'] = 'application/x-www-form-urlencoded'
payload = {
    'username': 'hristogr',
    'password': 'he2Rop',
    'csrfmiddlewaretoken': csrftoken
}
response = session.post(login_link, data=payload, headers=session_headers)
session_headers['cookie'] = '; '.join([x.name + '=' + x.value for x in response.cookies])
print("Logged in!")

session_headers_post = {}

items_page_response = session.get('http://kraken.aiidatapro.net/items/edit/747658/')
tree = html.fromstring(items_page_response.text)
csrftoken = tree.xpath('(//input[@name="csrfmiddlewaretoken"]/@value)[1]')
print(session_headers['cookie'])
payload['csrfmiddlewaretoken'] = csrftoken[0]
payload['name'] = 'ubp.com/en'
payload['url'] = 'https://www.ubp.com/en'
payload['provider'] = '1'
payload['country'] = '21'
payload['scope'] = '2'
payload['languages'] = '602'
payload['subtype'] = '14'
payload['source_type'] = '9'
payload['focus'] = '6'
payload['supersector'] = '4'
payload['description'] = ''
payload['active'] = 'on'
payload['feed_properties'] = """{
  "scrapy_arguments": {
    "start_urls": "https://www.ubp.com/en;https://www.ubp.com/en/discover-ubp/press-area;https://www.ubp.com/en/newsroom;https://www.ubp.com/en/newsroom/insight;https://www.ubp.com/en/newsroom/ubp-in-the-press;https://www.ubp.com/en/newsroom/corporate",
    "articles_xpath": "//p/a[contains(@href,'/newsroom/')] | //div[@class='box box-content box-news blank nodeco box-minimal-xsmall']/a",
    "title_xpath": "//h1[contains(@class,'title')]",
    "pubdate_xpath": "//meta[@itemprop='datePublished']/@content",
    "date_order": "YMD",
    "author_xpath": "//div[@itemprop='author']/meta/@content",
    "body_xpath": "//div[@class='box box-quote box-auto nopadding blank nodeco notransi']| //div[@itemprop='articleBody']/node()",
    "link_id_regex": null
  },
  "scrapy_settings": {
    "LOG_LEVEL": "DEBUG",
    "COOKIES_ENABLED": false,
    "USER_AGENT": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/88.0"
  }
}"""
payload['botname'] = 'siteshtml'
payload['schedule'] = '01:05:00'
payload['enabled'] = 'on'
payload['dont-redirect'] = ''


session_headers['Connection'] = 'keep-alive'
session_headers['Content-Length'] = 'gzip'
session_headers['Content-Type'] = '16860'
session_headers['Content-Encoding'] = 'text/html; charset=utf-8'
session_headers['Host'] = 'kraken.aiidatapro.net'

print(session_headers)
print(payload)

response = session.post('http://kraken.aiidatapro.net/items/edit/747658/', data=payload, headers=session_headers)
print(response.url)
print(csrftoken[0])