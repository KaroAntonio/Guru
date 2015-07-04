import sqlite3
import json
import re
from parse import evaluate_house

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

state_frequencies = {};
city_frequencies = {};
num_blacklisted = 0;

#Filter Properties
for p in properties:
    try:
        state_frequencies[p['state']] += 1;
    except:
        state_frequencies[p['state']] = 1;
    try:
        city_frequencies[p['city']] += 1;
    except:
        city_frequencies[p['city']] = 1;
        
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
            isBlack = re.search(b, desc)
            if (isBlack):
                #valid = False
                num_blacklisted += 1;
                p['price'] = max(float(p['price']) * 1.7, float(p['price']) + 40000);
                p['notes'] = "Blacklisted"
                evaluate_house(p);
                break;
                
        if valid:
            filtered_properties.append(p);
print("Properties Blacklisted: " + str(num_blacklisted));

'''
print("STATE FREQUENCIES");
for f in state_frequencies:
    if (f != None):
        print(str(f) + " " + str(float(state_frequencies[str(f)])/len(properties)));

print("CITY FREQUENCIES");
for f in sorted(city_frequencies, key=city_frequencies.__getitem__, reverse=True):
    if (f != None):
        print(str(f) + " " + str(float(city_frequencies[str(f)])/len(properties)));
'''

#Sort Properties
#according to rent to price ratio
print("Sorting...")
sorted_properties = sorted(filtered_properties, key=lambda p: (float(p['rental_valuation'])), reverse=True)

first = sorted_properties[:2000]
#first = sorted_properties[:20]

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