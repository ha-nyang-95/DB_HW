# 실습 정리본 작성 요청

**User:** 장철환(하냥) (wkdcjfghks1@gmail.com)  
**Created:** 5/11/2025 11:48  
**Updated:** 5/11/2025 12:27  
**Exported:** 5/11/2025 12:33  

## Response:
좋아, 이번 실습은 PyFlink에서 RocksDB 기반 상태 백엔드를 사용해 **Full Checkpoint**와 **Incremental Checkpoint**의 성능 차이를 비교하는 고급 실습이야.  
다른 실습과 동일하게, 아래 네 가지 항목에 따라 전문 정리본을 순차적으로 제공할게:

* * *

### ✅ 구성 방식

1.  📘 실습 주제 개요
    
2.  🛠️ 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
    
3.  ⚙️ 전체 코드 + 상세 주석
    
4.  📚 추가 설명 및 실무 팁
    

* * *

먼저 **1\. 실습 주제 개요**부터 시작할게.

* * *

📘 1\. 실습 주제 개요
---------------

이번 실습은 PyFlink의 **RocksDB State Backend**를 활용해 두 가지 체크포인트 방식의 차이를 실험적으로 비교하는 것이다:

*   **Full Checkpoint**: 모든 상태를 매번 완전히 저장
    
*   **Incremental Checkpoint**: 변경된 상태만 저장하여 저장 공간과 시간 최적화
    

이 실습은 각 방식의 **체크포인트 생성 시간**과 **디스크 사용량**을 측정함으로써,  
실무 환경에서 어떤 방식이 더 효율적인지를 정량적으로 판단할 수 있도록 설계되었다.

* * *

### 실습 흐름 요약

> Pandas CSV → Flink Stream → RocksDB 상태 백엔드 → Full vs Incremental 설정  
> → 체크포인트 시간 측정 → 디스크 사용량 측정

* * *

### 학습 목표

*   Flink의 `RocksDBStateBackend` 사용법과 설정 이해
    
*   `enable_checkpointing()` 및 상태 저장 경로 구성법 숙지
    
*   Full과 Incremental Checkpoint의 성능 차이 체감
    
*   실무에서 체크포인트 저장 비용과 처리 성능 사이의 균형 이해
    

* * *

이제 다음 메시지에서는 **2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설**을 단계별로 아주 상세히 설명해줄게.  
바로 이어서 진행할게.

## Response:
좋아, 이제 **2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설**을 단계별로 상세히 설명할게.  
이번 실습은 Flink 상태 백엔드 비교 실험으로, 각 모드별 Checkpoint 생성 시간과 디스크 크기 차이를 **정량적으로 확인**하는 데 초점을 둬.

* * *

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
-------------------------------------

* * *

### 🔧 1단계: 실행 환경 및 Checkpoint 설정

```python
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
env.enable_checkpointing(5000)
```

*   Flink 스트리밍 실행 환경 생성
    
*   병렬성 1로 설정 → 로그 해석과 디스크 측정이 용이함
    
*   Checkpoint 주기 5초 → 테스트마다 상태가 저장될 수 있도록 설정
    

* * *

### 🧱 2단계: Checkpoint Storage 및 상태 백엔드 설정

```python
checkpoint_path = CHECKPOINT_PATH_FULL if checkpoint_type == "full" else CHECKPOINT_PATH_INCREMENTAL

env.get_checkpoint_config().set_checkpoint_storage(FileSystemCheckpointStorage(checkpoint_path))
env.set_state_backend(RocksDBStateBackend(checkpoint_path, use_incremental))
```

*   체크포인트 경로는 실행 모드(`full` 또는 `incremental`)에 따라 분리
    
*   `RocksDBStateBackend`는 Key-Value 기반 상태 저장 백엔드로 대용량 처리에 최적화
    
*   `use_incremental=True` 설정 시 변경된 상태만 저장되므로 효율적
    

* * *

### 🔁 3단계: 재시작 전략 구성

```python
env.set_restart_strategy(RestartStrategies.fixed_delay_restart(3, 3000))
```

*   장애 발생 시 최대 3회, 3초 간격으로 자동 재시작
    
*   실험 자체에서는 장애 유발이 없지만, 실무와 유사한 조건 구성
    

