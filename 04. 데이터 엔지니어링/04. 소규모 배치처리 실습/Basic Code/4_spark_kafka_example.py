from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import findspark

# 로컬 Python 환경에서 Spark를 사용할 수 있도록 초기화
findspark.init()

# Spark 세션 생성 함수
# 애플리케이션 이름 지정
# Kafka 연동용 패키지 자동 다운로드
def create_spark_session():
    return SparkSession.builder \
        .appName("KafkaSparkStreaming") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .getOrCreate()

# Kafka 스트림 처리 메인 함수
def process_kafka_stream():
    # Spark 세션 생성
    spark = create_spark_session()
    
    # Kafka에서 스트림 데이터 읽기
    # 실시간 스트림 읽기 시작
    # 데이터 소스 형식 지정
    # Kafka 브로커 주소
    # 구독할 Kafka 토픽 이름
    # 가장 마지막 오프셋부터 읽기 시작
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "test-topic") \
        .option("startingOffsets", "latest") \
        .load()
    
    # Kafka 메시지의 value는 binary 형태 → 문자열로 변환
    value_df = df.selectExpr("CAST(value AS STRING)")

    # Kafka 메시지 안의 JSON을 파싱하기 위한 스키마 정의
    # 이벤트 발생 시각
    # 메시지 본문
    schema = StructType([
        StructField("timestamp", TimestampType(), True),
        StructField("message", StringType(), True)
    ])
    
    # JSON 문자열을 구조화된 컬럼으로 파싱
    # JSON 파싱 후 "data" 컬럼으로 감싸기
    # 컬럼 펼치기 (timestamp, message 등으로 분리)
    parsed_df = value_df.select(
        from_json(col("value"), schema).alias("data")
    ).select("data.*")
    
    # 타임스탬프 기준으로 1분 단위 윈도우 집계
    # 1분 지연까지 허용 (이벤트 타임 기반)
    # 1분 단위로 타임스탬프 윈도우 분할
    result_df = parsed_df \
        .withWatermark("timestamp", "1 minute") \
        .groupBy(window("timestamp", "1 minute")) \
        .count()  # 각 윈도우별 메시지 수 계산
    
    # 실시간 집계 결과를 콘솔에 출력
    # 스트림 결과 쓰기 시작
    # 전체 윈도우 결과를 계속 갱신
    # 콘솔로 출력
    # 스트리밍 쿼리 시작
    query = result_df \
        .writeStream \
        .outputMode("complete") \
        .format("console") \
        .start()

    # 스트리밍 작업이 끝날 때까지 대기
    query.awaitTermination()

# 메인 함수 실행
if __name__ == "__main__":
    process_kafka_stream()
