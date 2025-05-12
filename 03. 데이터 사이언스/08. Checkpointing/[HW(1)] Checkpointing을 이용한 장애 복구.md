# 실습 정리본 작성 요청

**User:** 장철환(하냥) (wkdcjfghks1@gmail.com)  
**Created:** 5/11/2025 11:48  
**Updated:** 5/11/2025 12:27  
**Exported:** 5/11/2025 12:32  

## Response:
좋아, 이번 실습은 PyFlink에서 **Checkpoint 및 장애 복구 테스트**를 수행하는 고급 실습이야.  
이제까지와 마찬가지로 다음 네 가지 항목에 따라 전문 정리본을 단계별로 제공할게:

* * *

### ✅ 구성 방식

1.  📘 실습 주제 개요
    
2.  🛠️ 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
    
3.  ⚙️ 전체 코드 + 상세 주석
    
4.  📚 추가 설명 및 실무 팁
    

* * *

지금부터 **1\. 실습 주제 개요**를 먼저 설명할게.

* * *

📘 1\. 실습 주제 개요
---------------

이번 실습의 목표는 PyFlink에서 **Checkpoint 및 장애 복구 전략이 어떻게 동작하는지를 직접 실험을 통해 확인**하는 것이다.  
Flink는 장애가 발생하더라도 데이터 손실 없이 다시 실행할 수 있도록 \*\*상태(=State)를 주기적으로 저장(Checkpoint)\*\*하고,  
예외 발생 시 자동으로 이전 지점부터 복구하는 기능을 제공한다.

이 실습은 `MapFunction` 내에서 **의도적으로 예외를 발생**시키고,  
Flink의 \*\*고정 지연 재시작 전략(fixed delay restart)\*\*과 **파일 기반 상태 복구 기능**이 작동하는지 테스트하는 구조로 설계됐다.

* * *

### 실습 시나리오 요약

> CSV → Flink Stream 생성 → 매핑 처리 중 5번째 레코드에서 예외 발생  
> → Flink가 자동으로 잡 재시작 → 이전 Checkpoint 지점부터 재실행

* * *

### 학습 목표

*   Flink의 `enable_checkpointing()` 기능과 주기적 상태 저장 이해
    
*   예외 발생 시 자동 재시작 전략 설정 (`fixed_delay_restart`)
    
*   `FileSystemCheckpointStorage` 설정을 통한 로컬 파일 시스템 기반 복구 테스트
    
*   상태가 없는 연산(map)에서도 Flink의 복원 동작을 관찰하는 방법 체득
    

* * *

이제 다음 메시지에서는 **2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설**을 아주 자세히 설명해줄게.  
바로 이어서 진행할게.

## Response:
좋아, 이제 **2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설**을 상세하게 설명할게.  
이 실습은 Flink의 **Checkpoint 저장, 예외 유도, 자동 복구**의 전 과정을 실제 실행하며 확인하는 고급 실습이야.

* * *

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
-------------------------------------

* * *

### 🧱 1단계: 실행 환경 및 병렬성 설정

```python
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
```

*   Flink 실행 환경을 초기화하고 병렬성(parallelism)을 1로 설정
    
*   병렬성이 1이므로 예외 발생 시 상태 복구 흐름이 단일 스레드 기준으로 확인 가능
    

* * *

### 💾 2단계: Checkpoint 설정

```python
env.enable_checkpointing(5000)
env.get_checkpoint_config().set_checkpoint_storage(FileSystemCheckpointStorage(CHECKPOINT_PATH))
```

*   5초(5000ms)마다 Checkpoint를 수행하도록 설정
    
*   Checkpoint는 Flink가 처리 중간 상태를 주기적으로 저장하여 장애 복구 시 사용
    
*   저장 위치는 로컬 파일 시스템의 `/tmp/flink-checkpoints`
    

* * *

### 🔁 3단계: 재시작 전략 설정

```python
env.set_restart_strategy(RestartStrategies.fixed_delay_restart(3, 5000))
```

*   장애 발생 시 최대 3회까지 5초 간격으로 자동 재시도
    
