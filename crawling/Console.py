import requests
from datetime import datetime
import schedule
import time

# API 키 (발급받은 API 키를 입력하세요)
api_key = '9ad4acf0420c46b0bba900de0cfbea94'  # 여기에 실제 API 키를 입력하세요
url = 'https://newsapi.org/v2/everything'  # 올바른 엔드포인트

def fetch_and_display_news():
    # 현재 날짜와 시간 가져오기
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    print(f"크롤링 날짜 및 시간: {formatted_time}")
    print("API 요청을 시작합니다...")

    # HTTP GET 요청
    params = {'q': '경제 OR IT OR AI', 'language': 'ko', 'apiKey': api_key}
    response = requests.get(url, params=params)

    print("API 요청 완료, 상태 코드:", response.status_code)

    # 응답 상태 코드 확인
    if response.status_code == 200:
        print("응답이 성공적으로 수신되었습니다.")

        data = response.json()

        # 뉴스 기사를 담을 리스트
        articles = data.get('articles', [])

        # 주제별로 기사를 분류할 딕셔너리
        categorized_articles = {'경제': [], 'IT': [], 'AI': []}

        # 기사 분류
        for article in articles:
            title = article['title']
            link = article['url']
            topic = '경제' if '경제' in title else 'IT' if 'IT' in title else 'AI' if 'AI' in title else None

            if topic:
                categorized_articles[topic].append({
                    'title': title,
                    'link': link
                })

        # 각 주제별로 최대 5개 기사 출력
        for topic, articles in categorized_articles.items():
            print(f"\n주제: {topic}")
            if articles:
                for i, article in enumerate(articles[:5]):  # 최대 5개 출력
                    print(f"기사 {i + 1}:")
                    print(f"제목: {article['title']}")
                    print(f"링크: {article['link']}")
            else:
                print("뉴스 기사가 없습니다.")
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
