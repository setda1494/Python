import pygame
import random

# 초기화
pygame.init()

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# 화면 크기
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout Game")

# 패들 설정
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 10
paddle_x = (WIDTH - PADDLE_WIDTH) // 2
paddle_y = HEIGHT - 50
paddle_speed = 10

# 공 설정
BALL_SIZE = 10
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_speed_x = 4 * random.choice((1, -1))
ball_speed_y = -4

# 블록 설정
BLOCK_WIDTH = 75
BLOCK_HEIGHT = 20
blocks = []
for i in range(8):
    for j in range(5):
        if j == 0:  # 첫 번째 줄에 강화 블록 추가
            blocks.append((pygame.Rect(i * (BLOCK_WIDTH + 10) + 35,
                                       j * (BLOCK_HEIGHT + 10) + 50,
                                       BLOCK_WIDTH, BLOCK_HEIGHT), 'strong'))
        elif j == 1:  # 두 번째 줄에 파괴 불가능한 블록 추가
            blocks.append(
                (pygame.Rect(i * (BLOCK_WIDTH + 10) + 35,
                             j * (BLOCK_HEIGHT + 10) + 50, BLOCK_WIDTH,
                             BLOCK_HEIGHT), 'indestructible'))
        else:
            blocks.append((pygame.Rect(i * (BLOCK_WIDTH + 10) + 35,
                                       j * (BLOCK_HEIGHT + 10) + 50,
                                       BLOCK_WIDTH, BLOCK_HEIGHT), 'normal'))

# 점수 및 레벨
score = 0
level = 1
high_score = 0
played_levels = 0

# 게임 루프 설정
running = True
clock = pygame.time.Clock()


def reset_game():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, paddle_x, score, level, blocks
    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2
    ball_speed_x = 4 * random.choice((1, -1))
    ball_speed_y = -4
    paddle_x = (WIDTH - PADDLE_WIDTH) // 2
    score = 0
    level = 1
    generate_blocks()


def generate_blocks():
    global blocks
    blocks = []
    for i in range(8):
        for j in range(5):
            if j == 0:
                blocks.append(
                    (pygame.Rect(i * (BLOCK_WIDTH + 10) + 35,
                                 j * (BLOCK_HEIGHT + 10) + 50, BLOCK_WIDTH,
                                 BLOCK_HEIGHT), 'strong'))
            elif j == 1:
                blocks.append(
                    (pygame.Rect(i * (BLOCK_WIDTH + 10) + 35,
                                 j * (BLOCK_HEIGHT + 10) + 50, BLOCK_WIDTH,
                                 BLOCK_HEIGHT), 'indestructible'))
            else:
                blocks.append(
                    (pygame.Rect(i * (BLOCK_WIDTH + 10) + 35,
                                 j * (BLOCK_HEIGHT + 10) + 50, BLOCK_WIDTH,
                                 BLOCK_HEIGHT), 'normal'))


def display_score():
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(
        f'Score: {score}  Level: {level}  High Score: {high_score}', True,
        WHITE)
    screen.blit(score_text, (10, 10))


def display_game_over():
    font = pygame.font.SysFont(None, 48)
    game_over_text = font.render("Game Over", True, RED)
    score_text = font.render(f"Final Score: {score}  Level: {level}", True,
                             WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)

    screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
    screen.blit(score_text, (WIDTH // 2 - 150, HEIGHT // 2))
    screen.blit(restart_text, (WIDTH // 2 - 150, HEIGHT // 2 + 50))


def display_tutorial():
    font = pygame.font.SysFont(None, 36)
    tutorial_texts = [
        "Welcome to Breakout!",
        "Use the LEFT and RIGHT arrow keys to move the paddle.",
        "Break all the blocks to win!", "Good luck!"
    ]

    for i, text in enumerate(tutorial_texts):
        rendered_text = font.render(text, True, WHITE)
        screen.blit(rendered_text,
                    (WIDTH // 2 - 150, HEIGHT // 2 - 100 + i * 30))


def handle_block_collision():
    global score, level, high_score
    for block in blocks:
        rect, block_type = block
        if rect.collidepoint(ball_x + BALL_SIZE // 2, ball_y + BALL_SIZE // 2):
            if block_type == 'strong':
                # 강화 블록은 두 번 맞아야 파괴됨
                blocks.remove(block)
                score += 30  # 강화 블록 점수
                return 2  # 두 번 더 맞아야 파괴됨
            elif block_type == 'indestructible':
                # 파괴 불가능한 블록은 파괴되지 않음
                return 0
            else:  # 일반 블록
                blocks.remove(block)
                score += 20  # 일반 블록 점수
                return 1  # 파괴됨
    return 0


while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 패들 이동
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle_x > 0:
        paddle_x -= paddle_speed
    if keys[pygame.K_RIGHT] and paddle_x < WIDTH - PADDLE_WIDTH:
        paddle_x += paddle_speed

    # 공 이동
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # 공 충돌 처리
    if ball_x <= 0 or ball_x >= WIDTH - BALL_SIZE:
        ball_speed_x *= -1
    if ball_y <= 0:
        ball_speed_y *= -1
    if ball_y >= HEIGHT:
        # 게임 오버 처리
        high_score = max(high_score, score)
        display_game_over()
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    reset_game()
                    break
            if not running:
                break
        continue

    # 패들과 공 충돌 처리
    if (paddle_y < ball_y + BALL_SIZE < paddle_y + PADDLE_HEIGHT
            and paddle_x < ball_x + BALL_SIZE < paddle_x + PADDLE_WIDTH):
        ball_speed_y *= -1
        score += 10  # 점수 증가

    # 블록과 공 충돌 처리
    collision_result = handle_block_collision()
    if collision_result == 1:
        ball_speed_y *= -1
    elif collision_result == 2:
        ball_speed_y *= -1

    # 블록 그리기
    for block in blocks:
        rect, block_type = block
        if block_type == 'strong':
            pygame.draw.rect(screen, YELLOW, rect)  # 강화 블록 색상
        elif block_type == 'indestructible':
            pygame.draw.rect(screen, GREEN, rect)  # 파괴 불가능 블록 색상
        else:
            pygame.draw.rect(screen, RED, rect)  # 일반 블록 색상

    # UI 표시
    display_score()

    pygame.draw.rect(screen, WHITE,
                     (paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.ellipse(screen, GREEN, (ball_x, ball_y, BALL_SIZE, BALL_SIZE))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