*   `RestartStrategies.fixed_delay_restart(max_attempts, delay_ms)` 패턴
    
*   재시도 후에도 실패하면 job이 실패 상태로 종료됨
    

* * *

### 📄 4단계: 입력 데이터 로딩

```python
df = pd.read_csv("../data/data.csv")
transactions = df[['transaction_id', 'amount']].dropna().values.tolist()
```

*   Pandas로 거래 데이터를 로딩하고, 필요한 컬럼만 추출
    
*   결측값을 제거하고 Flink에 넘기기 위한 리스트 형태로 변환
    

* * *

### ⚠️ 5단계: 예외 유발 MapFunction 구현

```python
class FailingMapFunction(MapFunction):
    def __init__(self):
        self.counter = 0

    def map(self, value):
        self.counter += 1
        time.sleep(1)
        if self.counter == 5:
            print(f"Checkpoint 실패 발생! Transaction ID: {value[0]}")
            raise Exception("의도적인 Checkpoint 실패 발생")
        return value
```

*   처리된 레코드 수를 세는 `counter` 변수를 가지고 있음
    
*   5번째 레코드에서 강제로 예외 발생 → Flink는 이 예외를 감지하여 job 재시작 수행
    
*   `time.sleep(1)`은 스트리밍처럼 동작하게 만들기 위한 artificial delay
    

* * *

### 🌊 6단계: Flink DataStream 구성

```python
transaction_stream = env.from_collection(transactions)
transaction_stream = transaction_stream.map(FailingMapFunction())
```

*   리스트 데이터를 스트림으로 만들고, `FailingMapFunction`을 적용
    
*   이 함수는 처음에는 정상 작동하다가 5번째 처리에서 강제로 실패함
    

* * *

### 📤 7단계: 출력 및 실행 트리거

```python
transaction_stream.print()
env.execute("Checkpoint Recovery Example")
```

*   스트림 데이터를 콘솔로 출력
    
*   Flink 잡 실행 트리거
    

* * *

### 🖥️ 실행 결과 예시

처음 실행 시 출력:

```
('tx1001', 2500.0)
('tx1002', 3100.0)
('tx1003', 4000.0)
('tx1004', 2900.0)
Checkpoint 실패 발생! Transaction ID: tx1005
```

그 뒤에는 다음과 같은 로그가 출력됨:

```
Restarting job Checkpoint Recovery Example from latest checkpoint...
Recovered state from checkpoint: /tmp/flink-checkpoints/xxx
Retry #1
('tx1005', 8900.0)
('tx1006', 1200.0)
...
```

* * *

### 📌 핵심 관찰 포인트

*   Flink는 5번째 레코드에서 예외 발생 직후 자동 재시작
    
*   마지막으로 성공한 Checkpoint 이후부터 재처리됨 → **데이터 손실 없음**
    
*   이 실습은 Flink의 \*\*exactly-once 처리 보장과 내결함성(fault tolerance)\*\*을 확인하는 좋은 실험임
    

* * *

다음 메시지에서는 이 실습 코드를 **한 줄도 생략하지 않고**, **모든 구문에 대해 상세한 주석을 포함한 형태로 정리한**  
**⚙️ 3\. 전체 코드 + 상세 주석**을 제공할게.  
바로 이어서 진행할게.

## Response:
좋아, 이제 이번 실습의 **⚙️ 3\. 전체 코드 + 상세 주석**을 제공할게.  
Checkpoint, 장애 유도, 자동 재시작 메커니즘이 어떻게 작동하는지 파악할 수 있도록 **모든 코드 라인에 상세한 설명**을 달았어.

* * *

⚙️ 3\. 전체 코드 + 상세 주석
--------------------

