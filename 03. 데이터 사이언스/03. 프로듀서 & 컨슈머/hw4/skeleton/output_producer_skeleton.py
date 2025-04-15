# %%
"""
Kafka 컨슈머를 활용하여 `input-topic`의 메시지를 변환 후 `output-topic`으로 전송하는 실습입니다.

TODO:
1. kafka-python 라이브러리를 사용하여 KafkaConsumer를 생성합니다.
2. KafkaProducer를 생성하여 변환된 메시지를 `output-topic`으로 전송합니다.
3. `input-topic`에서 메시지를 소비한 후 특정 변환 로직을 적용하여 `output-topic`으로 다시 송신합니다.
"""

from kafka import KafkaConsumer, KafkaProducer

# %%
# TODO 1: KafkaConsumer를 생성하세요.
consumer = KafkaConsumer(
    "input-topic",  # 구독할 토픽 설정
    bootstrap_servers='localhost:9092',  # Kafka 브로커 주소 설정
    auto_offset_reset='earliest',  # 오프셋 초기화 방식 설정
    enable_auto_commit=True,  # 자동 오프셋 커밋 여부 설정
    group_id='transform-group',  # 컨슈머 그룹 ID 설정
)

# %%
# TODO 2: KafkaProducer를 생성하세요.
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',  # Kafka 브로커 주소 설정
    value_serializer=lambda v: v.encode('utf-8')  # 메시지 직렬화 방식 설정
)

# %%
# TODO 3: `input-topic`의 메시지를 변환 후 `output-topic`으로 전송하세요.
for message in consumer:  # 메시지를 소비하는 컨슈머 객체
    transformed_message = message.value.decode('utf-8').upper()  # 메시지 변환 (대문자로 변경)
    producer.send("output-topic", value=transformed_message)  # 변환된 메시지를 프로듀서로 전송하는 함수
    print(f"Transformed and Sent: {transformed_message}")


