# Flink 과제 실행 방법

📘 Apache Flink Checkpoint 실습 과제 정리본 (비전공자용 완성본)
================================================

* * *

🎯 과제 목표
--------

Flink의 **Checkpoint 기능**과 **Restart Strategy**를 실습을 통해 이해하고,  
장애가 발생했을 때 Flink가 어떻게 자동 복구하는지를 확인하는 것이 목표입니다.

* * *

✅ 실습 환경 준비
----------

*   Flink 설치 위치: `/usr/local/flink-1.20.0`
    
*   실행 명령어:
    
    ```bash
    cd /usr/local/flink-1.20.0
    ./bin/start-cluster.sh
    ```
    
*   Web UI 확인: `http://localhost:8081` 접속
    

* * *

✅ 가상환경 실행 (선택 사항)
-----------------

```bash
cd ~/data_science2_hw_8_2
source venv/bin/activate
```

* * *

✅ 실행 파일: `skeleton/skeleton.py`
-------------------------------

*   CSV 파일: `../data/data.csv`
    
*   실행 명령어:
    
    ```bash
    cd skeleton
    python skeleton.py
    ```
    

* * *

✅ 실습 코드 전체 (비전공자용 상세 주석 포함)
---------------------------

```python
# 필수 라이브러리 불러오기
import os
import time
import pandas as pd  # CSV 파일을 다루기 위한 라이브러리

# Flink 관련 모듈 불러오기
from pyflink.datastream import StreamExecutionEnvironment  # Flink 실행 환경 생성용
from pyflink.datastream.checkpoint_storage import FileSystemCheckpointStorage  # 체크포인트 저장 위치 설정용
from pyflink.datastream.functions import MapFunction  # 사용자 정의 데이터 처리 함수 생성용
from pyflink.common.restart_strategy import RestartStrategies  # 장애 발생 시 재시작 전략 설정용

# 체크포인트 데이터를 저장할 로컬 디렉토리 설정
CHECKPOINT_PATH = "file:///tmp/flink-checkpoints"

# 사용자 정의 MapFunction 클래스 정의
# 데이터가 들어올 때마다 하나씩 처리하며, 5번째 데이터에서 의도적으로 오류를 발생시켜 Flink의 복구 기능을 실험합니다.
class FailingMapFunction(MapFunction):
    def __init__(self):
        self.counter = 0  # 몇 번째 데이터를 처리 중인지 기록하는 변수

    def map(self, value):  # 각 데이터에 대해 실행되는 함수
        self.counter += 1
        time.sleep(1)  # 1초간 멈춤 (실시간처럼 보이게)

        # 5번째 데이터를 처리할 때 의도적으로 에러를 발생시킴
        if self.counter == 5:
            print(f"Checkpoint 실패 발생! Transaction ID: {value[0]}")
            raise Exception("의도적인 Checkpoint 실패 발생")

        return value  # 문제 없으면 원래 데이터 그대로 반환

# main 함수: Flink 스트림 처리 전체 흐름을 구성
def main():
    # Flink 실행 환경 생성
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)  # 병렬 처리 없이 순차적으로 실행

    # 5초마다 자동으로 Checkpoint 저장하도록 설정
    env.enable_checkpointing(5000)  # 단위: 밀리초

    # 체크포인트 파일 저장 위치 설정
    env.get_checkpoint_config().set_checkpoint_storage(
        FileSystemCheckpointStorage(CHECKPOINT_PATH)
    )

    # 장애 발생 시 재시작 전략 설정
    # 최대 3회까지, 5초 간격으로 재시도
    env.set_restart_strategy(RestartStrategies.fixed_delay_restart(3, 5000))

    # Pandas로 CSV 파일 읽기
    df = pd.read_csv("../data/data.csv")  # transaction_id, amount 컬럼이 있다고 가정
    df = df[['transaction_id', 'amount']].dropna()  # 필요한 열만 선택하고, 결측값 제거
    transactions = df.values.tolist()  # 2차원 리스트로 변환 [[id, amount], ...]

    # 리스트를 Flink 스트림 데이터로 변환
    transaction_stream = env.from_collection(transactions)

    # 사용자 정의 MapFunction 적용 (5번째 데이터에서 에러 발생)
    transaction_stream = transaction_stream.map(FailingMapFunction())

    # 처리 결과 출력 (터미널에서 확인 가능)
    transaction_stream.print()

    # Flink Job 실행
    print("🚀 Flink Job을 제출합니다...")
    env.execute("Checkpoint Recovery Example")  # Job 이름 지정

# main 함수 실행 (스크립트를 직접 실행했을 때만 동작)
if __name__ == "__main__":
    main()
```

