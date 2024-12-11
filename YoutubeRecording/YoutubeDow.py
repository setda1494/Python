import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from pytube import YouTube, Playlist
import threading
from tkinter.ttk import Progressbar
import os
import json
import time
import requests
from PIL import Image, ImageTk
from io import BytesIO  # 이미지 처리를 위한 라이브러리

# API 키와 기본 URL 설정
API_KEY = 'YOUR_API_KEY'  # 여기에 본인의 API 키를 입력하세요
SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'

# 다운로드 히스토리 및 대기열 저장
download_history = []  # 다운로드한 비디오의 제목을 저장하는 리스트
download_queue = []    # 대기 중인 비디오 URL을 저장하는 리스트
current_download = None  # 현재 다운로드 중인 비디오 URL
is_downloading = False  # 다운로드 진행 상태 플래그
cancel_download = False  # 다운로드 취소 플래그

# 기본 설정 로드
settings_file = "settings.json"  # 설정 파일 이름
settings = {
    "download_path": "",  # 다운로드 경로
    "file_format": "mp4",  # 기본 파일 형식
    "quality": "720p",  # 기본 해상도
}

def load_settings():
    """설정 파일에서 설정을 로드합니다."""
    global settings
    if os.path.exists(settings_file):  # 설정 파일이 존재하는 경우
        with open(settings_file, 'r') as f:
            settings = json.load(f)  # 설정 로드

def save_settings():
    """현재 설정을 파일에 저장합니다."""
    with open(settings_file, 'w') as f:
        json.dump(settings, f)  # 설정 저장

def update_settings():
    """설정을 업데이트하고 저장합니다."""
    settings["download_path"] = download_path.get()  # 다운로드 경로 업데이트
    settings["file_format"] = format_var.get()  # 파일 형식 업데이트
    settings["quality"] = quality_var.get()  # 해상도 업데이트
    save_settings()  # 설정 저장

def search_videos(query):
    """YouTube에서 비디오 검색 결과를 가져옵니다."""
    params = {
        'part': 'snippet',
        'q': query,
        'key': API_KEY,
        'maxResults': 5,  # 최대 검색 결과 수
        'type': 'video'
    }
    response = requests.get(SEARCH_URL, params=params)
    if response.status_code == 200:
        return response.json()['items']
    else:
        messagebox.showerror("오류", "검색 중 오류가 발생했습니다.")
        return []

def display_search_results(videos):
    """검색 결과를 GUI에 표시합니다."""
    for widget in results_frame.winfo_children():
        widget.destroy()  # 이전 결과 지우기

    for video in videos:
        title = video['snippet']['title']
        description = video['snippet']['description']
        thumbnail_url = video['snippet']['thumbnails']['default']['url']
        video_id = video['id']['videoId']
        
        # 비디오 정보 표시
        video_frame = tk.Frame(results_frame)
        video_frame.pack(pady=5)

        # 썸네일 이미지 표시
        img_response = requests.get(thumbnail_url)
        img_data = Image.open(BytesIO(img_response.content))
        img = img_data.resize((120, 90), Image.ANTIALIAS)
        thumbnail = ImageTk.PhotoImage(img)

        img_label = tk.Label(video_frame, image=thumbnail)
        img_label.image = thumbnail  # 참조 유지
        img_label.pack(side=tk.LEFT)

        info_label = tk.Label(video_frame, text=f"{title}\n{description}", justify=tk.LEFT)
        info_label.pack(side=tk.LEFT)

        download_button = tk.Button(video_frame, text="다운로드", command=lambda v_id=video_id: download_video(v_id))
        download_button.pack(side=tk.RIGHT)

def search_button_clicked():
    """검색 버튼 클릭 시 호출되는 함수."""
    query = search_entry.get()
    if query:
        videos = search_videos(query)
        display_search_results(videos)
    else:
        messagebox.showwarning("경고", "검색어를 입력하세요.")

