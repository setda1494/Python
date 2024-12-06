import tkinter as tk

def open_window(window_name):
    print(f"{window_name} 창이 열렸습니다.")

# 메인 윈도우 생성
root = tk.Tk()
root.title("게임 메인 화면")

# 상단 빨간색 영역
header = tk.Frame(root, bg='red', height=50)
header.pack(fill='x')

# 버튼이 들어갈 프레임
button_frame = tk.Frame(root)
button_frame.pack(side='bottom', fill='x')

# 파란색 버튼 (상점)
blue_button = tk.Button(button_frame, text="상점", bg='blue', command=lambda: open_window("상점"))
blue_button.pack(side='left', expand=True, fill='both')

# 회색 버튼 (장비창)
gray_button = tk.Button(button_frame, text="장비창", bg='gray', command=lambda: open_window("장비창"))
gray_button.pack(side='left', expand=True, fill='both')

# 노란색 버튼 (스테이지 보기)
yellow_button = tk.Button(button_frame, text="스테이지 보기", bg='yellow', command=lambda: open_window("스테이지 보기"))
yellow_button.pack(side='left', expand=True, fill='both')

# 초록색 버튼 (스텟 업그레이드)
green_button = tk.Button(button_frame, text="스텟 업그레이드", bg='green', command=lambda: open_window("스텟 업그레이드"))
green_button.pack(side='left', expand=True, fill='both')

# 갈색 버튼 (던전 선택)
brown_button = tk.Button(button_frame, text="던전 선택", bg='brown', command=lambda: open_window("던전 선택"))
brown_button.pack(side='left', expand=True, fill='both')

# 메인 루프 시작
root.mainloop()