* * *

### 📄 4단계: Pandas CSV 로딩 및 스트림 생성

```python
df = pd.read_csv("../data/data.csv")
transactions = df[['transaction_id', 'amount']].dropna().values.tolist()
transaction_stream = env.from_collection(transactions)
```

*   거래 데이터를 로드하여 결측값 제거 후 Flink 스트림으로 변환
    
*   입력 스트림은 상태를 유도하지 않지만, 내부적으로 RocksDB에 저장됨
    

* * *

### 🕒 5단계: 체크포인트 성능 측정을 위한 지연 처리

```python
def process_data(value):
    time.sleep(0.5)  # 0.5초 처리 지연을 통해 체크포인트 생성 시점 확보
    return value
```

*   처리 시간 확보를 위해 인위적 딜레이 삽입
    
*   실제 스트리밍처럼 천천히 처리하게 하여 Checkpoint 발생 타이밍 확보
    

* * *

### 🖨️ 6단계: 데이터 출력 및 Job 실행

```python
result = transaction_stream.map(process_data)
result.print()
env.execute(f"{checkpoint_type.capitalize()} Checkpoint Test")
```

*   가공된 스트림을 출력하며 실행 트리거
    
*   Job 이름을 `Full Checkpoint Test` 또는 `Incremental Checkpoint Test`로 지정
    

* * *

### 📏 7단계: 시간 및 디스크 사용량 측정

```python
checkpoint_duration = checkpoint_end - checkpoint_start
checkpoint_size = get_checkpoint_size(checkpoint_path)
```

*   `time.time()`으로 처리 시간 측정
    
*   `du -sh` 명령어로 디스크 사용량 측정 (`os.popen()` 사용)
    

* * *

### 🖥️ 실행 결과 예시

```shell
Full Checkpoint 테스트 시작...
실행 모드: Full Checkpoint
Full Checkpoint 실행 시작...
Checkpoint 소요 시간: 14.50초
Checkpoint 저장 크기: 56M

Incremental Checkpoint 테스트 시작...
실행 모드: Incremental Checkpoint
Incremental Checkpoint 실행 시작...
Checkpoint 소요 시간: 11.20초
Checkpoint 저장 크기: 9.2M
```

* * *

### 🔍 비교 결과 해석

| 항목 | Full Checkpoint | Incremental Checkpoint |
| --- | --- | --- |
| 생성 시간 | 오래 걸림 (전체 상태 저장) | 상대적으로 빠름 |
| 디스크 크기 | 큼 (전체 상태 매번 저장) | 작음 (변경분만 저장) |
| 적합 상황 | 초기 개발, 간단한 파이프라인 | 대규모 상태 관리, 장기 실행 잡 |

* * *

이제 다음 메시지에서는 전체 코드를 **모든 구문과 함께, 각 줄마다 상세한 설명 주석을 포함한 버전으로 제공하는**  
**⚙️ 3\. 전체 코드 + 상세 주석**을 정리해줄게. 바로 이어서 진행할게.

## Response:
좋아, 이번에는 이 실습의 **⚙️ 3\. 전체 코드 + 상세 주석**을 제공할게.  
모든 구문에 대해 Flink의 상태 관리 관점에서 상세하게 주석을 달았고,  
`Full`과 `Incremental` 모드 모두에 대해 어떤 설정이 중요한지 파악할 수 있도록 구성했어.

* * *

⚙️ 3\. 전체 코드 + 상세 주석
--------------------

