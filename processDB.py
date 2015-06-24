import sqlite3
import json
import re

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

#properties = properties[:10]

#Filter Properties with invalid fields
print("Filtering...")
filtered_properties = []
conditions = [
    ['rent_zestimate', '-1'],
    ['sale_status', 'Auction'],
]

ranges = [
    ['price', 27000, 100000000],
]

blacklist = [
    r'fixer upper',
    r'handyman',
    r'handy man',
    r'flip project',
    r'flip',
    r'needs.{,20}work',
    r'tlc',
    r'great.{,20}potential',
]

for p in properties:
    valid = True
    try:
        float(p['price'])
        float(p['rent_zestimate'])       
    except:
        valid = False
        
    if valid:
        for c in conditions:
            if (p[c[0]] == c[1]):
                valid = False

        for r in ranges:
            if (int(p[r[0]]) > r[2] or int(p[r[0]]) < r[1]):
                valid = False

        #Properties with prices far higher or lower than the zestimate are no good
        dmax = 2
        dmin = 1/2
        ratio = float(p['zestimate'])/float(p['price'])
        if (ratio < dmin or ratio > dmax):
            valid = False
            
        #Filter Out blacklisted regexes
        desc = p['description'].lower()
        
        for b in blacklist:
            test = re.search(b, desc)
            if (test):
                valid = False
                break;
                
        if valid:
            filtered_properties.append(p)

#Sort Properties
#according to rent to price ratio
print("Sorting...")
sorted_properties = sorted(filtered_properties, key=lambda p: (float(p['rental_valuation'])), reverse=True)

first = sorted_properties[:2000]
'''
#Print Final Array
for p in first:
    ratio = float(p['zestimate'])/float(p['price'])
    if (ratio > 3):
        print(float(p['zestimate'])/float(p['price']))
    if (ratio < (1/3)):
        print(float(p['zestimate'])/float(p['price']))
'''

with open('properties.json', 'w') as outfile:
    json.dump(first, outfile)

print("Processed " + str(len(properties)) + " Properties\n" + "Exported " + str(len(first)) + " Properties")