SELECT i.item_id FROM Items i
WHERE i.currently = (SELECT MAX(currently) FROM Items);