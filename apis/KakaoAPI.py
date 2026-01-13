import requests
import json
import os

class KakaoAPI:
    def __init__(self, client_id, token_file="kakao_code.json"):
        self.client_id = client_id
        self.token_file = token_file
        self.tokens = self.load_tokens()

    def load_tokens(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as f:
                return json.load(f)
        return None

    def save_tokens(self, tokens):
        with open(self.token_file, "w") as f:
            json.dump(tokens, f)

    def refresh_access_token(self):
        """기존 Refresh Token을 사용하여 Access Token 갱신"""
        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": self.tokens.get("refresh_token")
        }
        response = requests.post(url, data=data)
        result = response.json()

        if "access_token" in result:
            self.tokens["access_token"] = result["access_token"]
            # 만약 새 refresh_token이 오면 그것도 업데이트
            if "refresh_token" in result:
                self.tokens["refresh_token"] = result["refresh_token"]
            self.save_tokens(self.tokens)
            print("[*] 카카오 토큰 갱신 성공")
            return True
        else:
            print(f"[!] 토큰 갱신 실패: {result}")
            return False

    def send_text_message(self, text):
        """나에게 텍스트 메시지 보내기"""
        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        headers = {"Authorization": f"Bearer {self.tokens['access_token']}"}

        payload = {
            "template_object": json.dumps({
                "object_type": "text",
                "text": text,
                "link": {
                    "web_url": "https://news.hada.io",
                    "mobile_web_url": "https://news.hada.io"
                },
                "button_title": "뉴스 보기"
            })
        }

        res = requests.post(url, headers=headers, data=payload)

        # 401 에러(토큰 만료) 시 갱신 후 재시도
        if res.status_code == 401:
            print("[!] 토큰 만료됨. 갱신 시도 중...")
            if self.refresh_access_token():
                headers["Authorization"] = f"Bearer {self.tokens['access_token']}"
                res = requests.post(url, headers=headers, data=payload)

        return res.status_code == 200