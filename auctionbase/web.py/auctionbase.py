#!/usr/bin/env python

import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

###########################################################################################
##########################DO NOT CHANGE ANYTHING ABOVE THIS LINE!##########################
###########################################################################################

######################BEGIN HELPER METHODS######################

# helper method to convert times from database (which will return a string)
# into datetime objects. This will allow you to compare times correctly (using
# ==, !=, <, >, etc.) instead of lexicographically as strings.

# Sample use:
# current_time = string_to_time(sqlitedb.getTime())

def string_to_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(globals)

    web.header('Content-Type','text/html; charset=utf-8', unique=True)

    return jinja_env.get_template(template_name).render(context)

#####################END HELPER METHODS#####################

urls = ('/currtime', 'curr_time',
        '/selecttime', 'select_time',
        '/search', 'search',
        '/add_bid', 'add_bid',
        '/auction/(.*)', 'auction',
        '/', 'curr_time',
        # TODO: add additional URLs here
        # first parameter => URL, second parameter => class name
        )

class curr_time:
    # A simple GET request, to '/currtime'
    #
    # Notice that we pass in `current_time' to our `render_template' call
    # in order to have its value displayed on the web page
    def GET(self):
        current_time = sqlitedb.getTime()
        return render_template('curr_time.html', time = current_time)

class select_time:
    # Aanother GET request, this time to the URL '/selecttime'
    def GET(self):
        return render_template('select_time.html')

    # A POST request
    #
    # You can fetch the parameters passed to the URL
    # by calling `web.input()' for **both** POST requests
    # and GET requests
    def POST(self):
        post_params = web.input()
        MM = post_params['MM']
        dd = post_params['dd']
        yyyy = post_params['yyyy']
        HH = post_params['HH']
        mm = post_params['mm']
        ss = post_params['ss']
        enter_name = post_params['entername']


        selected_time = '%s-%s-%s %s:%s:%s' % (yyyy, MM, dd, HH, mm, ss)
        update_message = '(Hello, %s. Previously selected time was: %s.)' % (enter_name, selected_time)
        # TODO: save the selected time as the current time in the database
        e = sqlitedb.updateCurrrentTime(selected_time)
        if e is not None:
            update_message = 'Can\'t update current time successfully.'
        # Here, we assign `update_message' to `message', which means
        # we'll refer to it in our template as `message'
        return render_template('select_time.html', message = update_message)


class search:
    def GET(self):
        return render_template('search.html')
    
    def POST(self):
        post_params = web.input()
        item_id = post_params['itemID']
        category = post_params['category']
        description = post_params['description']
        min_price = post_params['minPrice']
        max_price = post_params['maxPrice']
        status = post_params['status']
        current_time = string_to_time(sqlitedb.getTime())
        result = sqlitedb.getItems(item_id, category, description, min_price, max_price, status, current_time)
        return render_template('search.html', search_result = result)


class add_bid:
    def GET(self):
        return render_template('add_bid.html')
    
    def POST(self):
        post_params = web.input()
        item_id = post_params['itemID']
        user_id = post_params['userID']
        price = post_params['price']
        
        message = None
        add_result = None
        if item_id == '' or user_id == '' or price == '':
            message = 'All fields must be input!'
        else:
            item = sqlitedb.getItemById(item_id)
            user = sqlitedb.getUserById(user_id)
            if item is None and user is None:
                message = 'Item ID is incorrect. No such item exists! User ID is also incorrect. No such user exists!'
            elif item is None:
                message = 'Item ID is incorrect. No such item exists!'
            elif user is None:
                message = 'User ID is incorrect. No such user exists!'
            else:
                current_time = string_to_time(sqlitedb.getTime())
                if current_time < string_to_time(item.Started):
                    message = 'This auction has not started yet.'
                elif current_time > string_to_time(item.Ends):
                    message = 'This auction has been closed because the end time has past.'
                elif item.Buy_Price is not None and item.Number_of_Bids > 0 and item.Currently >= item.Buy_Price:
                    message = 'This auction has been closed because some bid reached the buy price.'
                elif price <= item.Currently:
                    message = 'Your bid must be higher than current price!'
                elif item.Buy_Price is not None and price >= item.Buy_Price:
                    message = sqlitedb.updateBid(user_id, item_id, price, current_time)
                    if message is None:
                        message = 'You have got the item because your bid is higher than the buy price.'
                        add_result = 'Success'
                else:
                    message = sqlitedb.updateBid(user_id, item_id, price, current_time)
                    if message is None:
                        message = 'Your bid has been placed!'
                        add_result = 'Success'

        return render_template('add_bid.html', message = message, add_result = add_result)


class auction:
    def GET(self, item_id):
        item = sqlitedb.getItemById(item_id)
        categories = None
        status = None
        bids = None
        winner = None
        if item is not None:
            categories = sqlitedb.getCategories(item_id)
            current_time = string_to_time(sqlitedb.getTime())
            if current_time < string_to_time(item.Started):
                status = 'notStarted'
            elif current_time > string_to_time(item.Ends):
                status = 'close'
            elif item.Buy_Price is not None and item.Number_of_Bids > 0 and item.Currently >= item.Buy_Price:
                status = 'close'
            else:
                status = 'open'

            bids = sqlitedb.getBids(item_id)

            if status == 'close':
                winner = sqlitedb.getWinner(item_id)

        return render_template('auction.html', item = item, status = status, winner = winner, categories = categories, bids = bids)


###########################################################################################
##########################DO NOT CHANGE ANYTHING BELOW THIS LINE!##########################
###########################################################################################

if __name__ == '__main__':
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))
    app.run()
