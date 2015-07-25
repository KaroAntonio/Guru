import sqlite3
import json
import re
from parse import evaluate_house

def get_YTY(house):
    #Determine the average year to year change in house price for this property
    #Calculate using the 
    prices = []
    
    YRi = 1000.0
    Pi = 0.0
    YRf = -1.0
    Pf = 0.0
    
    for sale in json.loads(house['price_history']):
        p = sale[2].replace(r',', "").replace(r'$', "")
        p = re.search(r'(\d+)',p)
        yr = re.findall(r'(\d+)',sale[0])
        status = sale[1]
        
        if (p!=None):
            p = p.group(1)
        if (yr!=None):
            yr = yr[2]
        
        try:
            p = int(p)
            yr = int(yr)
            if (status == "Sold"):
                if (yr < YRi):
                    YRi = float(yr)
                    Pi = float(p)
                if (yr > YRf):
                    YRf = float(yr)
                    Pf = float(p)

        except:
            p = 0
            yr = 0
            pass
        
        if (p != 0):
            prices.append(p)
    
    if (YRf == -1):
        #print("ERROR: No Price History")
        return -1
    else:
        if (YRf != YRi):
            
            #yty = (float(Pf)/ float(Pi)) / (float(YRf) - float(YRi))
            yty = ((Pf - Pi) / Pi) / (YRf - YRi)
            
            #print(YRf, Pf, YRi, Pi, yty)
        else:
            yty = 0
        return yty
    
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

#properties = properties[:2000]

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
    r'fix up',
    r'handyman',
    r'handy man',
    r'flip project',
    r'flip',
    r'needs.{,20}work',
    r'tlc',
    r'great.{,20}potential'
]

HOA_flags = [
    r'hoa',
    r'condo fees'
]

state_frequencies = {};
city_frequencies = {};
num_blacklisted = 0;

#Analyze Properties
yty_sum = 0
iyty = 0

for p in properties:
    try:
        state_frequencies[p['state']] += 1;
    except:
        state_frequencies[p['state']] = 1;
    try:
        city_frequencies[p['city']] += 1;
    except:
        city_frequencies[p['city']] = 1;
        
    yty = get_YTY(p)
    
    if (yty != -1):
        if (yty != 0):
            if (yty > 1):
                #print(yty, p["price_history"])
                pass
            yty_sum += yty
            iyty += 1
if (iyty != 0):
    avg_yty = yty_sum / iyty
else:
    avg_yty = 0
print (avg_yty, iyty)

#Filter Properties
for p in properties:
    #evaluate_house(p)
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
                
        for f in HOA_flags:
            isFlagged = re.search(f, desc)
            if (isFlagged):
                #valid = False
                num_blacklisted += 1;
                p['HOA'] = 200;
                if p['notes'] != None:
                    p['notes'] += "Has HOA"
                else:
                    p['notes'] = "Has HOA"
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

size_first = 1000
first = sorted_properties[:size_first]
#first = sorted_properties[:20]

#Analyze state + city frequencies for the first properties
f_city_frequencies = {}
f_state_frequencies = {}
for p in first:
    try:
        f_state_frequencies[p['state']] += 1;
    except:
        f_state_frequencies[p['state']] = 1;
    try:
        f_city_frequencies[p['city']] += 1;
    except:
        f_city_frequencies[p['city']] = 1;
    
#Process City Frequencies
#Ratio of the number of cities in the top slice of the database, to the whole database
city_ratios = {}
num_cities = 100
i = 0
for f in f_city_frequencies:
    if (i < num_cities):
        city_ratios[f] = (float(f_city_frequencies[f])/size_first)/(float(city_frequencies[f])/len(properties));
    i += 1;
    #print (f, f_city_frequencies[f],city_frequencies[f], city_ratios[f])
for f in sorted(f_city_frequencies, key=f_city_frequencies.__getitem__, reverse=True):
    print (f,  f_city_frequencies[f])

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