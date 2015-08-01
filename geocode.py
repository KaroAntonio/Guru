#script to geocode all properties in properties json
#using google api

from geopy.geocoders import Nominatim
import json
from pygeocoder import Geocoder
import contextlib
import sys, os

#hide warnings
@contextlib.contextmanager
def stdchannel_redirected(stdchannel, dest_filename):
    """
    A context manager to temporarily redirect stdout or stderr

    e.g.:


    with stdchannel_redirected(sys.stderr, os.devnull):
        if compiler.has_function('clock_gettime', libraries=['rt']):
            libraries.append('rt')
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
            
geocoder = Geocoder(client_id=None, private_key='AIzaSyBi0b_h-aqwf1zL4qZE3P2ZgxAN4c50X9o')

#load properties
with open('properties.json') as data_file:    
    properties = json.load(data_file)

#geocode property addresses
with stdchannel_redirected(sys.stderr, os.devnull):
    i = 0
    for p in properties:
        i += 1
        address = p["address"] + " " + p["city"] + " " + p["state"]
        l = geocoder.geocode(address)
        latlong = [ l.latitude, l.longitude]
        p["latlong"] = latlong
        
        #print percent progress
        sys.stdout.write("\r%d%%" % (float(i)/len(properties) *100.0))
        sys.stdout.flush()
        
print ("\nGeoCoding Complete")

#dump properties
with open('properties.json', 'w') as outfile:
    json.dump(properties, outfile)