import feedparser
from bs4 import BeautifulSoup
import requests

# RSS 피드 URL (예: Khan 뉴스 RSS)
RSS_FEED_URL = "https://www.mk.co.kr/rss/30100041/"


def crawl_article(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    category = soup.find("span", class_="cate c_point").text.strip()
    title = soup.find("h2", class_="news_ttl").text.strip()
    writer = soup.select_one("dl.author dd").text.strip()
    time_tags = soup.select("dl.registration dd")
    if len(time_tags)==1:
        write_time = time_tags[0].text.strip()
    else:
        write_time = time_tags[1].text.strip()

     # 본문 내용 크롤링
    content_paragraphs = []
    ref_num = 2
    while True:
        tag = soup.find("p", {"refid": str(ref_num)})
        if tag:
            content_paragraphs.append(tag.text.strip())
            ref_num += 1
        else:
            break

    content = "\n\n".join(content_paragraphs)

    return {
        "title": title,
        "category": category,
        "writer": writer,
        "write_time": write_time,
        "content": content
    }

def main():
    print("RSS 피드를 확인하는 중...")

    feed = feedparser.parse(RSS_FEED_URL)

    for entry in feed.entries:
        print(f"[URL] {entry.link}")
        print()

        article = crawl_article(entry.link)

        for key, value in article.items():
            print(f"[{key.upper()}]\n{value}\n")
        
        print("=" * 100)

if __name__ == "__main__":
    main()
