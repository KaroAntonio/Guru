import subprocess
import pico

def hello():
    return "Hello Karo"

def run():
    subprocess.call('rm houses.json', shell=True);
    subprocess.call('scrapy crawl zillow -o houses.json', shell=True);
    return "complete"
    

