#Build List of Cities from Property list
#Call scrapy
import subprocess
import sqlite3
import json
import re

def gen_city_urls():
    state_map = {
        "OR":"Oregon",
        "TX":"Texas",
        "AZ":"Arizona",
        "CA":"California",
        "IL":"Illinois",
        "OK":"Oklahoma",
        "NJ":"New-Jersey",
        "AR":"Arkansas",
        "AL":"Alabama",
        "WA":"Washington",
        "CO":"Colorado",
        "FL":"Florida",
        "MS":"Mississippi",
        "NM":"New-Mexico",
        "ID":"Idaho",
        "TN":"Tennessee",
        "PR":"Puerto-Rico",
        "LA":"Louisiana",
        "MO":"Missouri",
        "NV":"Nevada",
        "SC":"South-Carolina",
        "MN":"Minnesota",
        "AS":"American-Samoa",
        "NC":"North-Carolina",
        "AK":"Alaska",
        
    }
    print("Loading database...")
    #Setup connection to database
    conn = sqlite3.connect('properties.db')
    conn.row_factory = sqlite3.Row
    #establish connection cursor
    c = conn.cursor()
    #execute SQL statement via the cursor
    c.execute('SELECT * FROM HouseItem')
    #store all properties from database in array
    rows = c.fetchall()

    #http://stackoverflow.com/questions/3286525/return-sql-table-as-json-in-python
    properties = [dict(ix) for ix in rows]

    print("Analyzing cities...")
    cities = []
    for p in properties:
        if (p['state'] != None):
            if p['state'] in state_map.keys():
                city = p['city'].replace(" ","-") + "-" + state_map[p['state']]
                if city in cities:
                    pass
                else:
                    cities.append(city)
            else:
                print ("No State Code Mapping: "+p['state'])

    urls = []
    for c in cities:
        urls.append("http://www.city-data.com/city/"+c+".html")
        
    print("Num Cities Processed: " + str(len(cities)))

    return urls

#Call Scrapy
#gen_city_urls()
subprocess.call('rm cities.json', shell=True);
subprocess.call('scrapy crawl city -o cities.json', shell=True);
