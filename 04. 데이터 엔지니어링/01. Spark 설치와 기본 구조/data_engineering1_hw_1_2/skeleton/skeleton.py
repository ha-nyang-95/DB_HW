
# 데이터 생성 및 변환 실습 Answer 파일

from pyspark.sql import SparkSession

# SparkSession 생성
spark = SparkSession.builder.appName("Transformations").getOrCreate()
sc = spark.sparkContext

# 1. 버전 확인
# Spark version: 3.5.4
print("Spark version:", sc.version)

# 2. 숫자 데이터 생성 및 변환 연산
# 1~20까지 숫자 데이터 생성
numbers = sc.parallelize(range(1, 21))

# 생성된 데이터 확인
# [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]         
print(numbers.collect())

# 각 숫자를 2배 변환
# [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40]
doubled = numbers.map(lambda x: x * 2)
print(doubled.collect())

# 10보다 큰 숫자만 출력
# [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
greater_than_10 = numbers.filter(lambda x: x > 10)
print(greater_than_10.collect())

# 1~20까지 생성된 숫자의 총 개수 확인
# 20
print(numbers.count())

# 10보다 큰 숫자의 총 개수 확인
# 10
print(greater_than_10.count())

# 3. 알파벳 문자열 데이터 변환 연산
alphabets = sc.parallelize(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])

# 생성된 알파벳 데이터 확인
# ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
print(alphabets.collect())

# 각 문자를 두 번 반복
# ['AA', 'BB', 'CC', 'DD', 'EE', 'FF', 'GG', 'HH', 'II', 'JJ']
repeated = alphabets.map(lambda x: x * 2)
print(repeated.collect())

# "E"보다 뒤에 있는 문자만 출력
# ['F', 'G', 'H', 'I', 'J']
after_E = alphabets.filter(lambda x: x > "E")
print(after_E.collect())

# "E"보다 뒤에 있는 문자의 총 개수 확인
# 5
print(after_E.count())

# 알파벳 데이터를 소문자로 변환
# ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
lower_alphabets = alphabets.map(lambda x: x.lower())
print(lower_alphabets.collect())

# 4. 랜덤 숫자 리스트 변환
random_numbers = sc.parallelize([3, 10, 5, 7, 1])

# 모든 숫자를 제곱
# [9, 100, 25, 49, 1]
squared = random_numbers.map(lambda x: x * x)
print(squared.collect())

# 제곱한 숫자의 값 중 10보다 큰 값만 출력
# [100, 25, 49]                                                                   
greater_than_10_sq = squared.filter(lambda x: x > 10)
print(greater_than_10_sq.collect())

# 10보다 큰 값의 총 개수 확인
# 3
print(greater_than_10_sq.count())