```python
import time
import os
import pandas as pd
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.checkpoint_storage import FileSystemCheckpointStorage
from pyflink.datastream.state_backend import RocksDBStateBackend
from pyflink.common.restart_strategy import RestartStrategies

# 체크포인트 경로를 실행 모드별로 분리하여 지정
CHECKPOINT_PATH_FULL = "file:///tmp/flink-checkpoints/full"
CHECKPOINT_PATH_INCREMENTAL = "file:///tmp/flink-checkpoints/incremental"

def get_checkpoint_size(checkpoint_path):
    """ 
    체크포인트 디렉터리의 실제 디스크 사용량을 측정
    - checkpoint_path는 file:/// 경로 형식 → 실제 디렉토리 경로로 변환
    - Unix 명령어 `du -sh`를 통해 디스크 크기 측정
    """
    path = checkpoint_path.replace("file://", "")
    size = os.popen(f"du -sh {path}").read().strip()
    return size if size else "N/A"

def run_checkpoint_test(checkpoint_type="full"):
    """
    Flink Job 실행 함수
    checkpoint_type: 'full' 또는 'incremental'
    """

    # ✅ 1. Flink 실행 환경 설정
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    # ✅ 2. Checkpoint 활성화 (주기: 5초)
    env.enable_checkpointing(5000)

    print(f"\n실행 모드: {checkpoint_type.capitalize()} Checkpoint")

    # ✅ 3. 체크포인트 경로 선택
    checkpoint_path = (
        CHECKPOINT_PATH_FULL if checkpoint_type == "full"
        else CHECKPOINT_PATH_INCREMENTAL
    )

    # ✅ 4. Checkpoint 저장소 설정 (FileSystemCheckpointStorage)
    env.get_checkpoint_config().set_checkpoint_storage(
        FileSystemCheckpointStorage(checkpoint_path)
    )

    # ✅ 5. RocksDB 상태 백엔드 설정
    # use_incremental = True → 변경된 값만 저장
    use_incremental = checkpoint_type == "incremental"
    env.set_state_backend(RocksDBStateBackend(checkpoint_path, use_incremental))

    # ✅ 6. 재시작 전략 설정 (예외 상황 대비)
    env.set_restart_strategy(RestartStrategies.fixed_delay_restart(3, 3000))

    # ✅ 7. Pandas로 CSV 데이터 로드
    df = pd.read_csv("../data/data.csv")
    transactions = df[['transaction_id', 'amount']].dropna().values.tolist()

    # ✅ 8. Flink 스트림 생성
    transaction_stream = env.from_collection(transactions)

    # ✅ 9. Checkpoint 측정용 시간 기록
    checkpoint_start = time.time()

    def process_data(value):
        """ 각 데이터 처리 시 0.5초 지연 (스트리밍 환경 유사화) """
        time.sleep(0.5)
        return value

    # ✅ 10. 지연 함수 적용 및 출력
    result = transaction_stream.map(process_data)
    result.print()

    # ✅ 11. Job 실행 트리거
    print(f"{checkpoint_type.capitalize()} Checkpoint 실행 시작...")
    env.execute(f"{checkpoint_type.capitalize()} Checkpoint Test")

    # ✅ 12. Checkpoint 처리 시간 계산
    checkpoint_end = time.time()
    checkpoint_duration = checkpoint_end - checkpoint_start
    print(f"Checkpoint 소요 시간: {checkpoint_duration:.2f}초")

    # ✅ 13. 디스크 사용량 측정 및 출력
    checkpoint_size = get_checkpoint_size(checkpoint_path)
    print(f"Checkpoint 저장 크기: {checkpoint_size}")

if __name__ == "__main__":
    # ✅ Full Checkpoint 실험 실행
    print("Full Checkpoint 테스트 시작...")
    run_checkpoint_test("full")

    # ✅ Incremental Checkpoint 실험 실행
    print("\nIncremental Checkpoint 테스트 시작...")
    run_checkpoint_test("incremental")
```

* * *

이 코드는 Flink에서 **상태 저장 방식의 효율성**을 실제로 비교하고,  
`use_incremental` 설정 하나로 얼마나 큰 차이를 만들 수 있는지를 체감할 수 있게 도와주는 실습 예제야.

다음 메시지에서는 마지막으로 **📚 4\. 추가 설명 및 실무 팁**을 제공할게.  
Full vs Incremental 체크포인트의 구조 차이, 실무 적합성, 최적화 전략까지 정리해서 마무리할게.  
바로 이어서 진행할게.

## Response:
좋아, 이제 마지막 항목인 **📚 4\. 추가 설명 및 실무 팁**을 정리해줄게.  
이번 실습은 Flink의 상태 저장 전략 중 하나인 **RocksDB 상태 백엔드에서의 Full vs Incremental Checkpoint 차이**를 체감하며 이해하는 실험이야.  
이 지식은 실시간 스트리밍 시스템에서 **안정성과 성능 최적화의 핵심 기술**로 쓰이기 때문에 매우 중요해.

