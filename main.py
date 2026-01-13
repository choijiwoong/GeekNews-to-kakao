import feedparser
import os

# 1. 긱뉴스 RSS 주소
RSS_URL = "https://news.hada.io/rss"
DB_FILE = "last_link.txt"

def get_latest_news():
    # RSS 피드 읽기
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        return None

    # 가장 최신 뉴스 1개 추출
    latest_entry = feed.entries[0]
    link = latest_entry.link
    title = latest_entry.title

    # 2. 중복 체크 (이전에 보낸 링크인지 확인)
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            last_link = f.read().strip()
            if last_link == link:
                print("새로운 뉴스가 없습니다.")
                return None

    # 3. 새로운 뉴스라면 링크 저장 (업데이트)
    with open(DB_FILE, "w") as f:
        f.write(link)

    print(f"새 뉴스 발견: {title}")
    return {"title": title, "link": link}

if __name__ == "__main__":
    news = get_latest_news()
    if news:
        # 일단은 출력이 되나 확인용 (나중에 여기서 AI 요약으로 보냄)
        print(f"DEBUG: {news['title']} - {news['link']}")