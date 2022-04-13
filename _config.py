# Default config file, only as template, not actually used. Remove "_" from name.

side_of_window = 'l'  # side of window to open extractor in, r for right, l for left
proxy_for_source = 'http://ch.proxymesh.com:31280/'  # default proxy to add to JSON
user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/88.0'
settings_json = {'LOG_LEVEL': 'DEBUG', 'COOKIES_ENABLED': False, 'USER_AGENT': user_agent}
db_path = 'log.db'
local_db_path = 'local_log.db'
default_login_header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0"
}
window_title = "XPath Extractor"
background = "light grey"
label_font = "Calibri"
button_font = "Open Sans"
chrome_path = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
