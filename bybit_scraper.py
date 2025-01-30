import requests
from bs4 import BeautifulSoup
from firebase_admin import messaging, initialize_app
import time

# Firebase 초기화 (한 번만 실행)
initialize_app()

# 감시할 Bybit 공지사항 페이지
URL = "https://announcements.bybit.com/en/?page=1&category=delistings"

# 최근 공지사항 저장
latest_notice = None

def check_new_notice():
    global latest_notice
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    # 첫 번째 공지사항 가져오기
    article = soup.select_one(".article-title")
    if article:
        title = article.get_text(strip=True)
        link = "https://announcements.bybit.com" + article.find("a")["href"]

        # 새로운 공지사항이면 알람 전송
        if title != latest_notice:
            latest_notice = title
            send_push_notification(title, link)

def send_push_notification(title, link):
    """Firebase 푸시 알람 보내기"""
    message = messaging.Message(
        notification=messaging.Notification(
            title="📢 Bybit 새 공지!",
            body=title
        ),
        data={"link": link},
        topic="bybit_announcements"
    )
    messaging.send(message)
    print(f"새 공지사항 감지됨: {title} - {link}")

# 1분마다 실행
if __name__ == "__main__":
    while True:
        check_new_notice()
        time.sleep(60)
