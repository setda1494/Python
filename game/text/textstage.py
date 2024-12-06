import tkinter as tk
import time

def log_result(message):
    """결과를 로그처럼 텍스트 박스에 추가하는 함수"""
    result_text.insert(tk.END, message + "\n")
    result_text.see(tk.END)  # 항상 가장 아래로 스크롤

def execute_choice(choice):
    log_result("선택한 옵션: " + ("수락" if choice == "accept" else "거절"))
    character_action(choice)

def character_action(choice):
    action_label.config(text="캐릭터 행동 중...")
    root.update()
    time.sleep(1)  # 애니메이션 시뮬레이션
    if choice == "accept":
        log_result("캐릭터가 선택을 수락했습니다!")
    else:
        log_result("캐릭터가 선택을 거절했습니다!")

# 메인 윈도우 생성
root = tk.Tk()
root.title("스테이지 화면")

# 상단 흰색 영역 (캐릭터 애니메이션 표시)
action_label = tk.Label(root, text="", bg='white', height=5, width=50)
action_label.pack(pady=10)

# 갈색 영역 (결과 로그 표시)
result_text = tk.Text(root, bg='brown', height=10, width=50)
result_text.pack()

# 하단 회색 영역 (버튼)
button_frame = tk.Frame(root, bg='gray')
button_frame.pack(side='bottom', fill='x')

# 빨간색 버튼 (거절)
reject_button = tk.Button(button_frame, text="거절", bg='red', command=lambda: execute_choice("reject"))
reject_button.pack(side='left', expand=True, fill='both')

# 파란색 버튼 (수락)
accept_button = tk.Button(button_frame, text="수락", bg='blue', command=lambda: execute_choice("accept"))
accept_button.pack(side='right', expand=True, fill='both')

# 메인 루프 시작
root.mainloop()
