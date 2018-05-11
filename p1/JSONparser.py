
"""
FILE: JSONparser.py
------------------
Author: Firas Abuzaid (fabuzaid@stanford.edu)
Author: Perth Charernwattanagul (puch@stanford.edu)
Modified: 04/21/2014

Skeleton parser for CS564 programming project 1. Has useful imports and
functions for parsing, including:

1) Directory handling -- the parser takes a list of eBay json files
and opens each file inside of a loop. You just need to fill in the rest.
2) Dollar value conversions -- the json files store dollar value amounts in
a string like $3,453.23 -- we provide a function to convert it to a string
like XXXXX.xx.
3) Date/time conversions -- the json files store dates/ times in the form
Mon-DD-YY HH:MM:SS -- we wrote a function (transformDttm) that converts to the
for YYYY-MM-DD HH:MM:SS, which will sort chronologically in SQL.

Your job is to implement the parseJson function, which is invoked on each file by
the main function. We create the initial Python dictionary object of items for
you; the rest is up to you!
Happy parsing!
"""

import sys
from json import loads
from re import sub

columnSeparator = "|"

# Dictionary of months used for date transformation
MONTHS = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',\
        'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

"""
Returns true if a file ends in .json
"""
def isJson(f):
    return len(f) > 5 and f[-5:] == '.json'

"""
Converts month to a number, e.g. 'Dec' to '12'
"""
def transformMonth(mon):
    if mon in MONTHS:
        return MONTHS[mon]
    else:
        return mon

"""
Transforms a timestamp from Mon-DD-YY HH:MM:SS to YYYY-MM-DD HH:MM:SS
"""
def transformDttm(dttm):
    dttm = dttm.strip().split(' ')
    dt = dttm[0].split('-')
    date = '20' + dt[2] + '-'
    date += transformMonth(dt[0]) + '-' + dt[1]
    return date + ' ' + dttm[1]

"""
Transform a dollar value amount from a string like $3,453.23 to XXXXX.xx
"""

def transformDollar(money):
    if money == None or len(money) == 0:
        return money
    return sub(r'[^\d.]', '', money)

"""
Parses a single json file. Currently, there's a loop that iterates over each
item in the data set. Your job is to extend this functionality to create all
of the necessary SQL tables for your database.
"""
def parseJson(json_file):
    # print("here\n")
    with open('Items.dat', 'a') as Items:
        with open('Categories.dat','a') as Category:
            with open('Users.dat','a') as User:
                with open('Bids.dat','a') as Bid:
                    with open(json_file, 'r') as f:
                        items = loads(f.read())['Items'] # creates a Python dictionary of Items for the supplied json file
                        for item in items:
                            """
                            TODO: traverse the items dictionary to extract information from the
                            given `json_file' and generate the necessary .dat files to generate
                            the SQL tables based on your relation design
                            """
                            Started = transformDttm(item['Started']);
                            Ends = transformDttm(item['Ends'])
                            Currently = transformDollar(item['Currently'])
                            First_Bid = transformDollar(item['First_Bid'])
                            item_Name = '"'+item['Name'].replace('"','""')+'"'
                            seller_id = '"'+item['Seller']['UserID'].replace('"','""')+'"'
                            Items.write(item['ItemID']+columnSeparator+item_Name+columnSeparator+Currently+columnSeparator+First_Bid+columnSeparator+item['Number_of_Bids']+columnSeparator+Started+columnSeparator+Ends+columnSeparator+seller_id+columnSeparator)
                            if 'Buy_Price' not in item:
                                Items.write('NULL'+'|')
                            else:
                                Buy_Price = transformDollar(item['Buy_Price'])
                                Items.write(Buy_Price+'|')
                            if item['Description'] is None:
                                Items.write('NULL\n')
                                # print("None description")
                            else:
                                item_description = '"'+item['Description'].replace('"','""')+'"'
                                Items.write(item_description+'\n')
                            for curcate in item['Category']:
                                item_categories = '"'+curcate.replace('"','""')+'"'
                                Category.write(item['ItemID']+columnSeparator+item_categories+'\n')
                            
                            item_country = '"'+item['Country'].replace('"','""')+'"'
                            item_location = '"'+item['Location'].replace('"','""')+'"'
                            User.write(seller_id+columnSeparator+item_country+columnSeparator+item_location+columnSeparator+item['Seller']['Rating']+'\n')
                            if item['Bids'] is not None:
                                for singlebid in item['Bids']:
                                    bidder_id = '"'+singlebid['Bid']['Bidder']['UserID'].replace('"','""')+'"'
                                    User.write(bidder_id+columnSeparator)
                                    if 'Country' not in singlebid['Bid']['Bidder']:
                                        User.write('NULL'+columnSeparator)
                                    else:
                                        bidder_country = '"'+singlebid['Bid']['Bidder']['Country'].replace('"','""')+'"'
                                        User.write(bidder_country+columnSeparator)
                                    if 'Location' not in singlebid['Bid']['Bidder']:
                                        User.write('NULL'+columnSeparator)
                                    else:
                                        bidder_location = '"'+singlebid['Bid']['Bidder']['Location'].replace('"','""')+'"'
                                        User.write(bidder_location+columnSeparator)
                                    User.write(singlebid['Bid']['Bidder']['Rating']+'\n')
                            # Current design for those have no bids+don't record them in the Bid table
                            if item['Bids'] is not None:
                                for singlebid in item['Bids']:
                                    Time = transformDttm(singlebid['Bid']['Time'])
                                    Amount = transformDollar(singlebid['Bid']['Amount'])
                                    bidder_id = '"'+singlebid['Bid']['Bidder']['UserID'].replace('"','""')+'"'                                    
                                    Bid.write(bidder_id+columnSeparator+item['ItemID']+columnSeparator+Time+columnSeparator+Amount+'\n')
                            pass

"""
Loops through each json files provided on the command line and passes each file
to the parser
"""
def main(argv):
    if len(argv) < 2:
        print >> sys.stderr, 'Usage: python skeleton_json_parser.py <path to json files>'
        sys.exit(1)
        # loops over all .json files in the argument
    for f in argv[1:]:
        if isJson(f):
            parseJson(f)
            # print("enhere\n")
            print ("Success parsing " + f)

if __name__ == '__main__':
    main(sys.argv)
