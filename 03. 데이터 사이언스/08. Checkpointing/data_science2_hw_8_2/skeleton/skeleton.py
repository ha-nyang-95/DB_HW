import os
import time
import pandas as pd
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.checkpoint_storage import FileSystemCheckpointStorage
from pyflink.datastream.functions import MapFunction
from pyflink.common.restart_strategy import RestartStrategies

# Checkpoint 저장 경로 설정
CHECKPOINT_PATH = "file:///tmp/flink-checkpoints"

class FailingMapFunction(MapFunction):
    """특정 데이터에서 강제 예외 발생하여 Checkpoint 복구 테스트"""
    def __init__(self):
        self.counter = 0  # 데이터를 처리한 개수를 추적하는 변수

    def map(self, value):
        self.counter += 1
        time.sleep(1)  # 스트리밍처럼 동작하도록 딜레이 추가

        # 특정 데이터에서 예외 발생
        if self.counter == 5:
            print(f"Checkpoint 실패 발생! Transaction ID: {value[0]}")
            raise Exception("의도적인 Checkpoint 실패 발생")

        return value

def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1) 

    # Checkpoint 활성화 (간격: 5000 ms)
    env.enable_checkpointing(5000)  # 체크포인트 활성화 함수 작성

    # Checkpoint 저장소 설정 (파일 시스템 경로 필요)
    env.get_checkpoint_config().set_checkpoint_storage(FileSystemCheckpointStorage(CHECKPOINT_PATH))  # 체크포인트 저장소 경로 지정

    # 장애 발생 시 자동 재시작 설정 (최대 재시도 횟수, 대기 시간 설정 필요)
    env.set_restart_strategy(RestartStrategies.fixed_delay_restart(3, 5000))  # 재시작 전략

    # CSV 데이터 로드
    df = pd.read_csv("../data/data.csv")
    transactions = df[['transaction_id', 'amount']].dropna().values.tolist()

    # Flink 데이터 스트림 생성
    transaction_stream = env.from_collection(transactions)

    # Checkpoint 테스트를 위한 데이터 처리
    transaction_stream = transaction_stream.map(FailingMapFunction())

    # 데이터 출력
    transaction_stream.print()

    # 잡 실행
    print("Flink Job을 제출합니다...")
    env.execute("Checkpoint Recovery Example")

if __name__ == "__main__":
    main()
