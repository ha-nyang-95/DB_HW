-- 3_2 --
CREATE DATABASE library_db

USE library_db

DROP TABLE authors;
DROP TABLE genres;
DROP TABLE books;

CREATE TABLE authors(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100)
);

CREATE TABLE genres(
    id INT PRIMARY KEY AUTO_INCREMENT,
    genre_name VARCHAR(100)
);

CREATE TABLE books(
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100),
    author_id INT,
    genre_id INT,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
);

INSERT INTO authors (name)
VALUES
('J.K. Rowling'),
('George R.R. Martin'),
('J.R.R. Tolkien'),
('Isaac Asimov'),
('Agatha Christie');

INSERT INTO genres (genre_name)
VALUES
('Fantasy'),
('Science Fiction'),
('Mystery'),
('Thriller');

INSERT INTO books (title, author_id, genre_id)
VALUES
("Harry Potter and the Philosopher's Stone",1,1),
("Harry Potter and the Chamber of Secrets",1,1),
("A Game of Thrones",2,1),
("A Clash of Kings",2,1),
("The Hobbit",3,1),
("The Lord of the Rings",3,1),
("Foundation",4,2),
("I, Robot",4,2),
("Murder on the Orient Express",5,3),
("The Mysterious Affair at Styles",5,3),
("The Girl with the Dragon Tattoo",5,4);


SELECT * FROM authors;
SELECT * FROM genres;
SELECT * FROM books;

-- 3_4 --
ALTER TABLE authors
ADD INDEX idx_authors_name (name);

ALTER TABLE genres
ADD INDEX idx_genres_genre_name (genre_name);

-- SHOW INDEX FROM authors;
-- SHOW INDEX FROM genres;

SELECT books.title,authors.name,genres.genre_name
FROM books
JOIN authors ON authors.id = books.author_id
JOIN genres ON genres.id = books.genre_id
ORDER BY books.id;

SELECT books.title,authors.name,genres.genre_name
FROM books
JOIN authors ON authors.id = books.author_id
JOIN genres ON genres.id = books.genre_id
WHERE authors.name = 'J.K. Rowling' AND genres.genre_name = 'Fantasy'
ORDER BY books.id;


SELECT * FROM authors;
SELECT * FROM genres;
SELECT * FROM books;
