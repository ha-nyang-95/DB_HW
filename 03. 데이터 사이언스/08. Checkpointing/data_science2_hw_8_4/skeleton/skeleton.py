import time
import os
import pandas as pd
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.checkpoint_storage import FileSystemCheckpointStorage
from pyflink.datastream.state_backend import RocksDBStateBackend
from pyflink.common.restart_strategy import RestartStrategies

# 체크포인트 저장 경로 설정
CHECKPOINT_PATH_FULL = "file:///tmp/flink-checkpoints/full"
CHECKPOINT_PATH_INCREMENTAL = "file:///tmp/flink-checkpoints/incremental"

def get_checkpoint_size(checkpoint_path):
    """ 저장된 체크포인트 크기 확인 """
    path = checkpoint_path.replace("file://", "")
    size = os.popen(f"du -sh {path}").read().strip()
    return size if size else "N/A"

def run_checkpoint_test(checkpoint_type="full"):
    """ RocksDB 기반 Full vs Incremental Checkpoint 비교 실행 """

    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    # 체크포인트 활성화 (5초마다)
    env.enable_checkpointing(5000)

    # 실행 모드 출력
    print(f"\n실행 모드: {checkpoint_type.capitalize()} Checkpoint")

    # 체크포인트 경로 선택
    checkpoint_path = CHECKPOINT_PATH_FULL if checkpoint_type == "full" else CHECKPOINT_PATH_INCREMENTAL

    # 체크포인트 스토리지 설정
    env.get_checkpoint_config().set_checkpoint_storage(FileSystemCheckpointStorage(checkpoint_path))  # 빈칸: 체크포인트 저장소 설정

    # RocksDB 상태 백엔드 설정 (incremental 여부 설정)
    use_incremental = checkpoint_type == "incremental"
    env.set_state_backend(RocksDBStateBackend(checkpoint_path, use_incremental))  # 빈칸: 상태 백엔드 설정

    # 재시작 전략 설정
    env.set_restart_strategy(RestartStrategies.fixed_delay_restart(3, 3000))  # 빈칸: 재시작 전략 설정

    # 데이터 로드
    df = pd.read_csv("../data/data.csv")
    transactions = df[['transaction_id', 'amount']].dropna().values.tolist()

    # 스트림 생성
    transaction_stream = env.from_collection(transactions)

    # 체크포인트 시간 측정 시작
    checkpoint_start = time.time()

    def process_data(value):
        """ 처리 함수 (0.5초 대기) """
        time.sleep(0.5)
        return value

    result = transaction_stream.map(process_data)
    result.print()

    # 실행
    print(f"{checkpoint_type.capitalize()} Checkpoint 실행 시작...")
    env.execute(f"{checkpoint_type.capitalize()} Checkpoint Test")

    # 체크포인트 시간 측정 종료
    checkpoint_end = time.time()
    checkpoint_duration = checkpoint_end - checkpoint_start
    print(f"Checkpoint 소요 시간: {checkpoint_duration:.2f}초")

    # 디스크 사용량 측정
    checkpoint_size = get_checkpoint_size(checkpoint_path)
    print(f"Checkpoint 저장 크기: {checkpoint_size}")

if __name__ == "__main__":
    print("Full Checkpoint 테스트 시작...")
    run_checkpoint_test("full")

    print("\nIncremental Checkpoint 테스트 시작...")
    run_checkpoint_test("incremental")
