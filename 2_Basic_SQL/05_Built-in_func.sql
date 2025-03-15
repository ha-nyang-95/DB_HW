-- Built-in Function
-- 문자형 함수
-- CONCAT
SELECT CONCAT('FirstName', '_', 'LastName');

-- TRIM
SELECT TRIM('   PHONE   ');
SELECT TRIM('-' FROM '---TITLE---');
SELECT TRIM(LEADING '-' FROM '---TITLE---');
SELECT TRIM(TRAILING '-' FROM '---TITLE---');

-- REPLACE
SELECT REPLACE('$10000', '$', '￦');

-- LOCATE
SELECT LOCATE('path', 'www.web-path-site.com/path/');
SELECT LOCATE('path', 'www.web-path-site.com/path/', 10);

-- 숫자형 함수
-- ABS 함수
SELECT ABS(-12);
-- MOD 함수 (나머지 구하기)
SELECT MOD(10, 7);
SELECT 10%7;   -- MOD와 동일함

-- POW 함수 (제곱근 구하기)
SELECT POW(2, 6);   -- 단축어
SELECT POWER(2, 6); -- POW와 동일함 

-- CEIL 함수
SELECT CEIL(3.7);
SELECT CEIL(3.3);
-- FLOOR 함수
SELECT FLOOR(3.7);
SELECT FLOOR(3.2);
-- ROUND 함수
SELECT ROUND(3.7);
SELECT ROUND(3.2);

-- 날짜형 함수
-- 현재 날짜
SELECT CURDATE();
-- 현재 시간
SELECT CURTIME();
-- 현재 날짜 및 시간
SELECT NOW();
-- 시간 포멧 설정하기
SELECT DATE_FORMAT
('2024-08-23 13:35:20', '%b-%d (%a) %r');

-- NULL 관련 함수
-- IFNULL 함수
SELECT IFNULL(NULL, 'expr1 is NULL');
SELECT IFNULL('expr1', 'expr1 is NULL');

-- IFNULL 함수 example
SELECT 
  Name,
  -- IndepYear,  
  IFNULL(IndepYear, 'no_data') 
FROM 
  country
WHERE 
  Continent = 'North America'; 

-- NULLIF 함수
SELECT NULLIF('expr1', 'expr1');
SELECT NULLIF('expr1', 'expr2');
-- NULLIF 함수 example
SELECT 
  Name, 
  -- Population,
  NULLIF(Population, 0)
FROM country;

-- COALESCE 함수
SELECT COALESCE('expr1', 'expr2', NULL);
SELECT COALESCE(NULL, 'expr2', NULL);
SELECT COALESCE(NULL, NULL, NULL);

-- COALESCE 함수 예시
SELECT 
  -- Name, GNP, GNPOld,
  Name,
  COALESCE(NULLIF(GNP, 0), GNPOld, 'No data') AS gnp_data
FROM country
WHERE
  Continent = 'Africa'
  AND LifeExpectancy < 70;

-- GNP에 의한 데이터인지... GNPOld에 대한 데이터인지 알 수가 없다...
SELECT
  Name, 
  CASE
    WHEN GNP > 0 THEN CONCAT(GNP, ' (GNP)')
    WHEN GNPOld IS NOT NULL THEN CONCAT(GNPOld, ' (GNPOld)')
    ELSE 'no_data'
  END AS gnp_data
FROM country
WHERE
  Continent = 'Africa'
  AND LifeExpectancy < 70;

