import feedparser
import os
import ssl

# 1. 정확한 긱뉴스 RSS 주소로 수정
RSS_URL = "https://news.hada.io/rss/news"
DB_FILE = "last_link.txt"

def get_latest_news():
    print(f"[*] 스크립트 실행 시작: {RSS_URL} 접속 시도 중...")

    # SSL 인증서 문제 해결 (로컬/서버 공용)
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    # RSS 피드 읽기 (브라우저인 척 User-Agent 추가)
    feed = feedparser.parse(RSS_URL, agent='Mozilla/5.0')

    if not feed.entries:
        print("[!] RSS 데이터를 불러오지 못했습니다. 주소나 네트워크를 확인하세요.")
        if hasattr(feed, 'status'):
            print(f"[*] 상태 코드: {feed.status}")
        return None

    # 가장 최신 뉴스 1개 추출
    latest_entry = feed.entries[0]
    link = latest_entry.link
    title = latest_entry.title

    print(f"[*] 최신 뉴스 확인: {title}")

    # 2. 중복 체크 (이전에 저장한 링크와 비교)
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding='utf-8') as f:
            last_link = f.read().strip()
            if last_link == link:
                print("[-] 새로운 뉴스가 없습니다. (중복)")
                return None

    # 3. 새로운 뉴스라면 링크 저장
    with open(DB_FILE, "w", encoding='utf-8') as f:
        f.write(link)

    print(f"[+] 새 뉴스 발견 및 저장 완료: {title}")
    return {"title": title, "link": link}

if __name__ == "__main__":
    news = get_latest_news()
    if news:
        print(f"\n[최종 결과]\n제목: {news['title']}\n링크: {news['link']}\n")
    print("[*] 스크립트 실행 종료.")