import requests
from datetime import datetime
import schedule
import time

# API 키 (발급받은 API 키를 입력하세요)
api_key = '9ad4acf0420c46b0bba900de0cfbea94'  # 여기에 실제 API 키를 입력하세요
url = 'https://newsapi.org/v2/everything'  # 올바른 엔드포인트

# 텔레그램 봇 설정
telegram_bot_token = 'YOUR_TELEGRAM_BOT_TOKEN'  # 여기에 실제 텔레그램 봇 토큰을 입력하세요
telegram_chat_id = 'YOUR_CHAT_ID'  # 여기에 실제 채팅 ID를 입력하세요

def fetch_and_display_news():
    # 현재 날짜와 시간 가져오기
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    print(f"크롤링 날짜 및 시간: {formatted_time}")
    print("API 요청을 시작합니다...")

    # HTTP GET 요청
    params = {'q': '경제 OR IT OR AI OR 보안 OR 사이버 OR 해킹', 'language': 'ko', 'apiKey': api_key}
    response = requests.get(url, params=params)

    print("API 요청 완료, 상태 코드:", response.status_code)

    # 응답 상태 코드 확인
    if response.status_code == 200:
        print("응답이 성공적으로 수신되었습니다.")

        data = response.json()

        # 뉴스 기사를 담을 리스트
        articles = data.get('articles', [])

        # 주제별로 기사를 분류할 딕셔너리
        categorized_articles = {'경제': [], 'IT': [], 'AI': [], '보안': []}

        # 기사 분류
        for article in articles:
            title = article['title']
            link = article['url']
            topic = '경제' if '경제' in title else 'IT' if 'IT' in title else 'AI' if 'AI' in title else '보안' if '보안' in title or '사이버' in title or '해킹' in title else None

            if topic:
                categorized_articles[topic].append({
                    'title': title,
                    'link': link
                })

        # 텔레그램 메시지 생성
        message = f"크롤링 날짜 및 시간: {formatted_time}\n\n"

        # 각 주제별로 최대 5개 기사 메시지에 추가
        for topic, articles in categorized_articles.items():
            message += f"\n주제: {topic}\n"
            if articles:
                for i, article in enumerate(articles[:5]):  # 최대 5개 출력
                    message += f"기사 {i + 1}:\n"
                    message += f"제목: {article['title']}\n"
                    message += f"링크: {article['link']}\n"
            else:
                message += "뉴스 기사가 없습니다.\n"

        # 텔레그램으로 메시지 전송
        send_message_url = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage'
        payload = {
            'chat_id': telegram_chat_id,
            'text': message,
            'parse_mode': 'Markdown'  # 마크다운 형식으로 텍스트 전송
        }

        response = requests.post(send_message_url, json=payload)

        # 텔레그램 메시지 전송 결과 확인
        if response.status_code == 200:
            print("텔레그램으로 메시지를 성공적으로 전송했습니다.")
        else:
            print("텔레그램으로 메시지 전송에 실패했습니다. 상태 코드:", response.status_code)
    else:
        print("API 요청 실패, 상태 코드:", response.status_code)

# 12시와 00시에 뉴스 업데이트
schedule.every().day.at("00:00").do(fetch_and_display_news)
schedule.every().day.at("12:00").do(fetch_and_display_news)

# 프로그램 실행
fetch_and_display_news()  # 처음 실행하여 바로 보내기
while True:
    schedule.run_pending()
    time.sleep(1)
