from manager import NewsManager

if __name__ == "__main__":
    # 실행부
    RSS_URL = "https://news.hada.io/rss/news"
    DB_FILE = "last_link.txt"

    manager = NewsManager(RSS_URL, DB_FILE)
    manager.run()