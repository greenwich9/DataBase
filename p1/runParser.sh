#!/bin/bash
python JSONparser.py ebay_data/items-*.json
sort -u Bids.dat > newBid.dat
sort -u Items.dat > newItem.dat
sort -u Users.dat > newUser.dat
sort -u Categories.dat > newCategory.dat
cat newBid.dat > Bids.dat
cat newUser.dat > Users.dat
cat newItem.dat > Items.dat
cat newCategory.dat > Categories.dat
rm -rf new*.dat