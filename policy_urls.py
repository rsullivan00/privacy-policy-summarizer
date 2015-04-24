#
# Gathers all Privacy Policy urls that are displayed from the top 100
# free apps on the Google Play store. Uses the 42 matters (paid) API,
# which offers free trials.
#
# Requests to the Play store are separated by 1 second to avoid any
# issues with Google.
#

import requests
import sys
import time
from bs4 import BeautifulSoup


def add_link(policy_urls, l):
    """
    Processes a raw link, then adds cleaned link to
    the policy_urls list.
    """
    if l.get_text().strip() == "Privacy Policy":
        l_href = l.get('href')
        google_pp = 'http://www.google.com/intl/en-US_us/policies/privacy/'
        if l_href != google_pp:
            # Remove redirect
            l_href = l_href.replace('https://www.google.com/url?q=', '')
            i = l_href.find('&sa')
            l_href = l_href[:i]
            policy_urls.append(l_href)
            print('\t' + l_href)

    return policy_urls


def process_market_urls(urls, delay=1):
    """
    Find Privacy Policy URL from each of the Google Play
    app store URLs.

    delay param pauses between requests to Google to prevent
    any problems with terms of service.
    """
    policy_urls = []
    for url in urls:
        print('\n---------\nURL: %s\n---------\n' % url)
        html_page = requests.get(url).text
        soup = BeautifulSoup(html_page)
        links = soup.find_all('a')
        for l in links:
            add_link(policy_urls, l)

        time.sleep(delay)
        print('\n')

    return policy_urls


#
# Beginning of script that runs automatically.
#
api_url = """
    https://42matters.com/api/1/apps/top_google_charts.json?\
    list_name=topselling_free&cat_key=APPS&country=US&limit=100&access_token=
    """

# 42 matters API token must be stored in a '.token' file.
try:
    token = open('.token').read().rstrip()
    api_url += token
except:
    print("Could not find API token file.")
    sys.exit(1)

req = requests.get(api_url)
content = req.json()
apps = content['appList']
market_urls = []

for a in apps:
    market_urls.append(a['market_url'])

policy_urls = process_market_urls(market_urls)
fout = open('policy_urls.txt', 'w')
for url in policy_urls:
    fout.write(url + '\n')
