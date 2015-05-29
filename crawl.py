import subprocess
import pico

def hello():
    return "Hello Karo"

def timetest():
    return ("Fri May 29 10:05:47 2015" < "Fri May 29 10:05:51")

def run():
    subprocess.call('rm houses.json', shell=True);
    subprocess.call('scrapy crawl zillow -o houses.json', shell=True);
    return "complete"
    