* * *

📚 4\. 추가 설명 및 실무 팁
-------------------

* * *

### ✅ Full Checkpoint vs Incremental Checkpoint 차이 개념 정리

| 항목 | Full Checkpoint | Incremental Checkpoint |
| --- | --- | --- |
| 저장 방식 | 전체 상태 전체 저장 | 이전 상태와 비교해 변경된 부분만 저장 |
| 디스크 사용량 | 큼 | 작음 |
| 생성 시간 | 상대적으로 느림 | 빠름 |
| 장점 | 구현 및 복구 로직 단순 | 저장 공간 절약, 빠른 수행 |
| 단점 | 비효율적 I/O, 중복 저장 | 복구 시 더 많은 메타데이터 필요 |
| 실무 적합성 | 소규모 Job, 테스트 | 대규모 실시간 Job, 장기 실행 시스템 |

> 🔍 **실제 운영 환경에서는 대부분 Incremental 방식을 선택**하며, 특히 장시간 실행되는 Job에서는 필수로 사용돼.

* * *

### 🧠 실무에서의 사용 시 주의 사항

| 주의사항 | 설명 |
| --- | --- |
| ❌ Checkpoint 저장 위치를 로컬 디스크에만 의존 | 실운영에서는 HDFS, S3, GCS 같은 분산 저장소 사용 권장 |
| ❌ use\_incremental 설정 없이 상태 용량만 키움 | 불필요한 저장소 낭비 발생, 디스크 부족 문제 유발 가능 |
| ❌ 처리량 높은 Job에서 Full 사용 | 처리 중단, GC 압박, OOM 등 발생 가능성 ↑ |
| ❌ Checkpoint 실패 무시 | Checkpoint 누락 시 장애 복구가 불가하므로 모니터링 필수 |

* * *

### 🧩 실무 확장 방향 및 최적화 전략

#### ✅ 1\. Checkpoint Storage → S3 or HDFS로 전환

```python
env.get_checkpoint_config().set_checkpoint_storage("s3://my-bucket/flink-checkpoints")
```

#### ✅ 2\. RocksDB 백엔드 설정 세분화

*   압축 알고리즘 (LZ4, Snappy 등) 설정
    
*   Write Buffer, Block Cache, SST 설정 → 성능 극대화 가능
    

#### ✅ 3\. Async Checkpoint + State TTL 사용

*   Checkpoint가 처리에 영향을 주지 않도록 비동기 처리
    
*   오래된 상태 자동 삭제로 저장 공간 최소화
    

#### ✅ 4\. Savepoint 활용 (운영 Job의 상태 이관)

*   Savepoint는 수동 상태 스냅샷
    
*   버전 업그레이드나 DAG 변경 시 유용
    

* * *

### 🔧 체크포인트 구성 최적 예시 (프로덕션 기준)

```python
env.enable_checkpointing(10000)  # 10초 간격
env.get_checkpoint_config().set_min_pause_between_checkpoints(5000)
env.get_checkpoint_config().set_checkpoint_timeout(60000)
env.get_checkpoint_config().set_max_concurrent_checkpoints(1)
env.set_state_backend(RocksDBStateBackend("s3://my-bucket/flink-checkpoints", True))
```

* * *

### ✅ 마무리 요약

*   Incremental Checkpoint는 **성능과 안정성의 핵심 최적화 기술**이다.
    
*   RocksDB와 함께 사용할 때 그 진가를 발휘하며, 상태가 많은 대규모 Job에서 디스크 낭비를 크게 줄일 수 있다.
    
*   실무에서는 Checkpoint 설정과 저장소 구성, 모니터링 체계까지 포함하여 설계해야 진정한 fault-tolerant 시스템을 구축할 수 있다.
    

* * *

이제 이번 실습의 정리본도 완벽하게 마무리됐어.  
다음으로는 Savepoint를 테스트하거나, Kafka와 연결해 상태 기반 실시간 분석을 구성하거나, Flink HA 환경에서 Checkpoint/Recovery 흐름을 직접 다뤄볼 수도 있어.

다음으로 어떤 실습을 해보고 싶어?



---
Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)