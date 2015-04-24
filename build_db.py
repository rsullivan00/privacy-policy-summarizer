#
# Gathers all Privacy Policy urls that are displayed from the top 100
# free apps on the Google Play store. Uses the 42 matters (paid) API,
# which offers free trials.
#
# Requests to the Play store are separated by 1 second to avoid any
# issues with Google.
#

import os
from urllib import parse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from pyvirtualdisplay import Display
from termcolor import colored

fin = open('policy_urls.txt')
urls = fin.read().strip().split('\n')

# Slower with headless browser than direct requests,
# but allows for rendering of dynamic content.
display = Display(visible=0, size=(800, 600))
display.start()
browser = webdriver.Firefox()
browser.set_page_load_timeout(5)


# Gets text from html using approach
for url in urls:
    host = parse.urlparse(url).hostname
    host = host.replace('www.', '')
    policy_dir = 'policies'
    print("Processing %s" % host)

    policy_path = os.path.join(policy_dir, host)
    if os.path.exists(policy_path):
        # Wooo colored printing
        print(colored("Policy already exists", 'yellow'))
        continue

    try:
        browser.get(url)
    except TimeoutException:
        print("Timeout")
        continue

    clear_elements = ['header', 'footer']
    for ce in clear_elements:
        try:
            browser.find_element_by_tag_name(ce).clear()
        except:
            continue

    html_page = browser.find_element_by_tag_name('body')

    text = html_page.text

    #fout = open(policy_path, 'w')
    #fout.write(text)
