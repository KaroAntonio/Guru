#script to geocode all properties in properties json
#using google api

from geopy.geocoders import Nominatim
from geopy.geocoders import GoogleV3
import json
from pygeocoder import Geocoder
import contextlib
import sys, os

#hide warnings
@contextlib.contextmanager
def stdchannel_redirected(stdchannel, dest_filename):
    """
    A context manager to temporarily redirect stdout or stderr
    """

    try:
        oldstdchannel = os.dup(stdchannel.fileno())
        dest_file = open(dest_filename, 'w')
        os.dup2(dest_file.fileno(), stdchannel.fileno())

        yield
    finally:
        if oldstdchannel is not None:
            os.dup2(oldstdchannel, stdchannel.fileno())
        if dest_file is not None:
            dest_file.close()
            
def geocode():
    '''
    geocoder = GoogleV3(
        client_id='416144311414-9sa4usu4f9dsuvn8urbhprq3stdisq3k.apps.googleusercontent.com', 
        secret_key='0LGqN8vGa_xfEd4us9Y_VXKC',
        api_key='AIzaSyAc0R7DULyiZPWAcBTrCyFJM38WCepWrEU')
        '''
    #geocoder = GoogleV3(api_key='AIzaSyBBnPI_YDy1V51NfXAvHsVKWhq0Po31L24')	
    geocoder = Geocoder();
        
    #load geocode cache
    try:
        with open('process/geocache.json') as data_file:    
            cache = json.load(data_file)
    except:
        cache = {}

    #load properties
    with open('app/properties.json') as data_file:    
        properties = json.load(data_file)

    #geocode property addresses
    with stdchannel_redirected(sys.stderr, os.devnull):
        i = 0
        for p in properties:
            i += 1
            if p["id"] in cache:
                p["latlong"] = cache[p["id"]]
            else:
                try:
                    address = p["address"] + " " + p["city"] + " " + p["state"]
                    l = geocoder.geocode(address)
                    latlong = [ l.latitude, l.longitude]
                    p["latlong"] = latlong
                    cache[p["id"]] = latlong
                except: 
                    print('\nERROR: GeoCoding Failure, API Limit most likely reached')
                    break
                
                    

            #print percent progress
            sys.stdout.write("\r%d%%" % (float(i)/len(properties) *100.0))
            sys.stdout.flush()

    print ("\nGeoCoding Complete")

    #dump properties
    with open('app/properties.json', 'w') as outfile:
        json.dump(properties, outfile)

    #dump cache
    with open('process/geocache.json', 'w') as outfile:
        json.dump(cache, outfile)