* * *

🔍 실행 결과로 확인할 점
---------------

| 확인 항목 | 설명 |
| --- | --- |
| `[1000.0, ...]` 데이터 출력 | 데이터가 스트림으로 잘 들어왔음 |
| `Checkpoint 실패 발생! Transaction ID: 1004.0` | 5번째 데이터에서 의도적으로 오류 발생 |
| 동일 데이터 반복 출력 | Flink가 Checkpoint에서 상태 복원 중 |
| 최대 3회 재시도 후 Job 실패 | 재시도 전략이 제대로 적용됨 |

* * *

✅ Checkpoint 상태 확인
------------------

```bash
ls /tmp/flink-checkpoints
```

→ 디렉토리가 생성되면 Checkpoint 기능이 정상 작동한 것

* * *

✅ Flink Web UI에서 Job 확인
-----------------------

*   주소: `http://localhost:8081`
    
*   Job 이름: "Checkpoint Recovery Example"
    
*   상태: RUNNING → RESTARTING → FAILED (정상 흐름)
    

* * *

🧪 추가 실험 (선택)
-------------

| 실험 | 방법 |
| --- | --- |
| 예외 없이 정상 실행 | `if self.counter == 5:` 조건을 주석 처리 |
| Checkpoint 저장 주기 변경 | `env.enable_checkpointing(10000)` → 10초 |
| Kafka 연동 | 실시간 데이터 수신 실습 가능 (다음 단계 추천) |

* * *

🧠 주요 개념 정리
-----------

| 용어 | 설명 |
| --- | --- |
| Checkpoint | 장애 발생 시 복구할 수 있게 상태를 저장하는 기능 |
| Restart Strategy | 실패 시 몇 번, 어떤 간격으로 다시 시도할지를 정의 |
| MapFunction | 데이터를 하나씩 처리하는 사용자 정의 함수 |
| from\_collection | 리스트 데이터를 Flink 스트림으로 변환 |
| print() | 처리 결과를 콘솔에 출력 (테스트용) |

* * *

✅ 과제 성공 조건 체크리스트
----------------

*    의도적으로 예외 발생시킴
    
*    Flink가 자동으로 재시도함
    
*    동일 데이터 재출력됨 (Checkpoint 복원 성공)
    
*    `/tmp/flink-checkpoints` 경로에 데이터 생성됨
    
*    Web UI에서 Job 상태 확인 가능
    
*    재시도 횟수 초과 후 Job이 종료됨
    

* * *

🎉 마무리
------

이 실습을 통해 **Flink의 자동 복구 동작**과 **Checkpoint 기반의 상태 저장 원리**를 체험했습니다.

✔ 처음 Flink를 접한 비전공자도  
✔ 데이터를 스트림 형태로 처리하고  
✔ 장애 복구가 어떻게 일어나는지 확인하는 데 성공했습니다!

* * *

이 정리본이 PDF 또는 `.md`, `.docx` 파일로 필요하시다면 말씀만 주세요!  
다음 실습(예: Kafka 연동, 실시간 분석, 상태 저장 연산 등)도 도와드릴게요.

정말 잘하셨습니다 👏 언제든지 다시 찾아주세요!



---
Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)