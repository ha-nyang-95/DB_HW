# PyFlink 환경 설정 및 간단 예제 실행 가이드

## 1. 시스템 패키지 업데이트 및 필수 도구 설치

```bash
sudo apt update
sudo apt install -y software-properties-common
```

## 2. deadsnakes PPA 추가 (Python 3.10 설치를 위한 저장소)

```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
```

## 3. 패키지 목록 재업데이트

```bash
sudo apt update
```

## 4. Python 3.10 설치 및 가상환경 구성

```bash
sudo apt install -y python3.10 python3.10-venv python3.10-distutils

# 가상환경 생성 및 활성화
python3.10 -m venv ~/venvs/flink
source ~/venvs/flink/bin/activate

# Python 버전 확인
python --version  # Python 3.10.x
```

## 5. PyFlink 설치 후 실행 확인

# PyFlink 설치 (버전 명시)
pip install apache-flink==1.20

```bash
# PyFlink가 정상 설치되었는지 확인
python -c "import pyflink; print(pyflink.__file__)"
# 예상 출력:
# /home/ssafy/venvs/flink/lib/python3.10/site-packages/pyflink/__init__.py
```

## 6. PyFlink 로그 디렉토리 생성 및 권한 부여 (permission error 방지)
- PyFlink를 실행하면 내부적으로 로그를 남기기 위해 log 디렉토리를 사용
- 그러나 이 디렉토리는 기본적으로 존재하지 않거나, 쓰기 권한이 부족할 수 있습니다.
- 읽기/쓰기/실행 권한을 모두 부여

```bash
mkdir -p ~/venvs/flink/lib/python3.10/site-packages/pyflink/log
chmod -R 777 ~/venvs/flink/lib/python3.10/site-packages/pyflink/log
```

## 7. PyFlink 간단 실행 테스트

```bash
python -c 'from pyflink.datastream import StreamExecutionEnvironment; print("PyFlink 정상 실행 가능!")'
```

## 8. Flink 클러스터에 Python 인터프리터 명시(flink 설치 필요.)

```bash
./stop-cluster.sh

export PYFLINK_PYTHON=/home/ssafy/venvs/flink/bin/python

./start-cluster.sh
```

## 9. PyFlink 코드 실행

아래 코드를 `my_job.py`로 저장

```python
from pyflink.datastream import StreamExecutionEnvironment

# 1. 실행 환경 생성
env = StreamExecutionEnvironment.get_execution_environment()

# 2. 데이터 소스 정의 (리스트 데이터를 스트림으로 변환)
data_stream = env.from_collection([1, 2, 3, 4, 5])

# 3. 데이터 변환 (각 숫자에 *2 연산 수행)
transformed_stream = data_stream.map(lambda x: x * 2)

# 4. 결과를 콘솔에 출력
transformed_stream.print()

# 5. 작업 실행
env.execute("Simple Flink Job")
```


## 참고 사항
- 기본적으로 flink를 띄운 상태가 아니라면 위 코드는 로컬 MiniCluster에서 실행되며, Flink 내부적으로 미니 클러스터를 생성해 실행합니다.
- 그래서 flink 자체를 설치하지 않아도 pyflink로만 정상 실행이 가능합니다.
- 실제 Standalone Flink 클러스터에서 실행하려면 아래의 코드와와 같이 `flink run` 명령어를 사용하거나, `RemoteEnvironment`로 설정해야 합니다.
- 이렇게 해야 Flink 클러스터에 Python 작업이 제출됩니다.
- 이유는 Flink의 Python 실행 환경은 Java TaskManager에서 PythonWorker 프로세스를 별도로 띄워서 Python 코드를 실행합니다.
- PyFlink 내부적으로 Python Environment를 준비하고, Python 코드가 subprocess로 실행되기 때문입니다.
- PyFlink 실행 시 Flink 내부적으로 PythonWorker라는 별도의 Python 프로세스를 띄워서 Python 연산을 처리한다고 보면 됩니다.
- 이렇게 하면 출력결과를 확인할 수 없습니다.
- 따라서, Standalone을 필수적으로 활용해야 하는 4월 9일 실습 4를 제외한 나머지에서는 출력 결과를를 보고싶다면, python skeleton.py를 통해 MiniCluster를 활용해 실행하면 됩니다.

#### 정리
- Minicluster 사용: python skeleton.py
- Standalone cluster 사용: /usr/local/flink-1.20.0/bin/flink run -py my_job.py

```bash
export FLINK_HOME=/usr/local/flink-1.20.0
/usr/local/flink-1.20.0/bin/flink run -py my_job.py
```

## job을 UI 상에서 보고 싶은 경우 따로 설정해줘야 함
- Job을 파일 시스템에 저장(config.yaml)
jobmanager.archive.fs.dir: file:///tmp/flink-history