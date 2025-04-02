# %%
"""
Kafka 컨슈머를 활용하여 `output-topic`의 메시지를 소비하고 출력하는 실습입니다.

TODO:
1. kafka-python 라이브러리를 사용하여 KafkaConsumer를 생성합니다.
2. `output-topic`을 구독하고, 메시지를 소비합니다.
3. 소비한 메시지를 출력하여 변환된 데이터가 정상적으로 수신되었는지 확인합니다.
"""

from kafka import KafkaConsumer

# %%
# TODO 1: KafkaConsumer를 생성하세요.
consumer = KafkaConsumer(
    "output-topic",  # 구독할 토픽 설정
    bootstrap_servers='localhost:9092',  # Kafka 브로커 주소 설정
    auto_offset_reset='earliest',  # 오프셋 초기화 방식 설정
    enable_auto_commit=True,  # 자동 오프셋 커밋 여부 설정
    group_id='final-check-group'  # 컨슈머 그룹 ID 설정
)

# %%
# TODO 2: `output-topic`에서 메시지를 소비하고 출력하세요.
for message in consumer:  # 메시지를 소비하는 컨슈머 객체
    print(f"Consumed from output-topic: {message.value.decode('utf-8')}")


