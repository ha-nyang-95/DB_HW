# Flink 실시간 거래 감지

🧾 PyFlink 이상 거래 탐지 과제 완벽 복습 노트 (비전공자용)
=======================================

* * *

1\. ✅ 과제 목적
-----------

### ✔️ 목표:

*   **금융 거래 데이터를 실시간으로 분석**
    
*   **거래 금액이 8000.0을 초과하는 이상 거래를 감지**
    
*   **실시간 처리 후 파일로 저장**
    

* * *

2\. ✅ 실행 흐름 요약
--------------

| 단계 | 설명 |
| --- | --- |
| 1단계 | Flink 실행 환경 만들기 |
| 2단계 | Pandas로 CSV 파일 읽고 필요한 값만 추출 |
| 3단계 | 리스트 데이터를 Flink 스트림으로 변환 |
| 4단계 | 거래금액이 8000.0 이상인 데이터만 필터링 |
| 5단계 | 데이터를 문자열로 변환 (파일 저장을 위해) |
| 6단계 | 파일로 저장할 수 있도록 FileSink 설정 |
| 7단계 | Flink 실행 (`env.execute()`) |

* * *

3\. ✅ 코드 전체 (설명 포함)
-------------------

```python
import pandas as pd
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors import FileSink
from pyflink.common.serialization import Encoder
from pyflink.java_gateway import get_gateway

# 8000 이상이면 이상 거래로 판단
THRESHOLD = 8000.0

def main():
    # 1. Flink 실행 환경 생성
    env = StreamExecutionEnvironment.get_execution_environment()
    
    # 💡 병렬성 설정: 출력이 섞이지 않도록 병렬성을 1로 고정
    env.set_parallelism(1)

    # 2. CSV 불러오기 (판다스로 데이터 처리)
    df = pd.read_csv("../data/data.csv")  # 상대 경로는 실제 환경에 따라 조정
    transactions = df[["transaction_id", "customer_id", "amount"]].dropna().values.tolist()

    # 3. 데이터 스트림 생성 (리스트 → Flink 스트림)
    transaction_stream = env.from_collection(
        transactions,
        type_info=Types.TUPLE([Types.STRING(), Types.STRING(), Types.FLOAT()])
    )

    # 4. 이상 거래 필터링
    suspicious_transactions = transaction_stream.filter(lambda x: x[2] > THRESHOLD)

    # 5. 문자열 변환 (파일로 저장할 수 있도록)
    formatted_stream = suspicious_transactions.map(
        lambda x: f"{x[0]}, {x[1]}, {x[2]}",
        output_type=Types.STRING()
    )

    # 6. 파일 저장 준비: Java 인코더 사용
    gateway = get_gateway()
    j_string_encoder = gateway.jvm.org.apache.flink.api.common.serialization.SimpleStringEncoder()
    encoder = Encoder(j_string_encoder)

    # 파일 싱크 정의
    file_sink = FileSink.for_row_format(
        "./output/suspicious_transactions",
        encoder
    ).build()

    # 7. 싱크 연결 & 실행
    formatted_stream.sink_to(file_sink)
    env.execute("Anomaly Detection in Transactions with File Sink")

if __name__ == "__main__":
    main()
```

* * *

4\. ✅ 실행 결과 예시
--------------

### 📄 출력 경로:

```
./output/suspicious_transactions/part-0-00000
```

### 📊 출력 내용 (실제 실행 결과):

```
1002, C012, 9582.150390625
1005, C014, 9807.0498046875
1009, C015, 9269.9599609375
1011, C007, 9612.3603515625
1018, C005, 9559.7099609375
1031, C008, 8906.3896484375
1036, C012, 9622.7998046875
1041, C002, 9822.3701171875
1042, C015, 9597.1796875
```

> 🔍 모두 `amount > 8000.0`을 만족하는 이상 거래입니다.

* * *

5\. ✅ 주요 개념 이해 (비전공자용)
----------------------

| 용어 | 설명 | 예시 |
| --- | --- | --- |
| **Flink** | 실시간으로 데이터를 처리하는 엔진 | 거래가 발생하자마자 바로 필터링 |
| **StreamExecutionEnvironment** | Flink 실행의 시작점 | 작업 설계도 |
| **set\_parallelism(1)** | 병렬 작업 수를 1로 제한 | 결과가 섞이지 않도록 설정 |
| **from\_collection()** | 리스트 → 스트림 변환 | Pandas로 불러온 데이터를 Flink에서 사용 |
| **filter()** | 조건에 맞는 것만 남김 | 금액이 8000 초과인 거래만 선택 |
| **map()** | 형식 변환 | 숫자 → 문자열 변환 (저장용) |
| **FileSink** | 스트림 데이터를 파일에 저장 | 지정된 폴더에 결과 저장 |
| **Encoder** | 데이터를 파일에 어떻게 저장할지 정의 | SimpleStringEncoder 사용 (Java) |

* * *

6\. ✅ 과제에서 주의할 점
----------------

*   ✅ **병렬성 설정 필수** (`env.set_parallelism(1)`)
    
*   ✅ **파일 저장 시 Java Encoder 사용** (Python Encoder는 내부적으로 Java 연동)
    
*   ✅ **`formatted_stream.sink_to(file_sink)`를 해야 실제로 저장됨**
    
*   ✅ **`env.execute()`로 Flink 작업 실행**
    

* * *

7\. 📚 혼자 공부할 때 참고할 자료
----------------------

| 자료 | 추천 이유 |
| --- | --- |
| [PyFlink 공식 문서](https://nightlies.apache.org/flink/flink-docs-release-1.20/docs/dev/python/datastream/) | 최신 PyFlink 기능 정리 |
| Flink 한국어 설명 블로그 | 개념 이해에 도움 |
| Pandas 사용법 정리 | CSV 전처리 학습용 |
| 유튜브 - Flink 초보자 강의 | 개념 이해 시각화 |

* * *

8\. 📌 마무리 체크리스트
----------------

*    Pandas로 CSV 불러옴
    
*    결측치 제거 및 리스트 변환
    
*    from\_collection으로 스트림 생성
    
*    filter로 이상 거래만 선택
    
*    map으로 문자열 변환
    
*    Encoder 설정
    
*    FileSink로 저장
    
*    병렬성 1로 설정
    
*    Flink 실행(`env.execute()`)
    

* * *

필요하다면 아래도 추가로 정리해드릴 수 있어요:

*   `.csv` 샘플 생성 방법
    
*   VSCode에서 실행 시 주의할 점
    
*   PyFlink + Kafka 연결 (실시간 확장용)
    
*   PyFlink로 REST API 연동하는 방법 등
    

추가로 궁금한 게 있으면 언제든지 질문 주세요! 😊



---
Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)