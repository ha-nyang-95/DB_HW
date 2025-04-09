# Flink 체크포인트 성능 비교

✅ PyFlink 실습 정리: Full vs Incremental Checkpoint 성능 비교 실험
========================================================

📌 1. 실험 목표
-----------

> Flink의 상태 저장 기능인 **Checkpoint**의 두 방식인 **Full**과 **Incremental**을 직접 실험하고, 각 방식의 **처리 속도**와 **저장 용량**의 차이를 비교한다.

* * *

🧠 2. Checkpoint란?
------------------

Flink는 작업 중간에 상태를 주기적으로 저장해서 장애 발생 시 복구할 수 있도록 합니다. 이 기능을 **Checkpoint**라고 합니다.

### ✅ 두 가지 방식 비교

| 구분 | Full Checkpoint | Incremental Checkpoint |
| --- | --- | --- |
| 저장 방식 | 전체 상태를 매번 저장 | 이전과 변경된 부분만 저장 |
| 속도 | 느림 | 빠름 |
| 저장 공간 | 많이 사용 | 적게 사용 |
| 설정 | 간단함 | RocksDB 사용 필요 |

* * *

⚙️ 3. 실험 환경 및 파일 구조
-------------------

```bash
Flink_Checkpoint_실험/
├── skeleton.py           ← 실험 전체 코드
├── data/
│   └── data.csv          ← 실험에 사용할 트랜잭션 데이터
```

* * *

🧩 4. 실습 코드 (주석 기반 설명 포함)
-------------------------

```python
import time                       # 처리 시간 측정용
import os                         # 체크포인트 디렉토리 크기 확인용
import pandas as pd              # CSV 파일을 불러오기 위해 사용

# Flink 스트리밍 환경 설정 관련 모듈
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.checkpoint_storage import FileSystemCheckpointStorage
from pyflink.datastream.state_backend import RocksDBStateBackend
from pyflink.common.restart_strategy import RestartStrategies

# 체크포인트 저장 경로 설정 (로컬 경로를 file:// 형식으로 작성)
CHECKPOINT_PATH_FULL = "file:///tmp/flink-checkpoints/full"
CHECKPOINT_PATH_INCREMENTAL = "file:///tmp/flink-checkpoints/incremental"

def get_checkpoint_size(checkpoint_path):
    """
    저장된 체크포인트 디렉토리의 용량을 측정하여 반환.
    - 'du -sh' 명령어를 사용해 경로 크기를 계산함
    - 결과가 없으면 "N/A" 반환
    """
    path = checkpoint_path.replace("file://", "")  # 경로에서 file:// 제거
    size = os.popen(f"du -sh {path}").read().strip()  # 경로 크기 측정
    return size if size else "N/A"

def run_checkpoint_test(checkpoint_type="full"):
    """
    Full 또는 Incremental 체크포인트 방식으로 Flink 작업 실행
    - 체크포인트 저장 경로, 백엔드, 주기, 재시작 전략 설정
    - 데이터 처리 후 소요 시간 및 저장 크기 출력
    """
    
    # Flink 실행 환경 생성
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)  # 병렬 처리 비활성화 (하나의 작업만 실행하도록 설정)

    # 체크포인트 주기 설정 (5000ms = 5초)
    env.enable_checkpointing(5000)

    # 현재 실행 모드 출력
    print(f"\n실행 모드: {checkpoint_type.capitalize()} Checkpoint")

    # 실행 모드에 따라 체크포인트 저장 경로 선택
    checkpoint_path = CHECKPOINT_PATH_FULL if checkpoint_type == "full" else CHECKPOINT_PATH_INCREMENTAL

    # 체크포인트를 로컬 파일 시스템에 저장하도록 설정
    env.get_checkpoint_config().set_checkpoint_storage(FileSystemCheckpointStorage(checkpoint_path))

    # 상태 백엔드 설정
    # - Full: RocksDB 사용하지만 incremental=False
    # - Incremental: RocksDB + incremental=True
    use_incremental = checkpoint_type == "incremental"
    env.set_state_backend(RocksDBStateBackend(checkpoint_path, use_incremental))

    # 장애 발생 시 자동으로 재시작하도록 전략 설정 (최대 3회, 3초 간격)
    env.set_restart_strategy(RestartStrategies.fixed_delay_restart(3, 3000))

    # CSV 파일을 Pandas로 읽어오기 (transaction_id, amount만 사용)
    df = pd.read_csv("../data/data.csv")
    transactions = df[['transaction_id', 'amount']].dropna().values.tolist()  # 결측치 제거 후 리스트로 변환

    # Flink에서 사용할 스트림 생성 (리스트 기반)
    transaction_stream = env.from_collection(transactions)

    # 체크포인트 성능 측정 시작 시간 기록
    checkpoint_start = time.time()

    # 데이터 처리 함수 정의: 각 데이터를 0.5초 대기 후 그대로 반환
    def process_data(value):
        time.sleep(0.5)  # 0.5초 지연 (처리 시간이 있는 것처럼 만들기 위한 시뮬레이션)
        return value

    # Flink 스트림에 처리 함수 적용 및 결과 출력 설정
    result = transaction_stream.map(process_data)
    result.print()  # 결과를 콘솔에 출력

    # Flink 실행 시작
    print(f"{checkpoint_type.capitalize()} Checkpoint 실행 시작...")
    env.execute(f"{checkpoint_type.capitalize()} Checkpoint Test")

    # 실행 종료 시간 기록
    checkpoint_end = time.time()
    checkpoint_duration = checkpoint_end - checkpoint_start  # 총 소요 시간 계산

    # 체크포인트 실행 시간 출력
    print(f"Checkpoint 소요 시간: {checkpoint_duration:.2f}초")

    # 체크포인트 저장 경로의 디스크 사용량 출력
    checkpoint_size = get_checkpoint_size(checkpoint_path)
    print(f"Checkpoint 저장 크기: {checkpoint_size}")

if __name__ == "__main__":
    # Full 체크포인트 방식 테스트 실행
    print("Full Checkpoint 테스트 시작...")
    run_checkpoint_test("full")

    # Incremental 체크포인트 방식 테스트 실행
    print("\nIncremental Checkpoint 테스트 시작...")
    run_checkpoint_test("incremental")
```

