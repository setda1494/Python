import pygame
import random
import os
import time

# 게임 설정
WIDTH, HEIGHT = 300, 600
BLOCK_SIZE = 30
ROWS, COLS = HEIGHT // BLOCK_SIZE, WIDTH // BLOCK_SIZE

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),  # Cyan
    (255, 165, 0),  # Orange
    (0, 0, 255),  # Blue
    (255, 0, 0),  # Red
    (255, 255, 0),  # Yellow
    (128, 0, 128),  # Purple
    (0, 255, 0),  # Green
    (255, 192, 203)  # Pink
]

SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[0, 1, 1], [1, 1, 1]],  # U
]

SCORE_FILE = 'high_score.txt'


# 게임 통계 저장용 클래스
class GameStats:

    def __init__(self):
        self.games_played = 0
        self.total_score = 0
        self.average_score = 0

    def update_stats(self, score):
        self.games_played += 1
        self.total_score += score
        self.average_score = self.total_score / self.games_played

    def save_stats(self):
        with open('game_stats.txt', 'w') as f:
            f.write(
                f"{self.games_played},{self.total_score},{self.average_score}\n"
            )

    def load_stats(self):
        if os.path.exists('game_stats.txt'):
            with open('game_stats.txt', 'r') as f:
                data = f.read().strip().split(',')
                self.games_played = int(data[0])
                self.total_score = int(data[1])
                self.average_score = float(data[2])


def load_high_score():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, 'r') as f:
            return int(f.read().strip())
    return 0


def save_high_score(score):
    with open(SCORE_FILE, 'w') as f:
        f.write(str(score))


class Tetris:

    def __init__(self):
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.current_shape = self.new_shape()
        self.current_position = [0, COLS // 2 - 1]
        self.score = 0
        self.high_score = load_high_score()
        self.game_over = False
        self.speed = 500  # 블록 떨어지는 속도 (밀리초)
        self.clock = pygame.time.Clock()
        self.level = 1  # 난이도 레벨 추가
        self.stats = GameStats()  # GameStats 인스턴스 생성
        self.stats.load_stats()  # 통계 로드

    def new_shape(self):
        shape = random.choice(SHAPES)
        color = random.choice(COLORS)
        return shape, color

    def draw_board(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board[row][col]:
                    pygame.draw.rect(surface, self.board[row][col],
                                     (col * BLOCK_SIZE, row * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE))
                    # 애니메이션 효과: 블록이 떨어질 때 부드럽게 표시
                    pygame.draw.rect(surface, (255, 255, 255),
                                     (col * BLOCK_SIZE, row * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_shape(self, surface):
        shape, color = self.current_shape
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    pygame.draw.rect(
                        surface, color,
                        ((self.current_position[1] + c) * BLOCK_SIZE,
                         (self.current_position[0] + r) * BLOCK_SIZE,
                         BLOCK_SIZE, BLOCK_SIZE))
                    # 애니메이션 효과: 블록이 떨어질 때 부드럽게 표시
                    pygame.draw.rect(
                        surface, (255, 255, 255),
                        ((self.current_position[1] + c) * BLOCK_SIZE,
                         (self.current_position[0] + r) * BLOCK_SIZE,
                         BLOCK_SIZE, BLOCK_SIZE), 1)

    def rotate_shape(self):
        self.current_shape = (list(zip(*self.current_shape[0][::-1])),
                              self.current_shape[1])

    def move_shape(self, dx):
        self.current_position[1] += dx
        if self.check_collision():
            self.current_position[1] -= dx  # 원래 위치로 되돌리기

    def drop_shape(self):
        self.current_position[0] += 1
        if self.check_collision():
            self.current_position[0] -= 1
            self.lock_shape()
            self.clear_lines()
            self.current_shape = self.new_shape()
            self.current_position = [0, COLS // 2 - 1]
            if self.check_collision():
                self.game_over = True

    def check_collision(self):
        shape, _ = self.current_shape
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    if (self.current_position[0] + r >= ROWS
                            or self.current_position[1] + c < 0
                            or self.current_position[1] + c >= COLS
                            or self.board[self.current_position[0] +
                                          r][self.current_position[1] + c]):
                        return True
        return False

    def lock_shape(self):
        shape, color = self.current_shape
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    self.board[self.current_position[0] +
                               r][self.current_position[1] + c] = color

    def clear_lines(self):
        lines_cleared = 0
        for r in range(ROWS - 1, -1, -1):
            if all(self.board[r]):
                lines_cleared += 1
                del self.board[r]
                self.board.insert(0, [0 for _ in range(COLS)])
        if lines_cleared > 0:
            self.update_score(lines_cleared)

    def update_score(self, lines_cleared):
        self.score += lines_cleared * 100
        # 난이도 조절: 점수에 따라 레벨 증가
        if self.score // 500 > self.level:
            self.level += 1
            self.speed = max(100, self.speed - 50)  # 속도 증가
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)

    def reset(self):
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.current_shape = self.new_shape()
        self.current_position = [0, COLS // 2 - 1]
        self.score = 0
        self.game_over = False
        self.level = 1  # 레벨 리셋


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    game = Tetris()

    while True:
        screen.fill(BLACK)
        game.draw_board(screen)
        game.draw_shape(screen)

        # 점수 및 통계 표시
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {game.score}", True, WHITE)
        high_score_text = font.render(f"High Score: {game.high_score}", True,
                                      WHITE)
        level_text = font.render(f"Level: {game.level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 50))
        screen.blit(level_text, (10, 90))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.stats.save_stats()  # 게임 종료 시 통계 저장
                print("Game exited.")
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move_shape(-1)  # 블록을 왼쪽으로 이동
                elif event.key == pygame.K_RIGHT:
                    game.move_shape(1)  # 블록을 오른쪽으로 이동
                elif event.key == pygame.K_UP:
                    game.rotate_shape()  # 블록 회전
                elif event.key == pygame.K_DOWN:
                    game.drop_shape()  # 블록을 빠르게 떨어뜨림

        # 블록 떨어뜨리기
        game.drop_shape()

        # FPS 조절
        clock.tick(60)  # FPS 조절
        pygame.display.flip()


if __name__ == "__main__":
    main()
