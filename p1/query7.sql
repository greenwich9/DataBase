SELECT COUNT(DISTINCT item_category)
FROM Categories c JOIN Bids b ON c.item_id = b.item_id
WHERE b.amount > 100;