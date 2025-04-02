# %%
"""
Kafka 프로듀서를 활용하여 특정 키 값을 가진 메시지가 동일한 파티션으로 전송되는지 확인하는 실습입니다.

TODO:
1. kafka-python 라이브러리를 사용하여 KafkaAdminClient를 생성합니다.
2. 기존 test-topic이 존재하면 삭제한 후, 파티션 개수가 3개인 새 토픽을 생성합니다.
3. KafkaProducer를 사용하여 특정 키 값을 가진 메시지를 여러 번 전송합니다.
4. 특정 키를 가진 메시지가 항상 같은 파티션으로 들어가는지 확인합니다.
"""

import time
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

# %%
# TODO 1: KafkaAdminClient를 생성하세요.
admin_client = KafkaAdminClient(
    bootstrap_servers="localhost:9092",  # Kafka 브로커 주소 설정
    client_id='test-admin'  # 클라이언트 ID 설정
)

topic_name = "test-topic"

# %%
# TODO 2: 기존 test-topic을 삭제한 후, 2초 대기 후 새로 생성하세요.
existing_topics = admin_client.list_topics()  # 기존 토픽 목록을 가져오는 함수
if topic_name in existing_topics:
    admin_client.delete_topics([topic_name])  # 특정 토픽을 삭제하는 함수
    print(f"기존 토픽 '{topic_name}' 삭제 완료")
    time.sleep(2)  # 삭제 후 2초 대기

new_topic = NewTopic(name=topic_name, num_partitions=3, replication_factor=1)
admin_client.create_topics([new_topic])  # 새로운 토픽을 생성하는 함수
print(f"새로운 토픽 '{topic_name}' 생성 완료")

admin_client.close()  # AdminClient 연결을 닫는 함수

# %%
# TODO 3: KafkaProducer를 생성하세요.
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',  # Kafka 브로커 주소 설정
    key_serializer=str.encode,  # 키 직렬화 설정
    value_serializer=str.encode  # 값 직렬화 설정
)

# %%
# TODO 4: 특정 키 값을 가진 메시지를 여러 개 전송하세요.
keys = ["key1", "key2", "key3"]
for i in range(10):
    key = keys[i % len(keys)]
    value = f"message-{i}"
    producer.send(topic_name, key=key, value=value)  # 프로듀서에서 메시지를 보내는 함수
    print(f"Sent: {value} with key: {key}")


