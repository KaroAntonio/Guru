import sqlite3
import json

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
for p in properties:
    try:
        float(p['price'])
        float(p['rent_zestimate'])
        if (p['rent_zestimate'] != '-1'):
            if (p['sale_status'] != 'Auction'):
                filtered_properties.append(p)
    except:
        pass

#Sort Properties
#according to rent to price ratio
print("Sorting...")
sorted_properties = sorted(filtered_properties, key=lambda p: (float(p['price']) / float(p['rent_zestimate'])))

first = sorted_properties[:2000]

'''
#Print Final Array
for p in sorted_properties:
    print(p['rent_zestimate'] + "\t" + p['price'] + "\t" + str(float(p['rent_zestimate']) / float(p['price'])))
'''

with open('properties.json', 'w') as outfile:
    json.dump(first, outfile)

print("Processed " + str(len(properties)) + " Properties")