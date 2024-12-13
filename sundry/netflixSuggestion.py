import tkinter as tk
from tkinter import messagebox, simpledialog
import requests
import random
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# RapidAPI 설정
RAPIDAPI_HOST = "moviesdatabase.p.rapidapi.com"
RAPIDAPI_KEY = "YOUR_RAPIDAPI_KEY"  # RapidAPI에서 발급받은 API 키

# MovieLens API 설정 (가상의 URL)
MOVIELENS_URL = "https://movielens.org/api"  # 실제 MovieLens API URL로 변경 필요

# 사용자 데이터 초기화
user_data = {
    "watched_movies": [],      # 사용자가 시청한 영화 목록
    "favorite_movies": [],     # 사용자가 즐겨찾는 영화 목록
    "preferred_genres": [],    # 사용자가 선호하는 장르 목록
    "feedback": {},            # 영화에 대한 사용자 피드백 저장
    "recommendations": {       # 추천 영화 목록
        "popular": [],
        "latest": [],
        "high_rated": []
    },
    "user_ratings": {}         # 사용자가 각 영화에 부여한 평점 저장
}

def fetch_movies_from_netflix(genre):
    """RapidAPI를 통해 넷플릭스에서 장르에 맞는 영화 목록을 가져옵니다."""
    url = f"https://{RAPIDAPI_HOST}/films"
    querystring = {"genre": genre, "platform": "netflix"}  # 넷플릭스에서만 검색
    headers = {
        'x-rapidapi-host': RAPIDAPI_HOST,
        'x-rapidapi-key': RAPIDAPI_KEY
    }
    
    try:
        # API 호출
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        return response.json().get("results", [])  # 영화 목록 반환
    except requests.exceptions.RequestException as e:
        messagebox.showerror("오류", f"영화 데이터를 가져오는 데 실패했습니다: {e}")  # 오류 처리
        return []

def fetch_recommendations_from_movielens():
    """MovieLens API를 통해 추천 영화를 가져옵니다."""
    url = f"{MOVIELENS_URL}/recommendations"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        return response.json()  # 추천 영화 목록 반환
    except requests.exceptions.RequestException as e:
        messagebox.showerror("오류", f"추천 영화를 가져오는 데 실패했습니다: {e}")  # 오류 처리
        return []

def hybrid_recommendation():
    """하이브리드 추천 시스템 구현"""
    if not user_data["watched_movies"]:
        return []  # 시청한 영화가 없으면 추천하지 않음

    # 사용자의 평점을 기반으로 클러스터링
    ratings = np.array(list(user_data["user_ratings"].values()))  # 사용자 평점 배열로 변환
    if ratings.size == 0:
        return []  # 평점이 없으면 추천하지 않음

    # KMeans 클러스터링
    kmeans = KMeans(n_clusters=3)  # 클러스터 수 설정
    clusters = kmeans.fit_predict(ratings.reshape(-1, 1))  # 평점을 클러스터링

    # 각 클러스터에서 추천 영화 선택
    recommendations = []
    for cluster in np.unique(clusters):
        cluster_movies = [movie for idx, movie in enumerate(user_data["watched_movies"]) if clusters[idx] == cluster]
        if cluster_movies:
            recommendations.append(random.choice(cluster_movies))  # 클러스터에서 랜덤으로 영화 선택
    return recommendations

def find_common_movies(netflix_movies, movielens_movies):
    """넷플릭스 영화와 MovieLens 영화에서 공통된 영화를 찾습니다."""
    netflix_titles = {movie['title'] for movie in netflix_movies}  # 넷플릭스 영화 제목 집합
    # 공통 영화 목록 생성
    common_movies = [movie for movie in movielens_movies if movie['title'] in netflix_titles]
    return common_movies