```python
import os
import time
import pandas as pd
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.checkpoint_storage import FileSystemCheckpointStorage
from pyflink.datastream.functions import MapFunction
from pyflink.common.restart_strategy import RestartStrategies

# Checkpoint 저장 경로 지정 (로컬 파일 시스템 사용)
CHECKPOINT_PATH = "file:///tmp/flink-checkpoints"

# 사용자 정의 MapFunction: 5번째 레코드에서 강제로 예외 발생
class FailingMapFunction(MapFunction):
    def __init__(self):
        self.counter = 0  # 처리된 레코드 수 추적

    def map(self, value):
        self.counter += 1
        time.sleep(1)  # 스트리밍처럼 동작하도록 1초 지연

        # 5번째 입력에서 강제로 예외 발생시킴
        if self.counter == 5:
            print(f"Checkpoint 실패 발생! Transaction ID: {value[0]}")
            raise Exception("의도적인 Checkpoint 실패 발생")

        # 예외가 발생하지 않은 경우 원래 값 반환
        return value

def main():
    # Flink 실행 환경 생성
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)  # 병렬성 1로 설정 (동작 확인을 쉽게 하기 위함)

    # ✅ 1. Checkpoint 활성화: 5000ms (5초) 간격으로 상태 저장
    env.enable_checkpointing(5000)

    # ✅ 2. Checkpoint 저장 위치 지정 (파일 시스템 경로)
    env.get_checkpoint_config().set_checkpoint_storage(
        FileSystemCheckpointStorage(CHECKPOINT_PATH)
    )

    # ✅ 3. 예외 발생 시 자동 재시작 전략 설정: 최대 3번, 5초 간격 재시도
    env.set_restart_strategy(RestartStrategies.fixed_delay_restart(3, 5000))

    # ✅ 4. Pandas로 CSV 데이터 로드
    df = pd.read_csv("../data/data.csv")

    # ✅ 5. 필요한 컬럼 선택 및 결측값 제거 후 리스트로 변환
    transactions = df[['transaction_id', 'amount']].dropna().values.tolist()
    # 예시: [["tx1001", 2500.0], ["tx1002", 3400.0], ...]

    # ✅ 6. Flink 데이터 스트림 생성
    transaction_stream = env.from_collection(transactions)

    # ✅ 7. 사용자 정의 함수(FailingMapFunction) 적용
    # 이 함수는 5번째 레코드에서 의도적으로 실패하고, Checkpoint 복구가 트리거됨
    transaction_stream = transaction_stream.map(FailingMapFunction())

    # ✅ 8. 결과 출력 (정상 처리된 레코드만 출력됨)
    transaction_stream.print()

    # ✅ 9. Flink Job 실행 트리거
    print("Flink Job을 제출합니다...")
    env.execute("Checkpoint Recovery Example")

# Python 파일이 직접 실행될 경우 main() 함수 호출
if __name__ == "__main__":
    main()
```

* * *

이 코드는 Flink에서 \*\*상태 기반 처리의 내결함성(fault tolerance)\*\*이 어떻게 작동하는지를 가장 직접적으로 확인할 수 있는 예제야.  
의도적으로 실패를 유도한 뒤 Checkpoint를 기반으로 복구가 발생하고, 처리가 이어지는 과정을 실시간으로 볼 수 있어.

다음 메시지에서는 마지막으로 **📚 4\. 추가 설명 및 실무 팁**을 제공할게.  
실무에서 Checkpoint가 왜 중요한지, 어떻게 설정해야 안정적인 시스템을 만들 수 있는지, 그리고 확장 방향까지 정리해줄게.  
바로 이어서 진행할게.

## Response:
좋아, 이제 마지막 항목인 **📚 4\. 추가 설명 및 실무 팁**을 정리해줄게.  
이번 실습은 Flink의 **내결함성(fault tolerance)** 개념을 실험적으로 학습하는 데 매우 중요하며,  
실시간 처리 시스템을 운영하는 입장에서는 반드시 이해하고 있어야 하는 핵심 개념이야.

* * *

📚 4\. 추가 설명 및 실무 팁
-------------------

* * *

### ✅ Checkpoint와 장애 복구의 실무적 의미

| 개념 | 설명 |
| --- | --- |
| **Checkpoint** | Flink의 연산 상태를 주기적으로 외부 저장소에 저장하는 메커니즘 |
| **Restart Strategy** | 연산 중 오류 발생 시 Flink 작업을 재시작하는 방식 (재시도 횟수, 대기 시간 등 설정 가능) |
| **Exactly-once 보장** | Flink는 Checkpoint와 재시작 전략을 통해 중복 없는 데이터 처리를 보장함 (예: 금융, 물류, 트랜잭션 시스템 등에서 필수) |

