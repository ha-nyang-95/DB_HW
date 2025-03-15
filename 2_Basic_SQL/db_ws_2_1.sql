CREATE DATABASE movies

USE movies

-- 2_1 --
CREATE TABLE movie_list(
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255),
    genre VARCHAR(100),
    release_year YEAR
);

INSERT INTO movie_list (title,genre,release_year)
VALUES
('Inception', 'Sci-Fi', 2010),
('The Dark Knight', 'Action', 2008),
('Interstellar', 'Sci-Fi', 2014),
('Unknown', 'Drama', Null),
('The Shawshank Redemption', 'Drama', 1994),
('Fight Club', 'Drama', 1999),
('Mad Max: Fury Road', 'Action', 2015),
('Star Wars: The Force Awakens', 'Sci-Fi', 2015);

SELECT * FROM movie_list;

-- 2_2 --
SELECT * FROM movie_list
WHERE release_year > 2010;

SELECT * FROM movie_list
WHERE genre = 'Action' OR genre = 'Sci-Fi'

SELECT * FROM movie_list
WHERE title LIKE 'The%'

SELECT * FROM movie_list
WHERE release_year BETWEEN 2008 AND 2014

SELECT * FROM movie_list
WHERE release_year IS NULL

SELECT * FROM movie_list;

-- 2_3 --
SELECT * FROM movie_list
WHERE release_year BETWEEN 2000 AND 2010;

SELECT * FROM movie_list
WHERE title BETWEEN 'A' AND 'M';

SELECT * FROM movie_list
WHERE (genre='Drama') AND (release_year BETWEEN 1990 AND 2000);

SELECT * FROM movie_list
WHERE (release_year BETWEEN 2015 AND 2020) 
AND (genre='Sci-Fi' OR genre='Action');

SELECT * FROM movie_list
WHERE release_year>2005 AND release_year<2015

SELECT * FROM movie_list;

-- 2_4 --
INSERT INTO movie_list (title,genre,release_year)
VALUES
('The Matrix','Sci-Fi',1999),
('Gladiator', 'Action',2000),
('Jurassic Park','Sci-Fi',1993),
('The Fugitive','Action',1993);

SELECT title FROM movie_list
WHERE genre='Drama' AND release_year IS NOT NULL
ORDER BY release_year
LIMIT 1;

SELECT title,release_year FROM movie_list
WHERE release_year>2000 AND release_year IS NOT NULL
ORDER BY release_year DESC
LIMIT 1;

SELECT * FROM movie_list
WHERE genre IN ('Sci-Fi', 'Action')
  AND release_year IN (
    SELECT release_year
    FROM movie_list
    WHERE genre = 'Drama'
      AND release_year IS NOT NULL
  );

SELECT * FROM movie_list
WHERE genre='Sci-Fi' 
AND release_year > (SELECT AVG(release_year) FROM movie_list WHERE genre='Action');

SELECT * FROM movie_list
WHERE genre!='Action'
AND release_year=(SELECT MIN(release_year) FROM movie_list WHERE genre='Action');

SELECT * FROM movie_list;

-- 2_5 --
SELECT genre FROM movie_list
GROUP BY genre
ORDER BY COUNT(*) DESC
LIMIT 1

SELECT * FROM movie_list
WHERE genre=(
    SELECT genre FROM movie_list
    GROUP BY genre
    ORDER BY COUNT(*) DESC
    LIMIT 1
    );

SELECT 
genre, 
COUNT(*) AS movie_count, 
AVG(release_year) AS avg_release_year 
FROM movie_list
WHERE release_year IS NOT NULL
GROUP BY genre;

SELECT m1.genre, m1.title, m1.release_year 
FROM movie_list AS m1
JOIN(
    SELECT genre,MAX(release_year) AS max_year
    FROM movie_list
    GROUP BY genre
) AS m2
    ON m1.genre=m2.genre
    AND m1.release_year = m2.max_year
ORDER BY m1.release_year

SELECT * FROM movie_list m1
WHERE release_year=(
    SELECT MIN(release_year)
    FROM movie_list
    WHERE genre='Action'
    )
ORDER BY release_year,title;

SELECT * FROM movie_list
WHERE genre in ('Sci-Fi','Action') AND release_year in (
        SELECT release_year
        FROM movie_list
        WHERE genre='Drama'
        )
ORDER BY release_year;

SELECT * FROM movie_list;