import pygame
import random
import sys

# 초기화
pygame.init()

# 색상 정의
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
BLACK = (0, 0, 0)

COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE]

# 화면 설정
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 8
TILE_SIZE = WIDTH // GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced Match-3 Game")


# 타일 클래스
class Tile:

    def __init__(self, color, is_special=False, special_type=None):
        self.color = color
        self.is_special = is_special  # 특수 타일 여부
        self.special_type = special_type  # 특수 타일의 종류

    def draw(self, x, y):
        pygame.draw.rect(screen, self.color,
                         (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        if self.is_special:
            pygame.draw.circle(screen, BLACK, (x * TILE_SIZE + TILE_SIZE // 2,
                                               y * TILE_SIZE + TILE_SIZE // 2),
                               TILE_SIZE // 4)


# 보드 초기화
def init_board():
    board = [[Tile(random.choice(COLORS)) for _ in range(GRID_SIZE)]
             for _ in range(GRID_SIZE)]
    return board


# 매치 확인
def check_matches(board):
    matches = []
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE - 2):
            if board[y][x] and board[y][x + 1] and board[y][x + 2] and \
               board[y][x].color == board[y][x + 1].color == board[y][x + 2].color:
                matches.extend([(y, x), (y, x + 1), (y, x + 2)])
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE - 2):
            if board[y][x] and board[y + 1][x] and board[y + 2][x] and \
               board[y][x].color == board[y + 1][x].color == board[y + 2][x].color:
                matches.extend([(y, x), (y + 1, x), (y + 2, x)])
    return list(set(matches))


# 매치된 타일 제거 및 아래로 내리기
def remove_matches(board, matches):
    for y, x in matches:
        board[y][x] = None
    for x in range(GRID_SIZE):
        empty_tiles = [y for y in range(GRID_SIZE) if board[y][x] is None]
        for y in range(GRID_SIZE - 1, -1, -1):
            if board[y][x] is not None and empty_tiles:
                empty_y = empty_tiles.pop()
                board[empty_y][x], board[y][x] = board[y][x], None


# 새 타일 추가
def fill_board(board):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if board[y][x] is None:
                is_special = random.random() < 0.1  # 10% 확률로 특수 타일 생성
                special_type = None
                if is_special:
                    special_type = random.choice(['explode',
                                                  'line'])  # 특수 타일 유형
                board[y][x] = Tile(random.choice(COLORS), is_special,
                                   special_type)


# 보드 그리기
def draw_board(board):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if board[y][x] is not None:
                board[y][x].draw(x, y)


# 점수 및 정보 표시
def display_info(score, combo=0, time_left=None, level_goal=None):
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f'Score: {score}', True, (0, 0, 0))
    combo_text = font.render(f'Combo: {combo}', True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    screen.blit(combo_text, (10, 50))
    if time_left is not None:
        time_text = font.render(f'Time Left: {time_left}', True, (0, 0, 0))
        screen.blit(time_text, (10, 90))
    if level_goal is not None:
        goal_text = font.render(f'Goal: {level_goal}', True, (0, 0, 0))
        screen.blit(goal_text, (10, 130))


# 게임 종료
def game_over():
    pygame.quit()
    sys.exit()


# 이벤트 처리
def handle_events(selected_tile):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            x, y = mouse_x // TILE_SIZE, mouse_y // TILE_SIZE
            return (y, x) if selected_tile is None else None
    return selected_tile


# AI 상대방
def ai_opponent(board, difficulty):
    potential_moves = [(y, x, y2, x2) for y in range(GRID_SIZE)
                       for x in range(GRID_SIZE)
                       for y2, x2 in [(y, x + 1), (y + 1, x)]
                       if y2 < GRID_SIZE and x2 < GRID_SIZE]

    if potential_moves:
        move = max(
            potential_moves, key=lambda m: evaluate_move(board, m)
        ) if difficulty != "easy" else random.choice(potential_moves)
        if move:
            (y1, x1, y2, x2) = move
            board[y1][x1], board[y2][x2] = board[y2][x2], board[y1][x1]


# AI 전략 평가
def evaluate_move(board, move):
    (y1, x1, y2, x2) = move
    board[y1][x1], board[y2][x2] = board[y2][x2], board[y1][x1]
    matches = check_matches(board)
    board[y1][x1], board[y2][x2] = board[y2][x2], board[y1][x1]
    return len(matches)


# 퍼즐 모드
def puzzle_mode():
    score = 0
    board = init_board()
    moves_left = 20
    target_matches = 15
    current_level = 1
    clock = pygame.time.Clock()
    running = True
    selected_tile = None
    combo = 0

    while running:
        screen.fill(WHITE)
        draw_board(board)
        matches = check_matches(board)

        if matches:
            combo += 1
            remove_matches(board, matches)
            fill_board(board)
            score += len(matches) * 10
            target_matches -= len(matches)

            # 레벨 목표 달성 시 레벨 업
            if target_matches <= 0:
                current_level += 1
                target_matches = 15 + (current_level -
                                       1) * 5  # 레벨마다 목표 매치 수 증가
                print(f'Level Up! Now at Level {current_level}.')

        else:
            combo = 0

        display_info(score, combo, level_goal=target_matches)
        selected_tile = handle_events(selected_tile)

        if moves_left <= 0:
            print(f'Puzzle Mode Completed! Score: {score}')
            running = False

        pygame.display.flip()
        clock.tick(30)


# 생존 모드
def survival_mode():
    score = 0
    board = init_board()
    time_limit = 60  # 60초 제한
    start_ticks = pygame.time.get_ticks()
    clock = pygame.time.Clock()
    running = True
    selected_tile = None

    while running:
        screen.fill(WHITE)
        draw_board(board)
        seconds = (pygame.time.get_ticks() - start_ticks) // 1000
        remaining_time = time_limit - seconds
        matches = check_matches(board)

        if matches:
            remove_matches(board, matches)
            fill_board(board)
            score += len(matches) * 5

        display_info(score, time_left=remaining_time)
        selected_tile = handle_events(selected_tile)

        if remaining_time <= 0:
            print(f'Survival Mode Completed! Final Score: {score}')
            running = False

        pygame.display.flip()
        clock.tick(30)


# AI 모드
def ai_mode(difficulty):
    score = 0
    ai_score = 0
    board = init_board()
    clock = pygame.time.Clock()
    running = True
    selected_tile = None

    while running:
        screen.fill(WHITE)
        draw_board(board)

        # 플레이어의 차례
        matches = check_matches(board)
        if matches:
            remove_matches(board, matches)
            fill_board(board)
            score += len(matches) * 5

        display_info(score, level_goal=ai_score)
        selected_tile = handle_events(selected_tile)

        # AI의 차례
        ai_matches = []  # AI 매치 초기화
        if selected_tile is None:
            ai_opponent(board, difficulty)
            ai_matches = check_matches(board)  # AI의 매치 체크
            if ai_matches:
                remove_matches(board, ai_matches)
                fill_board(board)
                ai_score += len(ai_matches) * 5

        # 게임 종료 조건
        if not matches and not ai_matches:
            print(
                f'AI Mode Completed! Player Score: {score}, AI Score: {ai_score}'
            )
            running = False

        pygame.display.flip()
        clock.tick(30)


# 메인 함수
def main():
    # 게임 모드 선택 또는 직접 호출
    puzzle_mode()  # 또는 survival_mode(), ai_mode("easy") 등으로 직접 호출 가능


if __name__ == "__main__":
    main()