def recommend_video(method):
    """추천 영화를 제공합니다."""
    selected_genre = genre_var.get()  # 선택된 장르 가져오기
    if selected_genre:
        # 사용자 선호 장르 업데이트
        if selected_genre not in user_data["preferred_genres"]:
            user_data["preferred_genres"].append(selected_genre)

        # 넷플릭스와 MovieLens에서 영화 목록 가져오기
        netflix_movies = fetch_movies_from_netflix(selected_genre)
        movielens_movies = fetch_recommendations_from_movielens()
        
        if netflix_movies and movielens_movies:
            # 추천 방식에 따라 영화 목록 업데이트
            if method == "popular":
                user_data["recommendations"]["popular"] = find_common_movies(netflix_movies, movielens_movies)
            elif method == "latest":
                user_data["recommendations"]["latest"] = netflix_movies[:5]  # 최신 5개 영화
            elif method == "high_rated":
                user_data["recommendations"]["high_rated"] = sorted(netflix_movies, key=lambda x: x.get('rating', 0), reverse=True)[:5]  # 높은 평점 상위 5개 영화

            # 하이브리드 추천 추가
            user_data["recommendations"]["hybrid"] = hybrid_recommendation()

            # 추천 영화 목록에서 하나 선택
            if user_data["recommendations"][method]:
                recommended_movie = random.choice(user_data["recommendations"][method])
                user_data["watched_movies"].append(recommended_movie['title'])  # 시청 기록에 추가
                # 추천 영화 정보 표시
                message = (f"추천 영화: {recommended_movie['title']}\n"
                           f"설명: {recommended_movie.get('description', '정보 없음')}\n"
                           f"별점: {recommended_movie.get('rating', '정보 없음')}")
                messagebox.showinfo("추천 영상", message)

                # 사용자 피드백 요청
                feedback = simpledialog.askstring("피드백", f"{recommended_movie['title']}에 대한 피드백을 입력하세요:")
                if feedback:
                    user_data["feedback"][recommended_movie['title']] = feedback
            else:
                messagebox.showwarning("경고", "추천할 영화가 없습니다.")
        else:
            messagebox.showwarning("경고", "추천할 영화가 없습니다.")
    else:
        messagebox.showwarning("경고", "장르를 선택하세요.")

def show_stats():
    """사용자 통계를 보여줍니다."""
    total_watched = len(user_data["watched_movies"])  # 총 시청한 영화 수
    preferred_genres = ', '.join(user_data["preferred_genres"])  # 선호 장르 목록 생성
    
    # 통계 정보 표시
    message = (f"총 시청한 영화 수: {total_watched}\n"
               f"선호 장르: {preferred_genres if preferred_genres else '없음'}")
    messagebox.showinfo("사용자 통계", message)

def visualize_data():
    """사용자의 시청 기록을 시각화합니다."""
    genres = user_data["preferred_genres"]  # 사용자 선호 장르 목록
    # 각 장르에 대해 시청한 영화 수 계산
    genre_counts = {genre: user_data["watched_movies"].count(genre) for genre in genres}
    
    # 데이터 시각화
    plt.bar(genre_counts.keys(), genre_counts.values())
    plt.xlabel('장르')
    plt.ylabel('시청한 영화 수')
    plt.title('장르별 시청 통계')
    plt.xticks(rotation=45)  # X축 레이블 회전
    plt.tight_layout()  # 레이아웃 최적화
    plt.show()

# GUI 설정
root = tk.Tk()
root.title("넷플릭스 영상 추천 프로그램")

# 장르 선택 레이블 및 드롭다운
tk.Label(root, text="추천할 장르를 선택하세요:").pack(pady=10)

genre_var = tk.StringVar(value="액션")  # 기본값 설정
genres = ["액션", "코미디", "드라마", "SF", "스릴러"]  # 예시 장르
genre_menu = tk.OptionMenu(root, genre_var, *genres)
genre_menu.pack(pady=10)

# 추천 버튼
popular_button = tk.Button(root, text="인기 영화 추천", command=lambda: recommend_video("popular"))
popular_button.pack(pady=5)

latest_button = tk.Button(root, text="최신 영화 추천", command=lambda: recommend_video("latest"))
latest_button.pack(pady=5)

high_rated_button = tk.Button(root, text="높은 평점 영화 추천", command=lambda: recommend_video("high_rated"))
high_rated_button.pack(pady=5)

# 통계 버튼
stats_button = tk.Button(root, text="사용자 통계", command=show_stats)
stats_button.pack(pady=10)

# 데이터 시각화 버튼
visualize_button = tk.Button(root, text="시청 데이터 시각화", command=visualize_data)
visualize_button.pack(pady=10)

# 메인 루프 시작
root.mainloop()