def download_video(video_id):
    """선택한 비디오를 다운로드합니다."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    start_download(url)

def download_youtube_video(url, path, progress_var, file_format, quality_var, filename):
    """유튜브 비디오를 다운로드합니다."""
    global current_download, is_downloading, cancel_download
    is_downloading = True
    cancel_download = False  # 다운로드 시작 시 취소 플래그 초기화

    try:
        yt = YouTube(url, on_progress_callback=lambda stream, chunk, bytes_remaining: 
                      on_progress(stream, chunk, bytes_remaining, yt, progress_var))

        # 비디오 정보 표시
        video_info = f"제목: {yt.title}\n설명: {yt.description}\n업로더: {yt.author}\n해상도: {quality_var}\n"
        messagebox.showinfo("비디오 정보", video_info)

        # 비디오 다운로드
        if file_format == 'mp4':
            stream = yt.streams.filter(res=quality_var, file_extension='mp4').first()
        elif file_format == 'mp3':
            stream = yt.streams.filter(only_audio=True).first()  # 오디오 스트림 선택
        elif file_format == 'avi':
            stream = yt.streams.filter(file_extension='mp4', res=quality_var).first()  # AVI 형식으로 다운로드

        # 파일 이름 설정
        final_filename = os.path.join(path, f"{filename}.{file_format}") if filename else os.path.join(path, f"{yt.title}.{file_format}")

        if os.path.exists(final_filename):  # 파일 이름 충돌 처리
            final_filename = handle_file_collision(final_filename)

        if file_format in ['mp4', 'avi']:
            stream.download(output_path=path, filename=final_filename)  # 비디오 다운로드
        else:  # MP3 다운로드
            audio_file = stream.download(output_path=path)  # 오디오 다운로드
            base, _ = os.path.splitext(audio_file)  # 파일 이름과 확장자 분리
            new_file = base + '.mp3'  # 새 MP3 파일 이름
            if os.path.exists(new_file):  # 파일 이름 충돌 처리
                new_file = handle_file_collision(new_file)
            os.rename(audio_file, new_file)  # 파일 이름 변경

        # 비디오 태그 및 설명 저장
        save_video_info(yt.title, yt.description, yt.keywords, path)

        # 다운로드 완료 메시지 및 알림
        messagebox.showinfo("완료", f"'{yt.title}'가 성공적으로 다운로드 되었습니다!")
        download_history.append(yt.title)  # 다운로드 히스토리에 추가
        log_download(yt.title)  # 다운로드 로그 기록
    except Exception as e:
        messagebox.showerror("오류", f"다운로드 중 오류 발생: {e}")
    finally:
        is_downloading = False
        process_download_queue(path, progress_var, file_format)  # 대기열 처리

def save_video_info(title, description, keywords, path):
    """비디오의 제목, 설명, 태그를 텍스트 파일로 저장합니다."""
    info_filename = os.path.join(path, f"{title}_info.txt")
    with open(info_filename, "w", encoding="utf-8") as info_file:
        info_file.write(f"제목: {title}\n")
        info_file.write(f"설명: {description}\n")
        info_file.write("태그: " + ", ".join(keywords) + "\n")  # 태그 저장
    print(f"비디오 정보가 '{info_filename}'에 저장되었습니다.")

def handle_file_collision(filename):
    """동일한 이름의 파일이 있을 경우 파일 이름을 변경합니다."""
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(filename):  # 파일이 존재하는 동안
        filename = f"{base}_{counter}{ext}"  # 이름 변경
        counter += 1
    return filename

def log_download(title):
    """다운로드 히스토리를 로그 파일에 기록합니다."""
    with open("download_log.txt", "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {title}\n")  # 로그 기록

def download_playlist(playlist_url, path, progress_var, file_format):
    """플레이리스트를 다운로드합니다."""
    try:
        pl = Playlist(playlist_url)  # 플레이리스트 객체 생성
        for video in pl.videos:
            download_queue.append(video.watch_url)  # 비디오 URL을 대기열에 추가
        process_download_queue(path, progress_var, file_format)  # 대기열 처리
    except Exception as e:
        messagebox.showerror("오류", f"플레이리스트 다운로드 중 오류 발생: {e}")

def process_download_queue(path, progress_var, file_format):
    """대기열에서 다음 비디오를 다운로드합니다."""
    global current_download
    if download_queue:
        current_download = download_queue.pop(0)  # 대기열에서 비디오 URL 가져오기
        threading.Thread(target=download_youtube_video, args=(current_download, path, progress_var, file_format, settings["quality"], None)).start()
    else:
        messagebox.showinfo("완료", "모든 다운로드가 완료되었습니다!")

def on_progress(stream, chunk, bytes_remaining, yt, progress_var):
    """다운로드 진행률을 업데이트합니다."""
    total_size = yt.filesize  # 전체 파일 크기
    percent_complete = (100 * (total_size - bytes_remaining)) / total_size  # 진행률 계산
    progress_var.set(percent_complete)  # 진행률 변수 업데이트

def start_download():
    """비디오 다운로드를 시작합니다."""
    url = url_entry.get()  # URL 입력란에서 URL 가져오기
    selected_format = format_var.get()  # 선택된 파일 형식 가져오기
    selected_quality = quality_var.get()  # 선택된 해상도 가져오기
    filename = simpledialog.askstring("파일 이름", "다운로드할 파일의 이름을 입력하세요:", parent=root)  # 파일 이름 입력 받기

    # 유효성 검사
    if not url:
        messagebox.showwarning("경고", "URL을 입력하세요.")
        return
    if not selected_format:
        messagebox.showwarning("경고", "파일 형식을 선택하세요.")
        return
    path = download_path.get()  # 다운로드 경로 가져오기
    if not path:
        messagebox.showwarning("경고", "다운로드 경로를 선택하세요.")
        return

    progress_var.set(0)  # 진행률 초기화
    download_button.config(state=tk.DISABLED)  # 다운로드 버튼 비활성화
    threading.Thread(target=download_youtube_video, args=(url, path, progress_var, selected_format, selected_quality, filename)).start()

def start_playlist_download():
    """플레이리스트 다운로드를 시작합니다."""
    playlist_url = url_entry.get()  # 플레이리스트 URL 가져오기
    selected_format = format_var.get()  # 선택된 파일 형식 가져오기

    # 유효성 검사
    if not playlist_url:
        messagebox.showwarning("경고", "플레이리스트 URL을 입력하세요.")
        return
    path = download_path.get()  # 다운로드 경로 가져오기
    if not path:
        messagebox.showwarning("경고", "다운로드 경로를 선택하세요.")
        return

    progress_var.set(0)  # 진행률 초기화
    download_button.config(state=tk.DISABLED)  # 다운로드 버튼 비활성화
    threading.Thread(target=download_playlist, args=(playlist_url, path, progress_var, selected_format)).start()

def select_download_path():
    """파일 탐색기를 열어 다운로드 경로를 선택합니다."""
    path = filedialog.askdirectory()  # 디렉토리 선택 대화상자 열기
    download_path.set(path)  # 선택한 경로 업데이트

def show_download_history():
    """다운로드 히스토리를 표시합니다."""
    history_window = tk.Toplevel(root)  # 새로운 윈도우 생성
    history_window.title("다운로드 히스토리")  # 히스토리 창 제목 설정
    history_text = tk.Text(history_window, wrap='word')  # 텍스트 위젯 생성
    history_text.pack(expand=True, fill='both')  # 텍스트 위젯 배치

    for title in download_history:
        history_text.insert(tk.END, title + "\n")  # 히스토리 추가
    history_text.config(state=tk.DISABLED)  # 읽기 전용

def cancel_download_thread():
    """현재 다운로드를 취소합니다."""
    global cancel_download
    cancel_download = True
    if is_downloading:
        messagebox.showinfo("취소", "다운로드가 취소되었습니다.")

# GUI 설정
root = tk.Tk()
root.title("YouTube 비디오 다운로드")  # 윈도우 제목 설정

# 기본 설정 로드
load_settings()

# 다운로드 경로 변수
download_path = tk.StringVar(value=settings["download_path"])

# 프레임 생성 및 중앙 정렬
frame = tk.Frame(root)
frame.pack(expand=True)  # 프레임을 가능한 공간에 맞게 확장

# URL 입력 레이블 및 입력란
tk.Label(frame, text="유튜브 영상/플레이리스트 URL:").pack(pady=5)  # 레이블
url_entry = tk.Entry(frame, width=50)  # 입력란
url_entry.pack(pady=5)  # 입력란 배치

# 파일 형식 선택 라디오 버튼
format_var = tk.StringVar(value=settings["file_format"])  # 기본값을 설정
tk.Label(frame, text="파일 형식 선택:").pack(pady=5)  # 형식 선택 레이블
tk.Radiobutton(frame, text="MP4", variable=format_var, value='mp4').pack(anchor=tk.W)  # MP4 라디오 버튼
tk.Radiobutton(frame, text="MP3", variable=format_var, value='mp3').pack(anchor=tk.W)  # MP3 라디오 버튼
tk.Radiobutton(frame, text="AVI", variable=format_var, value='avi').pack(anchor=tk.W)  # AVI 라디오 버튼

# 해상도 선택 드롭다운
quality_var = tk.StringVar(value=settings["quality"])  # 기본 해상도 설정
tk.Label(frame, text="해상도 선택:").pack(pady=5)  # 해상도 선택 레이블
quality_options = ['360p', '720p', '1080p']
quality_menu = tk.OptionMenu(frame, quality_var, *quality_options)
quality_menu.pack(pady=5)  # 해상도 선택 메뉴 배치

# 다운로드 경로 선택 버튼
tk.Button(frame, text="다운로드 경로 선택", command=select_download_path).pack(pady=10)

# 다운로드 버튼
download_button = tk.Button(frame, text="비디오 다운로드", command=start_download)  # 버튼 클릭 시 비디오 다운로드 시작
download_button.pack(pady=5)  # 버튼 배치

# 플레이리스트 다운로드 버튼
playlist_button = tk.Button(frame, text="플레이리스트 다운로드", command=start_playlist_download)  # 버튼 클릭 시 플레이리스트 다운로드 시작
playlist_button.pack(pady=5)  # 버튼 배치

# 진행률 표시 바
progress_var = tk.DoubleVar()  # 진행률 변수 생성
progress_bar = Progressbar(frame, variable=progress_var, maximum=100)  # 진행률 바 생성
progress_bar.pack(pady=10)  # 진행률 바 배치

# 다운로드 히스토리 버튼
history_button = tk.Button(frame, text="다운로드 히스토리", command=show_download_history)
history_button.pack(pady=5)  # 버튼 배치

# 다운로드 취소 버튼
cancel_button = tk.Button(frame, text="다운로드 취소", command=cancel_download_thread)
cancel_button.pack(pady=5)  # 버튼 배치

# 검색 기능 추가
search_frame = tk.Frame(root)
search_frame.pack(pady=10)

search_entry = tk.Entry(search_frame, width=50)
search_entry.pack(side=tk.LEFT)

search_button = tk.Button(search_frame, text="검색", command=search_button_clicked)
search_button.pack(side=tk.LEFT)

# 검색 결과 표시 프레임
results_frame = tk.Frame(root)
results_frame.pack(pady=10)

# 메인 루프 시작
root.mainloop()
