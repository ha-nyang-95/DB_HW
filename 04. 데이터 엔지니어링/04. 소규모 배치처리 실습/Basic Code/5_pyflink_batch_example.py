from pyflink.table import EnvironmentSettings, TableEnvironment
from pyflink.table.expressions import col
import tempfile
import os
import pandas as pd
import numpy as np
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Flink 배치 처리 시작")
    
    # 배치 처리를 위한 테이블 환경 설정
    env_settings = EnvironmentSettings.in_batch_mode()
    table_env = TableEnvironment.create(env_settings)
    
    # 실행 설정
    config = table_env.get_config().get_configuration()    
    config.set_string("parallelism.default", "1")
    config.set_string("pipeline.auto-watermark-interval", "0")
    
    # 입력/출력 경로 설정
    input_path = create_sample_csv()
    output_dir = os.path.join(os.getcwd(), 'flink_output')  # 현재 디렉토리로 변경
    
    logger.info(f"입력 파일 경로: {input_path}")
    logger.info(f"출력 디렉토리 경로: {output_dir}")
    
    # 기존 출력 디렉토리 삭제
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
        logger.info("기존 출력 디렉토리 삭제됨")
    
    # 소스 테이블 생성
    source_ddl = f"""
    CREATE TABLE sales (
        product_id STRING,
        category STRING,
        price DOUBLE,
        quantity INT,
        transaction_date STRING
    ) WITH (
        'connector' = 'filesystem',
        'path' = '{input_path}',
        'format' = 'csv',
        'csv.field-delimiter' = ',',
        'csv.ignore-parse-errors' = 'true'
    )
    """
    logger.info("소스 테이블 생성 시작")
    table_env.execute_sql(source_ddl)
    logger.info("소스 테이블 생성 완료")
    
    # 싱크 테이블 생성
    sink_ddl = f"""
    CREATE TABLE sales_summary (
        category STRING,
        total_revenue DOUBLE,
        avg_price DOUBLE,
        total_quantity BIGINT,
        transaction_count BIGINT
    ) WITH (
        'connector' = 'filesystem',
        'path' = '{output_dir}',
        'format' = 'csv',
        'csv.field-delimiter' = ',',
        'csv.quote-character' = '"',
        'sink.rolling-policy.file-size' = '1MB',
        'sink.rolling-policy.rollover-interval' = '0',
        'sink.rolling-policy.check-interval' = '1s'
    )
    """
    logger.info("싱크 테이블 생성 시작")
    table_env.execute_sql(sink_ddl)
    logger.info("싱크 테이블 생성 완료")
    
    # SQL 쿼리 실행
    logger.info("데이터 처리 쿼리 실행 시작")
    result = table_env.execute_sql("""
    INSERT INTO sales_summary
    SELECT 
        category,
        SUM(price * quantity) AS total_revenue,
        AVG(price) AS avg_price,
        SUM(quantity) AS total_quantity,
        COUNT(*) AS transaction_count
    FROM sales
    GROUP BY category
    """)
    
    logger.info(f"쿼리 실행 결과: {result.get_job_client().get_job_status()}")
    print(f"배치 처리가 완료되었습니다. 결과는 {output_dir} 에 저장되었습니다.")
    
    # 결과 확인
    try:
        import time
        time.sleep(2)
        result_files = [f for f in os.listdir(output_dir) if f.startswith('part-')]
        logger.info(f"발견된 결과 파일들: {result_files}")
        if not result_files:
            raise FileNotFoundError("결과 파일을 찾을 수 없습니다.")
        result_file = os.path.join(output_dir, result_files[0])
        result_df = pd.read_csv(result_file, header=None,
            names=['category', 'total_revenue', 'avg_price', 'total_quantity', 'transaction_count'])
        print("\n===== 처리 결과 =====")
        print(result_df)
    except Exception as e:
        logger.error(f"결과 확인 중 오류 발생: {e}")
        print(f"결과 확인 중 오류 발생: {e}")
        print("출력 폴더를 직접 확인하세요.")

def create_sample_csv():
    """샘플 판매 데이터 생성"""
    temp_file = os.path.join(os.getcwd(), 'sales_data.csv')  # 현재 디렉토리에 저장
    np.random.seed(42)
    products = ['laptop', 'smartphone', 'tablet', 'monitor', 'keyboard']
    categories = ['electronics', 'accessories', 'peripherals']
    data = []
    for i in range(1000):
        product_id = f"P{np.random.randint(100, 999)}"
        category = np.random.choice(categories)
        price = round(np.random.uniform(10.0, 1000.0), 2)
        quantity = np.random.randint(1, 10)
        date = f"2024-{np.random.randint(1, 13):02d}-{np.random.randint(1, 29):02d}"
        data.append(f"{product_id},{category},{price},{quantity},{date}")
    with open(temp_file, 'w') as f:
        f.write('\n'.join(data))
    print(f"샘플 데이터가 {temp_file}에 생성되었습니다.")
    return temp_file

if __name__ == '__main__':
    main()
