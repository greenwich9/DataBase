DROP TABLE IF EXISTS Items;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Categories;
DROP TABLE IF EXISTS Bids;
CREATE TABLE Items (
    item_id INTEGER,
    item_name VARCHAR(100) NOT NULL,
    currently FLOAT NOT NULL,
    first_bid FLOAT NOT NULL,
    number_of_bids INTEGER NOT NULL,
    starts DATETIME NOT NULL,
    ends DATETIME NOT NULL,
    seller_id VARCHAR(100) NOT NULL,
    buy_price FLOAT,
    item_description VARCHAR(300),
    PRIMARY KEY(item_id),
    FOREIGN KEY(item_id) REFERENCES Categories(item_id),
    FOREIGN KEY(seller_id) REFERENCES Users(user_id)
);

CREATE TABLE Categories (
    item_id INTEGER,
    item_category VARCHAR(80) NOT NULL,
    PRIMARY KEY(item_id,item_category)
);
CREATE TABLE Users (
    user_id VARCHAR(100),
    country VARCHAR(30),
    city_location VARCHAR(40),
    rating INTEGER NOT NULL,
    PRIMARY KEY(user_id)
);
CREATE TABLE Bids (
    bidder_id VARCHAR(100),
    item_id INTEGER NOT NULL,
    bid_time DATETIME NOT NULL,
    amount FLOAT NOT NULL,
    PRIMARY KEY(bidder_id,item_id,bid_time),
    FOREIGN KEY(item_id) REFERENCES Items(item_id),
    FOREIGN KEY(bidder_id) REFERENCES Users(user_id)
);




