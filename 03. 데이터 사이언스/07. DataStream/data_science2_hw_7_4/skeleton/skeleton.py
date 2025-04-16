import pandas as pd
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors import FileSink
from pyflink.common.serialization import Encoder
from pyflink.java_gateway import get_gateway

# 이상 거래 감지 임계값 설정
THRESHOLD  = 8000.0 # 이상 거래 탐지를 위한 임계값 설정 변수명

def main():
    # Flink 실행 환경 설정
    env = StreamExecutionEnvironment.get_execution_environment()
    # 병렬성 설정
    env.set_parallelism(1)  # 병렬성을 조정하는 함수

    # CSV 데이터 불러오기
    df = pd.read_csv("../data/data.csv")
    transactions = df[["transaction_id", "customer_id", "amount"]].dropna().values.tolist()  

    # 데이터 스트림 생성
    transaction_stream = env.from_collection(transactions, type_info=Types.TUPLE([Types.STRING(), Types.STRING(), Types.FLOAT()]))

    # 이상 거래 감지 (Threshold 초과 데이터만 필터링)
    suspicious_transactions = transaction_stream.filter(lambda x: x[2] > THRESHOLD)  # 필터링함수, 임계값을 초과하는 데이터 필터링 조건입력
    # 데이터를 문자열로 변환 후 저장
    formatted_stream = suspicious_transactions.map(lambda x: f"{x[0]}, {x[1]}, {x[2]}", output_type=Types.STRING())  # 데이터를 문자열로 변환하는 함수

    # 결과 실시간 출력
    formatted_stream.print()  # 스트림 데이터를 실시간으로 출력하세요.

    # FileSink 설정. File Sink를 사용하기 위해서는 JavaAPI가 반드시 필요.
    gateway = get_gateway()  
    j_string_encoder = gateway.jvm.org.apache.flink.api.common.serialization.SimpleStringEncoder()  # Java 엔코더 생성
    encoder = Encoder(j_string_encoder)  # Python Encoder 생성

    file_sink = FileSink.for_row_format(
        "./output/suspicious_transactions",  # 출력 디렉터리 지정
        encoder  # Encoder를 적용하여 파일 Sink를 설정하세요.
    ).build()

    # Sink에 데이터 연결 (파일 저장)
    formatted_stream.sink_to(file_sink)  # 데이터를 FileSink에 연결하세요.

    # 실행
    env.execute("Anomaly Detection in Transactions with File Sink")  # Flink 작업을 실행하세요.

if __name__ == "__main__":
    main()
