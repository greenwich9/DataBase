SELECT COUNT(DISTINCT u.user_id) FROM Users u JOIN Items i
ON u.user_id = i.seller_id
WHERE u.rating > 1000;