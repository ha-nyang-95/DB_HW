-- Sorting data
-- Order by example 1
SELECT 
  GovernmentForm
FROM 
  country
ORDER BY
  GovernmentForm;

-- Order by example 2
SELECT 
  GovernmentForm, SurfaceArea
FROM 
  country
ORDER BY
  GovernmentForm DESC;

-- Order by example 3
SELECT 
  GovernmentForm, SurfaceArea
FROM 
  country
ORDER BY
  GovernmentForm DESC, SurfaceArea ASC;

-- Order by example 4
SELECT
  Name, IndepYear
FROM
  country
WHERE
  Continent = 'Asia'
ORDER BY 
  IndepYear;

-- Order by example 5
SELECT
  Name, IndepYear
FROM
  country
WHERE
  Continent = 'Asia'
ORDER BY 
  IndepYear IS NULL, IndepYear;
-- PostgreSQL 같은 경우에는...
  -- IndepYear ASC NULLS LAST;

-- Limit example 1
SELECT 
  IndepYear, Name, Population
FROM 
  country
ORDER BY 
  Population DESC
LIMIT 7;

-- Limit example 2
SELECT 
  IndepYear, Name, Population
FROM 
  country
ORDER BY 
  Population DESC
LIMIT 4, 7;
-- LIMIT 7 OFFSET 4;


-- Aggregate Function​

-- 집계 함수 1
SELECT COUNT(*) FROM country;
SELECT COUNT(IndepYear) FROM country;

-- 집계 함수 2
SELECT SUM(GNP) FROM country WHERE Continent = 'Asia';
SELECT AVG(GNP) FROM country WHERE Continent = 'Asia';

-- 집계 함수 3
SELECT MAX(GNP) FROM country WHERE Continent = 'Asia';
SELECT MIN(GNP) FROM country WHERE Continent = 'Asia';

-- 집계 함수 4
SELECT STDDEV(GNP) FROM country WHERE Continent = 'Asia';
SELECT VARIANCE(GNP) FROM country WHERE Continent = 'Asia';


-- GROUP BY 

-- Group by 예시 1
SELECT
  Continent
FROM
  country
GROUP BY
  Continent;

-- Group by 예시 2
SELECT
  Continent, COUNT(*)
FROM
  country
GROUP BY
  Continent;

SELECT
  Continent, COUNT(IndepYear)
FROM
  country
GROUP BY
  Continent;

-- group by example 1
SELECT
  Continent, 
  ROUND(AVG(GNP), 2) AS avg_gnp
FROM
  country
GROUP BY
  Continent;


-- group by example 2
-- error code
SELECT
  Region,
  COUNT(Region) AS count_reg
FROM
  country
WHERE
  count_reg BETWEEN 15 AND 20 
GROUP BY
  Region
ORDER BY 
  count_reg DESC;

-- correct code
SELECT
  Region,
  COUNT(Region) AS count_reg
FROM
  country
GROUP BY
  Region
HAVING
  count_reg BETWEEN 15 AND 20
ORDER BY 
  count_reg DESC;
