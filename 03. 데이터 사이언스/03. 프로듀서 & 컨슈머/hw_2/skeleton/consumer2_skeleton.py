# %%
"""
Kafka 컨슈머를 활용하여 특정 키 값을 가진 메시지가 동일한 파티션에서 소비되는지 확인하는 실습입니다.

TODO:
1. kafka-python 라이브러리를 사용하여 KafkaConsumer를 생성합니다.
2. test-topic을 구독하고, 메시지를 소비합니다.
3. 메시지가 들어온 파티션 정보를 확인하여 동일한 키가 동일한 파티션으로 들어가는지 검증합니다.
"""

from kafka import KafkaConsumer

# %%
# TODO 1: KafkaConsumer를 생성하세요.
consumer = KafkaConsumer(
    "test-topic",
    bootstrap_servers='localhost:9092',  # Kafka 브로커 주소 설정
    auto_offset_reset='earliest',  # 오프셋 초기화 방식 설정
    enable_auto_commit=True,  # 자동 오프셋 커밋 여부 설정
    group_id='my-group-2'  # 컨슈머 그룹 ID 설정
)

# %%
# TODO 2: 메시지를 지속적으로 소비하고, 들어온 파티션 정보를 출력하세요.
for message in consumer:  # 메시지를 소비하는 컨슈머 객체
    print(f"Received: {message.value.decode('utf-8')}, Key: {message.key.decode('utf-8')}, Partition: {message.partition}")


