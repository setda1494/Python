import os
import time
import requests
from pytube import YouTube
from datetime import datetime
from pathlib import Path
from plyer import notification  # 알림 기능을 위한 라이브러리
import threading  # 백그라운드 실행을 위한 모듈

# YouTube API 키 및 채널 ID 설정
API_KEY = 'YOUR_API_KEY'  # 여기에 자신의 API 키를 입력하세요
CHANNEL_ID = 'YOUR_CHANNEL_ID'  # 여기에 채널 ID를 입력하세요

# API_KEY와 CHANNEL_ID가 설정되었는지 확인
if not API_KEY or not CHANNEL_ID:
    raise ValueError("API_KEY와 CHANNEL_ID를 설정해야 합니다.")  # 예외 처리

# 모니터링할 요일과 시간 설정
MONITOR_DAY = 6  # 6은 일요일
MONITOR_HOUR = 20  # 20은 8시 (24시간 형식)

def log_error(message):
    """오류 메시지를 로그 파일에 기록하는 함수."""
    error_log_file = "error_log.txt"  # 오류 로그 파일 이름
    with open(error_log_file, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def get_live_broadcast_id():
    """실시간 방송 ID를 가져오는 함수."""
    try:
        url = f'https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={CHANNEL_ID}&eventType=live&type=video'
        response = requests.get(url)  # API에 요청하여 실시간 방송 정보 가져오기
        response.raise_for_status()  # 상태 코드가 200이 아닐 경우 예외 발생
        
        data = response.json()  # JSON 형식으로 응답 받기
        if data['items']:
            return data['items'][0]['id']['videoId']  # 방송 ID 반환
    except Exception as e:
        log_error(f"실시간 방송 ID를 가져오는 중 오류 발생: {e}")  # 오류 메시지 기록
    return None  # 방송이 없으면 None 반환

def get_video_details(video_id):
    """비디오의 상세 정보를 가져오는 함수."""
    try:
        url = f'https://www.googleapis.com/youtube/v3/videos?key={API_KEY}&id={video_id}&part=status'
        response = requests.get(url)  # API에 요청하여 비디오 상세 정보 가져오기
        response.raise_for_status()  # 상태 코드가 200이 아닐 경우 예외 발생
        
        data = response.json()  # JSON 형식으로 응답 받기
        if data['items']:
            return data['items'][0]['status']['lifeCycleStatus']  # 방송 상태 반환
    except Exception as e:
        log_error(f"비디오 상세 정보를 가져오는 중 오류 발생: {e}")  # 오류 메시지 기록
    return None  # 상태를 가져오지 못한 경우 None 반환

def download_video(video_url, save_path, video_title):
    """비디오를 다운로드하는 함수."""
    file_path = Path(save_path) / f"{video_title}.mp4"  # 파일 경로 생성

    if file_path.is_file():  # 이미 다운로드한 파일인지 확인
        print(f"{video_title}는 이미 다운로드되었습니다.")
        return True  # 이미 다운로드된 경우

    try:
        yt = YouTube(video_url)  # YouTube 객체 생성
        print(f"다운로드할 비디오 제목: {video_title}")

        # 1080p 품질의 MP4 형식 선택
        stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution='1080p').first()
        if stream is None:
            print(f"1080p 품질의 MP4 스트림을 찾을 수 없습니다.")
            return False

        print("비디오 다운로드 중...")

        # 다운로드 진행률 표시 및 파일 저장
        stream.download(save_path, filename=f"{video_title}.mp4", on_progress_callback=on_progress)
        print("다운로드 완료!")
        return True  # 다운로드 성공
    except Exception as e:
        log_error(f"다운로드 중 오류 발생: {e}")  # 오류 메시지 기록
        return False  # 다운로드 실패

def on_progress(stream, chunk, bytes_remaining):
    """다운로드 진행률을 표시하는 콜백 함수."""
    total_size = stream.filesize  # 전체 파일 크기
    bytes_downloaded = total_size - bytes_remaining  # 다운로드된 바이트 수
    percentage = (bytes_downloaded / total_size) * 100  # 다운로드 진행률 계산
    print(f"다운로드 진행률: {percentage:.2f}%")  # 진행률 출력

def log_download(video_title):
    """다운로드 로그를 기록하는 함수."""
    log_file = "download_log.txt"  # 로그 파일 이름
    with open(log_file, 'a', encoding='utf-8') as f:
        # 로그에 날짜 및 시간과 함께 비디오 제목 기록
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {video_title} 다운로드 완료\n")

def send_notification(title, message):
    """시스템 알림을 보내는 함수."""
    notification.notify(
        title=title,  # 알림 제목
        message=message,  # 알림 내용
        app_name='YouTube Live Downloader',  # 애플리케이션 이름
        timeout=10  # 알림 표시 시간 (초)
    )

def should_monitor():
    """현재 시간이 설정된 요일과 시간인지 확인하는 함수."""
    now = datetime.now()
    return now.weekday() == MONITOR_DAY and now.hour == MONITOR_HOUR  # 설정된 요일과 시간 확인

def monitor_live_broadcast():
    """실시간 방송을 모니터링하는 함수."""
    save_path = "downloads"  # 다운로드할 폴더 설정
    if not os.path.exists(save_path):
        os.makedirs(save_path)  # 폴더가 없으면 생성

    live_broadcast_id = None  # 현재 실시간 방송 ID 초기화

    while True:
        if should_monitor():  # 설정된 요일과 시간에만 모니터링
            current_live_broadcast_id = get_live_broadcast_id()  # 현재 실시간 방송 ID 가져오기

            if current_live_broadcast_id and current_live_broadcast_id != live_broadcast_id:  # 새로운 방송 시작 시
                live_broadcast_id = current_live_broadcast_id
                print("새로운 실시간 방송이 시작되었습니다.")
                send_notification("Live Broadcast Started", f"새로운 방송이 시작되었습니다: https://www.youtube.com/watch?v={live_broadcast_id}")
            elif live_broadcast_id:  # 방송이 종료된 경우
                status = get_video_details(live_broadcast_id)  # 방송 상태 확인
                if status == "complete":
                    live_video_url = f"https://www.youtube.com/watch?v={live_broadcast_id}"  # 비디오 URL 생성
                    video_title = f"{live_broadcast_id}_{datetime.now().strftime('%Y%m%d')}"  # 제목에 날짜 추가

                    # 다운로드 시도
                    success = download_video(live_video_url, save_path, video_title)  # 비디오 다운로드 시도
                    if success:
                        log_download(video_title)  # 로그 기록
                        send_notification("Live Broadcast Downloaded", f"방송이 다운로드되었습니다: {video_title}")  # 다운로드 알림

                live_broadcast_id = None  # 방송 ID 초기화

        else:
            print("현재는 방송 모니터링을 하지 않습니다.")
            time.sleep(3600)  # 1시간 대기 (방송이 없어도 대기)

        time.sleep(60)  # 1분마다 체크

if __name__ == "__main__":
    # 백그라운드에서 방송 모니터링 스레드 시작
    monitor_thread = threading.Thread(target=monitor_live_broadcast)
    monitor_thread.daemon = True  # 메인 프로그램 종료 시 스레드도 종료
    monitor_thread.start()

    # 메인 프로그램은 다른 작업을 수행하거나 종료 대기
    while True:
        time.sleep(1)  # 메인 스레드는 계속 실행 중
