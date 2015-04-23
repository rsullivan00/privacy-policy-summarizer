import requests
import sys
sys.exit

url = "https://42matters.com/api/1/apps/top_google_charts.json?list_name=topselling_free&cat_key=APPS&country=US&limit=10&access_token="
try:
    token = open('.token').read()
    url += token
except:
    print("Could not find API token file.")
    sys.exit(1)

req = requests.get(url)
print(r.status_code)
print(r.content)
