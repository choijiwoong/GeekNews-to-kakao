import google.generativeai as genai
import os

class GeminiAPI:
    def __init__(self, api_key):
        # Gemini API 설정
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def summarize_news(self, title, description):
        """뉴스 한 건을 요약하여 카톡용 텍스트로 변환"""
        prompt = f"""
        당신은 IT 전문 뉴스 큐레이터입니다. 아래 뉴스를 읽고 한국어로 핵심만 요약해 주세요.

        [지시사항]
        1. 첫 줄은 내용을 관통하는 '한 줄 요약'을 작성하세요.
        2. 그 아래에 '주요 포인트'를 2~3개 불렛포인트로 작성하세요.
        3. 마지막에는 관련 해시태그를 2개 작성하세요.
        4. 친절하고 전문적인 말투를 사용하세요.

        제목: {title}
        내용: {description}
        """

        try:
            response = self.model.generate_content(prompt)
            summary_text = response.text.strip()

            # 최종 카톡 템플릿 구성
            formatted_msg = (
                f"📢 GeekNews 요약\n\n"
                f"📌 {title}\n\n"
                f"{summary_text}\n\n"
                f"🔗 링크: (원문 확인은 아래 버튼 클릭)"
            )
            return formatted_msg
        except Exception as e:
            print(f"[!] Gemini 요약 오류: {e}")
            return f"📢 GeekNews\n\n📌 {title}\n\n(요약 생성 중 오류가 발생했습니다.)\n\n🔗 링크: {title}"

    def process_all(self, news_list):
        """뉴스 리스트 전체를 순회하며 요약 목록 반환"""
        final_messages = []
        for news in news_list:
            print(f"[*] 요약 중: {news['title']}")
            summary = self.summarize_news(news['title'], news.get('description', ''))
            # 실제 링크는 카카오톡 버튼에 넣을 것이므로 데이터 구조에 함께 담음
            final_messages.append({
                "text": summary,
                "link": news['link']
            })
        return final_messages