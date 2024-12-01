import pygame
import time
import random
import os

# 초기화
pygame.init()

# 색상 정의
WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

# 게임 화면 크기
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game')

# 스네이크 속도
snake_block = 10
snake_speed = 15

# 폰트 설정
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

# 최고 점수 파일
SCORE_FILE = 'high_score.txt'


def load_high_score():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, 'r') as f:
            return int(f.read().strip())
    return 0


def save_high_score(score):
    with open(SCORE_FILE, 'w') as f:
        f.write(str(score))


def our_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(screen, BLACK, [x[0], x[1], snake_block, snake_block])


def message(msg, color):
    mesg = font_style.render(msg, True, color)
    screen.blit(mesg, [WIDTH / 6, HEIGHT / 3])


def display_score(score, high_score):
    value = score_font.render(f"Score: {score}  High Score: {high_score}",
                              True, WHITE)
    screen.blit(value, [10, 10])


def draw_obstacles(obstacles):
    for obs in obstacles:
        pygame.draw.rect(screen, RED, [obs[0], obs[1], obs[2], obs[3]])


def game_intro():
    while True:
        screen.fill(BLUE)
        message("Welcome to Snake Game!", WHITE)
        message("Press P to Play or Q to Quit", WHITE)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                if event.key == pygame.K_p:
                    return  # 게임 시작


def animate_snake_growth(snake):
    # 스네이크가 성장할 때 애니메이션 효과
    for _ in range(3):  # 3번 애니메이션 효과 적용
        snake.append(snake[-1])  # 스네이크의 마지막 위치를 복사하여 길이를 늘림
        pygame.time.delay(100)  # 지연 시간
        screen.fill(BLUE)
        our_snake(snake_block, snake)
        pygame.display.update()


def gameLoop(mode):  # 메인 게임 루프
    game_over = False
    game_close = False

    x1 = WIDTH / 2
    y1 = HEIGHT / 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    foodx = round(random.randrange(0, WIDTH - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, HEIGHT - snake_block) / 10.0) * 10.0

    # 장애물 생성 (고정 장애물과 움직이는 장애물)
    obstacles = [[
        random.randrange(1, WIDTH // snake_block) * snake_block,
        random.randrange(1, HEIGHT // snake_block) * snake_block, snake_block,
        snake_block
    ] for _ in range(5)]

    moving_obstacle = [
        random.randrange(1, WIDTH // snake_block) * snake_block,
        random.randrange(1, HEIGHT // snake_block) * snake_block
    ]

    high_score = load_high_score()
    score = 0
    start_time = time.time() if mode == "time_limit" else None

    while not game_over:

        while game_close == True:
            screen.fill(BLUE)
            message("You Lost! Press C-Play Again or Q-Quit", RED)
            display_score(score, high_score)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop(mode)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True

        x1 += x1_change
        y1 += y1_change
        screen.fill(BLUE)

        # 음식 그리기
        pygame.draw.rect(screen, GREEN,
                         [foodx, foody, snake_block, snake_block])

        # 장애물 그리기
        draw_obstacles(obstacles)

        # 움직이는 장애물
        moving_obstacle[0] += 2  # 오른쪽으로 이동
        if moving_obstacle[0] > WIDTH:
            moving_obstacle[0] = 0  # 화면을 벗어나면 다시 시작
        pygame.draw.rect(
            screen, RED,
            [moving_obstacle[0], moving_obstacle[1], snake_block, snake_block])

        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        our_snake(snake_block, snake_List)

        # 점수 업데이트
        display_score(score, high_score)

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(
                random.randrange(0, WIDTH - snake_block) / 10.0) * 10.0
            foody = round(
                random.randrange(0, HEIGHT - snake_block) / 10.0) * 10.0
            Length_of_snake += 1
            score += 10
            animate_snake_growth(snake_List)  # 애니메이션 효과

        # 장애물 체크
        for obs in obstacles:
            if snake_Head[0] in range(
                    obs[0], obs[0] + obs[2]) and snake_Head[1] in range(
                        obs[1], obs[1] + obs[3]):
                game_close = True

        # 움직이는 장애물 체크
        if snake_Head[0] in range(moving_obstacle[0], moving_obstacle[0] + snake_block) and \
           snake_Head[1] in range(moving_obstacle[1], moving_obstacle[1] + snake_block):
            game_close = True

        # 최고 점수 업데이트
        if score > high_score:
            high_score = score
            save_high_score(high_score)

        # 시간 제한 모드 처리
        if mode == "time_limit" and start_time:
            elapsed_time = time.time() - start_time
            if elapsed_time > 30:  # 30초 제한
                game_close = True

        pygame.time.Clock().tick(snake_speed)

    pygame.quit()
    quit()


# 게임 시작 전 메뉴 표시
game_intro()
# 게임 모드 선택
mode = 'time_limit'  # 'time_limit' 또는 'survival'로 설정
gameLoop(mode)
