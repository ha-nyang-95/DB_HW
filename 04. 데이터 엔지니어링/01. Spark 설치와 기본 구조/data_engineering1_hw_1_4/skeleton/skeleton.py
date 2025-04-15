# 텍스트 데이터 로드 및 탐색 실습 Skeleton 파일
# 아래의 빈칸(____)을 채우세요

from pyspark.sql import SparkSession

# SparkSession 생성
spark = SparkSession.builder.appName("TextDataAnalysis").getOrCreate()
sc = spark.sparkContext

# 텍스트 파일 로드
text_data = sc.textFile("../data/test_1.txt")

# 전체 텍스트 출력
# ['The world’s most valuable resource is no longer oil, but data.', 
#  'Big Data and AI are transforming industries worldwide.', 
#  'Companies are investing heavily in real-time analytics.']
print(text_data.collect())

# 줄 수 출력
# 전체 줄 개수: 3
print("전체 줄 개수:", text_data.count())

# 'data'가 포함된 문장 필터링
# ['The world’s most valuable resource is no longer oil, but data.', 
#  'Big Data and AI are transforming industries worldwide.']
contains_data = text_data.filter(lambda line: 'data' in line.lower())
print(contains_data.collect())

# 포함된 줄 수 출력
# 전체 줄 개수: 2
print("전체 줄 개수:", contains_data.count())

# 대문자로 변환
# ['THE WORLD’S MOST VALUABLE RESOURCE IS NO LONGER OIL, BUT DATA.', 
#  'BIG DATA AND AI ARE TRANSFORMING INDUSTRIES WORLDWIDE.', 
#  'COMPANIES ARE INVESTING HEAVILY IN REAL-TIME ANALYTICS.']
upper_case_data = text_data.map(lambda line: line.upper())
print(upper_case_data.collect())

# 소문자로 변환
# ['the world’s most valuable resource is no longer oil, but data.', 
#  'big data and ai are transforming industries worldwide.', 
#  'companies are investing heavily in real-time analytics.']
lower_case_data = text_data.map(lambda line: line.lower())
print(lower_case_data.collect())

# 기본 파티션 개수 확인
# 기본 파티션 개수: 2
print("기본 파티션 개수:", text_data.getNumPartitions())

# 파티션 4개로 재설정 후 확인
# 변경된 파티션 개수: 4
repartitioned_data = text_data.repartition(4)
print("변경된 파티션 개수:", repartitioned_data.getNumPartitions())
