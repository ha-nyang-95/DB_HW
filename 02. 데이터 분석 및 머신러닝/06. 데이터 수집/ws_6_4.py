from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# 1. 웹 드라이버 설정 및 브라우저 열기
def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # 실제 실행할 때는 주석 처리하여 브라우저가 열리도록 설정
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)  # Chrome() 메소드를 사용하여 웹 드라이버를 설정합니다.
    return driver

# 2. 페이지 접속 및 로딩 대기
def navigate_to_page(driver):
    print("\n문제 1. 페이지 접속 및 로드")
    try:
        driver.get("https://topis.seoul.go.kr")  # 지정된 URL로 이동합니다.
        print("답: 페이지에 접속했습니다.")
        WebDriverWait(driver, 20).until(  # 20초 동안 요소가 로드될 때까지 대기합니다.
            EC.presence_of_element_located((By.ID, "contents-area"))  # contents-area 요소의 존재 여부를 확인합니다.
        )
        print("답: 페이지가 로드되었습니다.")
    except TimeoutException:
        print("답: 페이지 로딩 시간 초과")
        driver.quit()
    except WebDriverException as e:
        print(f"답: 웹 드라이버 예외 발생: {e}")
        driver.quit()

# 3. 검색어 입력 및 검색 버튼 클릭
def search_keyword(driver, keyword):
    print("\n문제 2. 검색 기능 사용")
    try:
        contents_area = driver.find_element(By.ID, "contents-area")  # contents-area 요소를 찾습니다.
        search_box = contents_area.find_element(By.CSS_SELECTOR, "input.int-search")  # 검색 창 요소를 찾습니다.
        search_box.send_keys(keyword)  # '관악구' 키워드를 입력합니다.
        print(f"답: '{keyword}' 키워드를 입력했습니다.")

        search_button = contents_area.find_element(By.CSS_SELECTOR, "input.int-btn")  # 검색 버튼 요소를 찾습니다.
        search_button.click()  # 검색 버튼을 클릭합니다.
        print("답: 검색 버튼을 클릭했습니다.")

        WebDriverWait(driver, 20).until(  # 20초 동안 검색 결과가 로드될 때까지 대기합니다.
            EC.presence_of_element_located((By.CLASS_NAME, "asideContent"))  # asideContent 요소의 존재 여부를 확인합니다.
        )
        print("답: 검색 결과를 찾았습니다.")
    except TimeoutException:
        print("답: 검색 결과 로딩 시간 초과")
    except NoSuchElementException:
        print("답: 검색 요소를 찾을 수 없습니다.")
    except Exception as e:
        print(f"답: 검색 중 오류 발생: {e}")

# 4. 검색 결과 크롤링
def scrape_results(driver):
    print("\n문제 3. 검색 결과 크롤링")
    try:
        aside_content = driver.find_element(By.CLASS_NAME, "asideContent")  # asideContent 요소를 찾습니다.
        result_sections = {
            "도로": "resultListTraffic",
            "버스": "resultListBus",
            "정류소": "resultListBusStn",
            "따릉이": "resultListBic",
            "주차장": "resultListPark"
        }

        # 각 섹션의 검색 결과를 크롤링하여 출력
        for section_name, result_id in result_sections.items():
            try:
                print(f"\n{section_name} 검색 결과:")
                results = aside_content.find_element(By.ID, result_id).find_elements(By.TAG_NAME, "____")  # 각 li 태그 요소를 찾습니다.
                if results:
                    for result in results:
                        print(f"답: {result.text.strip()}")  # 검색 결과 텍스트를 출력합니다.
                else:
                    print(f"답: {section_name}에서 검색된 내역이 없습니다.")
            except NoSuchElementException:
                print(f"답: {section_name} 검색 결과가 없습니다.")
    except Exception as e:
        print(f"답: 결과 크롤링 중 오류 발생: {e}")

# 5. 메인 함수 실행
def main():
    driver = setup_driver()
    navigate_to_page(driver)
    search_keyword(driver, "관악구")  # 검색어를 원하는 대로 수정하세요
    scrape_results(driver)
    driver.quit()  # 브라우저를 종료합니다.

if __name__ == "__main__":
    main()
