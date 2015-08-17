import subprocess
from REI.parse import evaluate_house
from process.processDB import process as pdb
from process.geocode import geocode as geo

#Scrape Cities 
rm = subprocess.call('rm process/cities.json', shell=True)
crawl = subprocess.call('scrapy crawl city -o process/cities.json', shell=True)

#Process DB
pdb()

#Geocode Properties
geo()