import os
from apis.GeminiAPI import GeminiAPI
from apis.KakaoAPI import KakaoAPI
import feedparser
import ssl

class NewsManager:
    def __init__(self, rss_url, db_file):
        self.rss_url = rss_url
        self.db_file = db_file

        # 환경 변수에서 키 로드
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.kakao_key = os.environ.get("KAKAO_REST_API_KEY")

        # 모듈 초기화
        self.summarizer = GeminiAPI(self.gemini_key)
        self.kakao = KakaoAPI(self.kakao_key)

    def fetch_new_entries(self):
        """RSS에서 새로운 뉴스 목록만 필터링해서 가져옴"""
        print(f"[*] RSS 피드 확인 중: {self.rss_url}")

        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context

        feed = feedparser.parse(self.rss_url, agent='Mozilla/5.0')

        if not feed.entries:
            print("[!] 피드 데이터를 가져오지 못했습니다.")
            return []

        # 기존 기록 확인 (콜드 스타트 대응)
        last_link = ""
        if os.path.exists(self.db_file):
            with open(self.db_file, "r", encoding='utf-8') as f:
                last_link = f.read().strip()
        else:
            print("[!] 콜드 스타트: 기준점 생성 후 종료.")
            self._update_last_link(feed.entries[0].link)
            return []

        new_news = []
        for entry in feed.entries:
            if entry.link == last_link:
                break
            new_news.append({
                "title": entry.title,
                "description": entry.summary,
                "link": entry.link
            })

        return new_news

    def _update_last_link(self, link):
        """마지막 읽은 링크 저장"""
        with open(self.db_file, "w", encoding='utf-8') as f:
            f.write(link)

    def run(self):
        """전체 프로세스 실행 매니저"""
        print("=== 뉴스 자동 요약 및 전송 프로세스 시작 ===")

        # 1. 뉴스 수집
        new_items = self.fetch_new_entries()
        if not new_items:
            print("[-] 새로운 뉴스가 없습니다.")
            return

        print(f"[+] 총 {len(new_items)}개의 새로운 뉴스 발견.")

        # 2. 뉴스 요약 및 전송 루프
        # 리스트를 뒤집어서 오래된 뉴스부터 전송 (정렬)
        new_items.reverse()

        success_count = 0
        for item in new_items:
            try:
                # Gemini 요약 수행
                print(f"[*] 요약 중: {item['title']}")
                formatted_data = self.summarizer.summarize_news(item['title'], item['description'])

                # 카카오톡 전송
                # formatted_data는 텍스트, item['link']는 버튼용 URL
                if self.kakao.send_text_message(formatted_data, item['link']):
                    success_count += 1
                    print(f"[OK] 전송 완료: {item['title']}")
                else:
                    print(f"[Fail] 카톡 전송 실패: {item['title']}")

            except Exception as e:
                print(f"[Error] 처리 중 에러 발생: {e}")

        # 3. 모든 전송이 끝나면 DB 파일 업데이트 (가장 최신 뉴스 기준)
        # 루프를 돌기 전 원본 feed.entries[0].link를 저장하는 것이 안전함
        # 여기서는 단순화를 위해 실행 시점의 최신 항목으로 저장
        self._update_last_link(new_items[-1]['link']) # reverse 했으므로 마지막이 최신

        print(f"=== 프로세스 종료 (성공: {success_count}/{len(new_items)}) ===")

if __name__ == "__main__":
    # 실행부
    RSS_URL = "https://news.hada.io/rss/news"
    DB_FILE = "last_link.txt"

    manager = NewsManager(RSS_URL, DB_FILE)
    manager.run()