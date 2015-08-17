import subprocess
import pico
import re
import math
from subprocess import Popen

def run(url):
    subprocess.call('rm houses.json', shell=True);
    subprocess.call('scrapy crawl zillow -a url='+url+' -a prll=False -o houses.json', shell=True);
    return url

def run_parallel(url):
    subprocess.call('rm houses.json', shell=True);
    urls = gen_urls(url);
    
    processes = [
        Popen('scrapy crawl zillow -a url='+u+' -a prll=True -o houses.json',
              shell=True) 
        for u in urls]
    '''
    for u in urls:
        subprocess.call('scrapy crawl zillow -a url='+u+' -a prll=True -o houses.json', shell=True);
        '''
    
    for p in processes: p.wait()
    
    return

def process_DB(db_name):
    
    
    return

def div_url(url, base):
    #split the url into quarters with smaller scopes
    
    urls = []
    latlong = re.findall(r'(-?[1-9][0-9]*\.[0-9]+)',url)
    urla = re.search(r'^(.*?)\-?[1-9][0-9]*\.[0-9]+',url).group(1)
    urlb = re.search(r'(_rect/[0-9]*_zm.*)',url).group(1)
    
    #Lattitudes are indicated top to bottom
    lat1 = float(latlong[0])
    lat2 = float(latlong[2])
    dlat = lat1 - lat2
    #Longitudes are indicated right to left
    long1 = float(latlong[1])
    long2 = float(latlong[3])
    dlong =  long1 - long2
    
    maxdlat = dlat / base;
    maxdlong = dlong / base;
    
    nlat = base
    nlong = base
    
    for i in range (0, nlat):
        newlat1 = lat1 - (maxdlat * i)
        if (i == (nlat - 1)):
            newlat2 = lat2
        else:
            newlat2 = lat1 - (maxdlat * (i + 1))
            
        for j in range (0, nlong):
            newlong1 = long1 - (maxdlong * j)
            if (j == (nlong - 1)):
                newlong2 = long2
            else:
                newlong2 = long1 - (maxdlong * (j + 1))
                
            newurl = urla + str(newlat1) + "," + str(newlong1) + "," +  str(newlat2) + "," + str(newlong2) + urlb
            
            urls.append(newurl)
            
            #print(i, j, newlat1, newlat2, newlong1, newlong2)
            #print (i, j, newurl)
            
    print("Number of URLS: " + str(len(urls)))
    
    return urls
        
def gen_urls(url):
    #if the url will return potentially too many homes,
    #split the url into urls with smaller scopes
    
    #maximum scope
    #maxdlat = 0.005
    #maxdlong = 0.005
    maxdlat = 0.015
    maxdlong = 0.015
    
    urls = []
    latlong = re.findall(r'(-?[1-9][0-9]*\.[0-9]+)',url)
    urla = re.search(r'^(.*?)\-?[1-9][0-9]*\.[0-9]+',url).group(1)
    urlb = re.search(r'(_rect/[0-9]*_zm.*)',url).group(1)
    
    #Lattitudes are indicated top to bottom
    lat1 = float(latlong[0])
    lat2 = float(latlong[2])
    dlat = lat1 - lat2
    #Longitudes are indicated right to left
    long1 = float(latlong[1])
    long2 = float(latlong[3])
    dlong =  long1 - long2
    
    nlat = int(math.ceil(dlat/maxdlat))
    nlong = int(math.ceil(dlong/maxdlong))
    
    for i in range (0, nlat):
        newlat1 = lat1 - (maxdlat * i)
        if (i == (nlat - 1)):
            newlat2 = lat2
        else:
            newlat2 = lat1 - (maxdlat * (i + 1))
            
        for j in range (0, nlong):
            newlong1 = long1 - (maxdlong * j)
            if (j == (nlong - 1)):
                newlong2 = long2
            else:
                newlong2 = long1 - (maxdlong * (j + 1))
                
            newurl = urla + str(newlat1) + "," + str(newlong1) + "," +  str(newlat2) + "," + str(newlong2) + urlb
            
            urls.append(newurl)
    
    return urls

