import feedparser
from bs4 import BeautifulSoup
import requests

# RSS 피드 URL (예: Khan 뉴스 RSS)
RSS_FEED_URL = "https://www.khan.co.kr/rss/rssdata/total_news.xml"


def crawl_article(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    content_tag = soup.find_all("p", class_="content_text text-l")
    content_text = "\n\n".join([tag.text.strip() for tag in content_tag])

    return content_text

def main():
    print("RSS 피드를 확인하는 중...")

    feed = feedparser.parse(RSS_FEED_URL)

    for entry in feed.entries:
        print(entry.link)
        print()
        content = crawl_article(entry.link)
        print(content)
        print('='*100)

if __name__ == "__main__":
    main()
