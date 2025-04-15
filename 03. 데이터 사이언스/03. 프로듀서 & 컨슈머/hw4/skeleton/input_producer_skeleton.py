# %%
"""
Kafka 프로듀서를 활용하여 `input-topic`에 테스트 메시지를 전송하는 실습입니다.

TODO:
1. kafka-python 라이브러리를 사용하여 KafkaAdminClient를 생성합니다.
2. 기존 `input-topic`과 `output-topic`이 존재하면 삭제한 후, 새로 생성합니다.
3. KafkaProducer를 사용하여 `input-topic`에 테스트 메시지를 전송합니다.
"""

import time
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

# %%
# TODO 1: KafkaAdminClient를 생성하세요.
admin_client = KafkaAdminClient(
    bootstrap_servers='localhost:9092',  # Kafka 브로커 주소 설정
    client_id='test-admin'  # 클라이언트 ID 설정
)

input_topic = "input-topic"
output_topic = "output-topic"

# %%
# TODO 2: 기존 `input-topic`과 `output-topic`을 삭제한 후, 2초 대기 후 새로 생성하세요.
existing_topics = admin_client.list_topics()  # 기존 토픽 목록을 가져오는 함수
for topic in [input_topic, output_topic]:
    if topic in existing_topics:
        admin_client.delete_topics([topic])  # 특정 토픽을 삭제하는 함수
        print(f"기존 토픽 '{topic}' 삭제 완료")
        time.sleep(2)  # 삭제 후 2초 대기

admin_client.create_topics([
    NewTopic(name=input_topic, num_partitions=1, replication_factor=1),
    NewTopic(name=output_topic, num_partitions=1, replication_factor=1)
])  # 새 토픽 생성
print(f"새로운 토픽 '{input_topic}' 및 '{output_topic}' 생성 완료")

admin_client.close()  # AdminClient 연결을 닫는 함수

# %%
# TODO 3: KafkaProducer를 생성하세요.
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',  # Kafka 브로커 주소 설정
    value_serializer=lambda v: v.encode('utf-8')  # 메시지 직렬화 방식 설정
)

# %%
# TODO 4: `input-topic`에 테스트 메시지를 전송하세요.
test_messages = ["hello", "world", "kafka", "streaming", "data"]
for message in test_messages:
    producer.send(input_topic, value=message)  # 프로듀서에서 메시지를 보내는 함수
    print(f"Sent: {message}")


