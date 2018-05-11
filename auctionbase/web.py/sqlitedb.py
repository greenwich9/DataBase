import web
db = web.database(dbn='sqlite',
        db='auctions.db' #TODO: add your SQLite database filename
    )

######################BEGIN HELPER METHODS######################

# Enforce foreign key constraints
# WARNING: DO NOT REMOVE THIS!
def enforceForeignKey():
    db.query('PRAGMA foreign_keys = ON')

# initiates a transaction on the database
def transaction():
    return db.transaction()
# Sample usage (in auctionbase.py):
#
# t = sqlitedb.transaction()
# try:
#     sqlitedb.query('[FIRST QUERY STATEMENT]')
#     sqlitedb.query('[SECOND QUERY STATEMENT]')
# except Exception as e:
#     t.rollback()
#     print str(e)
# else:
#     t.commit()
#
# check out http://webpy.org/cookbook/transactions for examples

# returns the current time from your database
def getTime():
    # TODO: update the query string to match
    # the correct column and table name in your database
    query_string = 'select Time from CurrentTime'
    results = query(query_string)
    # alternatively: return results[0]['currenttime']
    return results[0].Time # TODO: update this as well to match the
                                  # column name

# returns a single item specified by the Item's ID in the database
# Note: if the `result' list is empty (i.e. there are no items for a
# a given ID), this will throw an Exception!
def getItemById(item_id):
    # TODO: rewrite this method to catch the Exception in case `result' is empty
    query_string = 'select * from Items where ItemID = $item_id'
    result = query(query_string, {'item_id': item_id})
    try:
        return result[0]
    except Exception as e:
        return None

def getUserById(user_id):
    query_string = 'select * from Users where UserID = $user_id'
    result = query(query_string, {'user_id': user_id})
    try:
        return result[0]
    except Exception as e:
        return None

# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
def query(query_string, vars = {}):
    return list(db.query(query_string, vars))

#####################END HELPER METHODS#####################

#TODO: additional methods to interact with your database,
# e.g. to update the current time

def updateCurrrentTime(current_time):
    query_string = 'update CurrentTime set Time = $current_time'
    t = transaction()
    res = None
    try:
        db.query(query_string, {'current_time': current_time})
    except Exception as e:
        t.rollback()
        res = str(e)
    else:
        t.commit()
    return res


def getItems(item_id = None, category = None, description = None, min_price = None, max_price = None, status = None, current_time = None):
    query_string = 'select * from Items'
    word = ' where '
    if item_id:
        query_string += word + 'ItemID = $item_id'
        word = ' and '
    if category:
        query_string += word + 'ItemID in (select ItemID from Categories where Category = $category)'
        word = ' and '
    if description:
        query_string += word + 'Description like $description'
        word = ' and '
    if min_price:
        query_string += word + 'Currently >= $min_price'
        word = ' and '
    if max_price:
        query_string += word + 'Currently <= $max_price'
        word = ' and '

    if status:
        if status == 'open':
            query_string += word + 'Ends >= $current_time and Started <= $current_time and (Buy_Price is NULL or Number_of_Bids = 0 or Currently < Buy_Price)'
        elif status == 'close':
            query_string += word + '((Ends < $current_time) or (Ends >= $current_time and Started <= $current_time and Buy_Price is not NULL and Number_of_Bids > 0 and Currently >= Buy_Price))'
        elif status == 'notStarted':
            query_string += word + 'Started > $current_time'
        elif status == 'all':
            if word == ' where ':
                query_string += ' limit 20'
    
    return query(query_string, {'item_id': item_id, 'category': category, 'description': description, 'min_price': min_price, 'max_price': max_price, 'status': status, 'current_time': current_time})


def getCategories(item_id):
    query_string = 'select Category from Categories where ItemID = $item_id'
    return query(query_string, {'item_id': item_id})


def getBids(item_id):
    query_string = 'select UserID, Time, Amount from Bids where ItemID = $item_id'
    return query(query_string, {'item_id': item_id})


def getWinner(item_id):
    query_string = 'select UserID from Bids where ItemID = $item_id and Amount = (select max(Amount) from Bids where ItemID = $item_id)'
    result = query(query_string, {'item_id': item_id})
    try:
        return result[0]
    except Exception as e:
        return None

def updateBid(user_id, item_id, price, current_time):
    res = None
    t = transaction()
    try:
        db.insert("Bids", ItemID = item_id, UserID = user_id, Amount = price, Time = current_time)
    except Exception as e:
        t.rollback()
        res = str(e).decode('utf-8')
    else:
        t.commit()
    return res
