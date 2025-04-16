CREATE DATABASE restaurants

USE restaurants

-- 2_a --
CREATE TABLE restaurants(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    location VARCHAR(255),
    cuisine_type VARCHAR(100)
);

CREATE TABLE menus(
    id INT PRIMARY KEY AUTO_INCREMENT,
    restaurant_id INT,
    item_name VARCHAR(255),
    price DECIMAL(10,2),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);

INSERT INTO restaurants (name, location, cuisine_type)
VALUES
('Sushi Place','Tokyo','Japanese'),
('Pasta Paradise','Rome','Italian'),
('Curry Corner','Mumbai','Indian');

INSERT INTO menus (restaurant_id,item_name,price)
VALUES
(1,'Salmon Nigiri',5.50),
(1,'Tuna Sashimi',6.00),
(2,'Spaghetti Carbonara',7.50),
(2,'Margherita Pizza',8.00),
(3,'Chicken Curry',6.50),
(3,'Vegetable Biryani',5.00);

SELECT * FROM restaurants;
SELECT * FROM menus;

-- 2_b --
SELECT name, location 
FROM restaurants;

SELECT item_name, price 
FROM menus 
WHERE price >= 6.00;

-- 2_c --
DROP TABLE menus;

CREATE TABLE menus (
    id INT PRIMARY KEY AUTO_INCREMENT,
    restaurant_id INT,
    item_name VARCHAR(255),
    price DECIMAL(10, 2),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants (id) ON DELETE CASCADE
);

DELETE FROM menus
WHERE item_name = 'Salmon Nigiri';

-- 테이블을 생성할 때, 외래키 참조에 ON DELETE CASCADE를 적어줘야
-- 삭제가 가능하다.
-- 이때, restaurants의 Pasta Paradise와 외래키로 연결된
-- menus 테이블 값들 또한 삭제된다.
-- 아니면, menus 테이블과 연결되어 있기 때문에, 삭제시 오류가 뜬다.
DELETE FROM restaurants
WHERE name = 'Pasta Paradise';

SELECT * 
FROM restaurants;

SELECT *
FROM menus;