* * *

🧪 5. 실행 결과 예시
--------------

```bash
Full Checkpoint 테스트 시작...

실행 모드: Full Checkpoint
[1000.0, 7341.46]
[1001.0, 3799.52]
...
[1049.0, 1235.08]
Checkpoint 소요 시간: 29.74초
Checkpoint 저장 크기: 16K       /tmp/flink-checkpoints/full

Incremental Checkpoint 테스트 시작...

실행 모드: Incremental Checkpoint
[1000.0, 7341.46]
[1001.0, 3799.52]
...
[1049.0, 1235.08]
Checkpoint 소요 시간: 27.82초
Checkpoint 저장 크기: 16K       /tmp/flink-checkpoints/incremental
```

* * *

🔍 6. 결과 해석
-----------

| 항목 | Full Checkpoint | Incremental Checkpoint |
| --- | --- | --- |
| **처리 시간** | 29.74초 | 27.82초 |
| **저장 크기** | 16K | 16K |

### ✔️ 해석 요약

*   Incremental 방식이 약간 더 빠름  
    → 변경된 상태만 저장하기 때문
    
*   저장 용량은 동일  
    → 데이터 양이 적어 두 방식 모두 16K 수준
    
*   **데이터가 많아질수록 Incremental 방식의 이점(속도 + 저장 효율성)이 커짐**
    

* * *

🧠 7. 학습 포인트 요약
---------------

*   **HashMapStateBackend**는 Full Checkpoint에 적합한 기본 방식
    
*   **RocksDBStateBackend**는 Incremental Checkpoint를 지원하는 고급 방식
    
*   Checkpoint 설정 시에는 반드시 저장 위치와 백엔드를 명확하게 설정해야 한다
    
*   PyFlink에서는 `env.execute()`가 있어야 작업이 실행된다
    

* * *

📎 8. 활용 팁
----------

*   대용량 데이터를 다룰 때는 반드시 Incremental 방식으로 설정하자.
    
*   실시간 스트리밍 또는 복구가 중요한 서비스에서 Checkpoint는 필수다.
    
*   이 실험 코드를 템플릿 삼아 다른 실험(예: 상태 복구, savepoint 등)도 시도해보자!
    

* * *

필요하다면 이 내용을 `.pdf`, `.md`, 또는 `.ipynb` 형식으로 저장해드릴 수 있습니다.  
다음으로는 결과 시각화나, **savepoint 실험** 또는 **Kafka 연동 실습**도 도전해보고 싶으신가요? 😄



---
Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)