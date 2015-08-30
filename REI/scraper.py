import re
from urlparse import urljoin

from bs4 import BeautifulSoup
from httplib import OK
import requests

#CONSTANTS
DESCRIPTION = "notranslate"
FACT_GROUPING = "disc-bullet"
HOME_TYPES = (
    "Apartment",
    "Condo",
    "Miscellaneous",
    "Multi Family",
    "Multiple Occupancy",
    "Single Family",
    "Townhouse"
)
HOME_VALUE = "home-value-wrapper"
INDIVIDUAL_FACT = "fact-bullet"
PROP_SUMMARY_CLASS = "zsg-content-header addr"
ZILLOW_HOMES_URL = "http://zillow.com/homes/"
ZILLOW_URL = "http://zillow.com"

def get_raw_html(url, timeout):
    #timeout in s
    response = requests.get(url, timeout=timeout)
    if response.status_code != OK:
        raise Exception("You received a {} error. Your content {}".format(
            response.status_code, response.content
        ))
    elif response.url == ZILLOW_HOMES_URL:
        raise Exception(
            "You were redirected to {} perhaps this is because your original url {} was "
            "unable to be found".format(ZILLOW_HOMES_URL, url)
        )
    else:
        return response.content

def get_table_body(ajax_url, request_timeout):
    html = get_raw_html(ajax_url, request_timeout)
    pattern = r' { "html": "(.*)" }'
    html = re.search(pattern, html).group(1)
    html = re.sub(r'\\"', r'"', html)  # Correct escaped quotes
    html = re.sub(r'\\/', r'/', html)  # Correct escaped forward slashes
    soup = BeautifulSoup(html)
    table = soup.find('table')
    table_body = table.find('tbody')
    return table_body

def get_price_history(ajax_url, request_timeout):
    table_body = get_table_body(ajax_url, request_timeout)
    data = []

    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele for ele in cols]
        date = cols[0].get_text()
        event = cols[1].get_text()
        price = cols[2].find('span').get_text()

        data.append([date, event, price])
    return data

def check_for_null_result(result):
    if not result:
        raise Exception(
            "We were unable to parse crucial facts for this home. This "
            "is probably because the HTML changed and we must update the "
            "scraper. File a bug at https://github.com/hahnicity/scrapezillow/issues"
        )

def get_ajax_url(soup, label):
    pattern = r"(\/AjaxRender.htm\?encparams=[\w\-_~=]+&rwebid=\d+&rhost=\d)\",jsModule:\"{}".format(label)
    url = re.search(pattern, soup.text)
    check_for_null_result(url)
    ajax_url = "http://www.zillow.com" + url.group(1)
    return ajax_url

def parse_taxes_response(self, response):
        
    house = response.meta['item']
    
    house['tax_url'] = '';
    tax_history = []
    pattern = r' { "html": "(.*)" }'
    html = re.search(pattern, response.body).group(1)
    html = re.sub(r'\\"', r'"', html)  # Correct escaped quotes
    html = re.sub(r'\\/', r'/', html)  # Correct escaped forward
    if (html != ""):
        soup = BeautifulSoup(html)
        table = soup.find('table')
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            try:
                cols = row.find_all('td')
                cols = [ele for ele in cols]
                date = cols[0].get_text()
                tax = cols[1].contents[0]
                assessment = cols[3].get_text()
                tax_history.append([date, tax, assessment])
            except:
                tax_history.append([Error])
        house['tax_history'] = json.dumps(tax_history)
        
    return house