# Apache Flink 1.20 설치 및 WSL2 네트워크 설정 가이드

## 1. Flink 설치 및 권한 설정

```bash
# /usr/local 디렉토리에 대한 권한 변경
sudo chown -R ssafy:ssafy /usr/local

# Flink 1.20 다운로드 및 압축 해제
sudo wget https://archive.apache.org/dist/flink/flink-1.20.0/flink-1.20.0-bin-scala_2.12.tgz
sudo tar -xvzf flink-1.20.0-bin-scala_2.12.tgz
```

## 2. Flink 설정 변경

```bash
cd flink-1.20.0/conf
vi flink-conf.yaml
```

다음 항목들을 추가 또는 수정:

```yaml
jobmanager.bind-host: 0.0.0.0
rest.address: 0.0.0.0
rest.bind-address: 0.0.0.0
```

## 3. 클러스터 시작 및 UI 접속

```bash
cd ../bin
./start-cluster.sh
```

- 웹 UI 접속: [http://localhost:8081](http://localhost:8081)

> 실행 시 `localhost`가 아닌 `Desktop-xxxx`와 같은 이름으로 뜰 수 있음  
> 이는 **WSL의 네트워크 구조** 때문입니다.
> 이를 통한 이슈를 없애고자 binding 설정을 사용합니다.

---

## WSL2 네트워크 구조 이해

### localhost란?

- `127.0.0.1`: 내 컴퓨터 내부에서만 접근 가능한 주소
- **“이 컴퓨터에서만 들어올 수 있는 문”**

### 0.0.0.0이란?

- “이 컴퓨터가 가진 **모든 네트워크 인터페이스에 대해 열어줌**”
- 즉, `localhost`, 내부 IP, 외부 IP 모두 포함

### WSL1 vs WSL2

| 항목 | WSL1 | WSL2 |
|------|------|------|
| 네트워크 공유 | Windows와 IP 공유 | 가상 네트워크 (IP 분리) |
| localhost 공유 | 가능 | 기본 불가능 (포트포워딩 필요) |
| 해결 방법 | 기본 공유됨 | `0.0.0.0` 바인딩 필수 |

### WSL2에서 0.0.0.0을 써도 괜찮은가?

- 대부분 NAT(Network Address Translation)로 외부에서 접근 불가
- Windows에서 보안 관리하므로, WSL 내에서 포트 개방은 상대적으로 안전
- Windows 브라우저에서 WSL 서버에 접속하려면 `0.0.0.0` 필수

---

## Flink 클러스터 종료

```bash
./stop-cluster.sh
```

---

## Socket 예제 실행

```bash
# 포트 확인
nc -l 8000  # 또는 9000 등 비어 있는 포트 확인

# 예제 실행
cd flink-1.20.0/
./bin/flink run examples/streaming/SocketWindowWordCount.jar --hostname localhost --port 8000
```

---

## Flink 로그 실시간 확인

```bash
cd flink-1.20.0/
tail -f log/flink-*.out
```

### tail 옵션 설명

- `tail`: 파일 마지막 부분 출력
- `-f`: 파일 변경사항을 실시간으로 추적하며 출력
- `log/flink-*.out`: Flink 로그 파일 전체 지정 (`standalonesession`, `taskexecutor` 등 포함)

---

이 설정을 마치면 Flink 1.20이 정상적으로 작동하며, WSL2 환경에서도 웹 UI 및 외부 접근이 가능합니다.
