import tkinter as tk
import random
import copy
import time

class Game2048:
    def __init__(self, master):
        self.master = master
        self.master.title("2048")
        
        self.high_score = 0  # 최고 점수 초기화
        self.score = 0       # 현재 점수 초기화
        self.move_count = 0  # 이동 횟수 초기화
        self.board = [[0] * 4 for _ in range(4)]  # 4x4 게임 보드 초기화
        self.undo_stack = []  # Undo 히스토리 저장
        self.start_time = None  # 게임 시작 시간
        self.play_time = 0  # 총 플레이 시간
        
        # 게임 UI 요소 설정
        self.canvas = tk.Canvas(master, width=400, height=400, bg='lightgray')
        self.canvas.pack()
        
        self.restart_button = tk.Button(master, text="재시작", command=self.restart_game)
        self.restart_button.pack(pady=10)

        self.score_label = tk.Label(master, text=f"점수: {self.score}")
        self.score_label.pack()

        self.high_score_label = tk.Label(master, text=f"최고 점수: {self.high_score}")
        self.high_score_label.pack()

        self.move_count_label = tk.Label(master, text=f"이동 횟수: {self.move_count}")
        self.move_count_label.pack()

        self.play_time_label = tk.Label(master, text="플레이 시간: 0초")
        self.play_time_label.pack()

        self.initialize_game()  # 게임 초기화
        self.draw_board()       # 보드 그리기
        self.master.bind("<Key>", self.key_press)  # 키 이벤트 바인딩

    def initialize_game(self):
        # 게임 초기화
        self.board = [[0] * 4 for _ in range(4)]
        self.score = 0
        self.move_count = 0
        self.undo_stack.clear()  # Undo 히스토리 초기화
        self.start_time = time.time()  # 게임 시작 시간 기록
        self.add_new_tile()  # 새로운 타일 추가
        self.add_new_tile()  # 새로운 타일 추가

    def restart_game(self):
        # 게임 재시작
        self.initialize_game()
        self.draw_board()

    def add_new_tile(self):
        # 빈 타일에 새로운 타일 추가
        empty_tiles = [(i, j) for i in range(4) for j in range(4) if self.board[i][j] == 0]
        if empty_tiles:
            i, j = random.choice(empty_tiles)
            self.board[i][j] = 2 if random.random() < 0.9 else 4

    def draw_board(self):
        # 보드 그리기
        self.canvas.delete("all")  # 기존 그래픽 삭제
        for i in range(4):
            for j in range(4):
                value = self.board[i][j]
                x0, y0 = j * 100, i * 100
                x1, y1 = x0 + 100, y0 + 100
                color = self.get_color(value)  # 타일 색상 설정
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color)  # 타일 그리기
                self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=str(value) if value != 0 else "", font=('Arial', 24))

        # 점수 및 이동 횟수 업데이트
        self.score_label.config(text=f"점수: {self.score}")
        self.high_score_label.config(text=f"최고 점수: {self.high_score}")
        self.move_count_label.config(text=f"이동 횟수: {self.move_count}")

        # 총 플레이 시간 계산 및 업데이트
        if self.start_time is not None:
            self.play_time = int(time.time() - self.start_time)
            self.play_time_label.config(text=f"플레이 시간: {self.play_time}초")

    def get_color(self, value):
        # 타일 값에 따른 색상 설정
        colors = {
            0: 'lightgray',
            2: '#eee4da',
            4: '#ede0c8',
            8: '#f2b179',
            16: '#f59563',
            32: '#f67c5f',
            64: '#f67c5f',
            128: '#edcf72',
            256: '#edcc61',
            512: '#edc850',
            1024: '#edc53f',
            2048: '#edc22e',
        }
        return colors.get(value, '#3c3a32')  # 기본 색상 반환

    def key_press(self, event):
        # 키 입력 처리
        if event.keysym in ['Up', 'Down', 'Left', 'Right', 'u']:
            if event.keysym in ['Up', 'Down', 'Left', 'Right']:
                self.save_state()  # 현재 상태 저장
                if event.keysym == 'Up':
                    self.move_up()
                elif event.keysym == 'Down':
                    self.move_down()
                elif event.keysym == 'Left':
                    self.move_left()
                elif event.keysym == 'Right':
                    self.move_right()
                self.add_new_tile()  # 새로운 타일 추가
                self.draw_board()  # 보드 다시 그리기
                if self.check_game_over():
                    self.canvas.create_text(200, 200, text="게임 오버!", font=('Arial', 48), fill='red')
                    self.update_high_score()  # 최고 점수 업데이트
                    self.display_statistics()  # 통계 표시
            elif event.keysym == 'u':  # Undo 기능
                self.undo()

    def update_high_score(self):
        # 최고 점수 업데이트
        if self.score > self.high_score:
            self.high_score = self.score
        self.high_score_label.config(text=f"최고 점수: {self.high_score}")

    def check_game_over(self):
        # 게임 종료 조건 체크
        return not any(0 in row for row in self.board) and not any(
            self.board[i][j] == self.board[i][j + 1] or self.board[i][j] == self.board[i + 1][j]
            for i in range(4) for j in range(4 - 1)
        )

    def compress(self, board):
        # 보드 압축
        new_board = [[0] * 4 for _ in range(4)]
        for i in range(4):
            pos = 0
            for j in range(4):
                if board[i][j] != 0:
                    new_board[i][pos] = board[i][j]
                    pos += 1
        return new_board

    def merge(self, board):
        # 보드 병합
        for i in range(4):
            for j in range(3):
                if board[i][j] == board[i][j + 1] and board[i][j] != 0:
                    board[i][j] *= 2
                    self.score += board[i][j]
                    board[i][j + 1] = 0
        return board

    def move_left(self):
        # 왼쪽으로 이동
        self.board = self.compress(self.board)
        self.board = self.merge(self.board)
        self.board = self.compress(self.board)
        self.move_count += 1

    def move_right(self):
        # 오른쪽으로 이동
        self.board = [row[::-1] for row in self.board]
        self.move_left()
        self.board = [row[::-1] for row in self.board]

    def move_up(self):
        # 위로 이동
        self.board = self.transpose(self.board)
        self.move_left()
        self.board = self.transpose(self.board)

    def move_down(self):
        # 아래로 이동
        self.board = self.transpose(self.board)
        self.move_right()
        self.board = self.transpose(self.board)

    def transpose(self, board):
        # 보드 전치
        return [[board[j][i] for j in range(4)] for i in range(4)]

    def save_state(self):
        # 현재 보드 상태를 스택에 저장
        self.undo_stack.append(copy.deepcopy(self.board))

    def undo(self):
        # Undo 기능
        if self.undo_stack:
            self.board = self.undo_stack.pop()  # 마지막 상태를 꺼내서 복원
            self.draw_board()
            self.move_count -= 1  # Undo 시 이동 횟수 감소

    def display_statistics(self):
        # 게임 종료 후 통계 표시
        stats_message = f"최고 점수: {self.high_score}\n최종 점수: {self.score}\n이동 횟수: {self.move_count}\n플레이 시간: {self.play_time}초"
        self.canvas.create_text(200, 200, text=stats_message, font=('Arial', 24), fill='black')

if __name__ == "__main__":
    root = tk.Tk()
    game = Game2048(root)
    root.mainloop()