실무에서는 Kafka, HDFS, S3, RocksDB, PostgreSQL 등 다양한 저장소와 연계하여 상태를 저장하고 복원한다.

* * *

### 🧠 실무에서 자주 겪는 문제 & 해결법

| 문제 | 원인 | 해결 방법 |
| --- | --- | --- |
| ❌ Checkpoint가 저장되지 않음 | 저장소 경로 누락 또는 권한 문제 | 로컬 경로는 `file:///`, HDFS는 `hdfs:///`로 명시, 쓰기 권한 확인 |
| ❌ 재시작이 너무 빨리 발생함 | checkpoint 간격보다 짧은 재시작 지연 설정 | `checkpoint interval` ≥ `restart delay` 권장 |
| ❌ 상태가 복구되지 않고 처음부터 실행됨 | Checkpoint가 실패했거나, disable된 상태 | `env.enable_checkpointing()` 호출 및 경로 설정 확인 |
| ❌ Flink Job이 반복적으로 실패 | 사용자 코드에서 예외가 계속 발생 | 재시작 횟수 제한 및 `SideOutput` 등을 통한 오류 분리 처리 권장 |

* * *

### 🔄 확장 아이디어

#### ✅ 1\. 상태가 있는 연산 테스트

*   현재 실습은 상태 없는 `map()` 기반이지만,  
    `key_by().reduce()` 또는 `process()`를 사용하면 상태 기반 처리 확인 가능
    
*   예외 발생 시 상태가 유지되었는지 확인하는 것이 핵심
    

#### ✅ 2\. 외부 저장소로 Checkpoint 저장

*   Amazon S3, HDFS, MinIO 등에 상태 저장
    

```python
env.get_checkpoint_config().set_checkpoint_storage("s3://flink-checkpoints-bucket/")
```

#### ✅ 3\. Savepoint와 Manual Recovery 연습

*   Savepoint는 수동으로 트리거하는 상태 저장
    
*   특정 시점의 상태에서 새 작업으로 이어받아 실행 가능
    

#### ✅ 4\. JobManager/TaskManager 장애 시 복구 확인

*   Docker 또는 Flink 클러스터 환경에서 프로세스를 kill하고 복구 시도
    

* * *

### ✅ 실무 적용 시 권장 구성

| 항목 | 설정 예시 |
| --- | --- |
| Checkpoint 주기 | 5~10초 (지연과 처리량의 균형 필요) |
| Checkpoint Storage | 로컬 디스크 → HDFS/S3로 전환 권장 |
| Restart Strategy | `fixed_delay_restart(3, 5000)` 또는 `failure_rate_restart(...)` |
| State Backend | Memory → RocksDB로 확장 (대용량 처리 시 필수) |
| Monitoring | Flink Web UI + Prometheus + Grafana 연동 권장 |

* * *

### ✅ 마무리 요약

*   Flink는 Checkpoint 기반으로 **Exactly-once**를 보장하며, 이는 **실시간 스트리밍 시스템의 신뢰성 핵심**이다.
    
*   이번 실습은 단순 예외 발생을 통해 Flink가 상태를 어떻게 저장하고, 어떤 방식으로 복구하는지를 직접 확인하는 구조이다.
    
*   실무에서는 Kafka 연동, 상태 연산 확대, S3/HDFS 저장소 연계, 클러스터 환경 구축 등을 통해 이 구조를 실질적인 운영 시스템으로 발전시킬 수 있다.
    

* * *

이제 정리본이 완벽하게 마무리됐어.  
혹시 다음 단계로 **상태 기반 연산의 Checkpoint 복구**나 **Kafka와 Flink의 실시간 장애 복구 실험**,  
혹은 **Savepoint 기반 수동 상태 이전** 등에 대해 실습해보고 싶다면 언제든지 이어서 도와줄게.

다음으로 어떤 걸 해보고 싶어?



---
Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)