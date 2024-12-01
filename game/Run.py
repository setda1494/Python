import pygame
import random
import os

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
pygame.display.set_caption("Run and Jump Game")

# 최고 점수 파일
SCORE_FILE = "high_score.txt"


# 최고 점수 로드
def load_high_score():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "r") as file:
            return int(file.read().strip())
    return 0


# 최고 점수 저장
def save_high_score(score):
    with open(SCORE_FILE, "w") as file:
        file.write(str(score))


# 캐릭터 클래스
class Player:

    def __init__(self):
        self.rect = pygame.Rect(100, HEIGHT - 60, 50, 50)
        self.jump_speed = 15
        self.gravity = 1
        self.velocity_y = 0
        self.is_jumping = False
        self.animation_frames = [
            pygame.Surface((50, 50)),  # 정지 상태
            pygame.Surface((50, 50)),  # 점프 상태
            pygame.Surface((50, 50)),  # 달리기 상태 1
            pygame.Surface((50, 50)),  # 달리기 상태 2
        ]
        self.animation_frames[0].fill(GREEN)  # 정지 상태
        self.animation_frames[1].fill((0, 200, 0))  # 점프 상태
        self.animation_frames[2].fill((0, 150, 0))  # 달리기 상태 1
        self.animation_frames[3].fill((0, 100, 0))  # 달리기 상태 2
        self.current_frame = 0
        self.frame_counter = 0

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = -self.jump_speed
            self.is_jumping = True

    def update(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # 바닥에 닿으면 점프 상태 초기화
        if self.rect.y >= HEIGHT - 60:
            self.rect.y = HEIGHT - 60
            self.is_jumping = False
            self.velocity_y = 0

        # 애니메이션 프레임 조절
        self.frame_counter += 1
        if self.frame_counter >= 10:  # 프레임 속도
            if self.is_jumping:
                self.current_frame = 1
            else:
                self.current_frame = 2 if self.frame_counter % 20 < 10 else 3  # 달리기 애니메이션
            self.frame_counter = 0

    def draw(self):
        screen.blit(self.animation_frames[self.current_frame],
                    self.rect.topleft)


# 장애물 클래스
class Obstacle:

    def __init__(self):
        self.type = random.choice(["normal", "spike", "moving"])  # 장애물 유형
        self.rect = pygame.Rect(WIDTH, HEIGHT - 60, 50, 50)
        if self.type == "spike":
            self.rect.height = 30  # 스파이크 장애물 높이 조정
        elif self.type == "moving":
            self.rect.y = HEIGHT - 80  # 움직이는 장애물 높이 조정
            self.direction = random.choice([-1, 1])  # 움직임 방향

    def update(self, speed):
        if self.type == "normal":
            self.rect.x -= speed  # 일반 장애물 이동 속도
        elif self.type == "spike":
            self.rect.x -= speed  # 스파이크 장애물 이동 속도
        elif self.type == "moving":
            self.rect.x -= speed  # 움직이는 장애물 이동 속도
            self.rect.y += self.direction * 2  # 위아래로 움직임
            if self.rect.y <= HEIGHT - 100 or self.rect.y >= HEIGHT - 60:
                self.direction *= -1  # 방향 반전

    def draw(self):
        color = RED if self.type == "normal" else BLUE if self.type == "spike" else (
            255, 165, 0)  # 장애물 색상
        pygame.draw.rect(screen, color, self.rect)


# 파워업 아이템 클래스
class PowerUp:

    def __init__(self):
        self.rect = pygame.Rect(WIDTH, random.randint(50, HEIGHT - 100), 30,
                                30)

    def update(self, speed):
        self.rect.x -= speed  # 아이템 이동 속도

    def draw(self):
        pygame.draw.rect(screen, YELLOW, self.rect)  # 아이템 색상


# 게임 상태 변수
player = Player()
obstacles = []
powerups = []
score = 0
high_score = load_high_score()
level = 1
running = True
game_over = False
clock = pygame.time.Clock()


def reset_game():
    global obstacles, powerups, score, level, game_over
    obstacles = []
    powerups = []
    score = 0
    level = 1
    game_over = False


def display_game_over():
    font = pygame.font.SysFont(None, 48)
    game_over_text = font.render("Game Over", True, RED)
    score_text = font.render(f"Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)

    screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 100))
    screen.blit(score_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
    screen.blit(high_score_text, (WIDTH // 2 - 100, HEIGHT // 2))
    screen.blit(restart_text, (WIDTH // 2 - 150, HEIGHT // 2 + 50))


while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:  # 스페이스바로 점프
                player.jump()
            if game_over and event.key == pygame.K_r:  # 게임 오버 시 R 키로 재시작
                reset_game()

    # 장애물 생성
    if not game_over and random.random() < 0.02 + (
            level * 0.01):  # 레벨에 따라 장애물 생성 확률 증가
        obstacles.append(Obstacle())

    # 파워업 아이템 생성
    if not game_over and random.random() < 0.01 + (
            level * 0.005):  # 레벨에 따라 아이템 생성 확률 증가
        powerups.append(PowerUp())

    # 장애물 및 아이템 업데이트
    speed = 5 + (level - 1)  # 레벨이 오를 때마다 장애물 속도 증가
    for obstacle in obstacles:
        obstacle.update(speed)
        if obstacle.rect.x < 0:  # 장애물이 화면을 넘어가면 제거
            obstacles.remove(obstacle)
            score += 1  # 점수 증가

    for powerup in powerups:
        powerup.update(speed)
        if powerup.rect.x < 0:  # 아이템이 화면을 넘어가면 제거
            powerups.remove(powerup)

    # 플레이어 업데이트
    player.update()

    # 충돌 체크
    for obstacle in obstacles:
        if player.rect.colliderect(obstacle.rect):
            game_over = True  # 충돌 시 게임 오버

    # 파워업 아이템 충돌 체크
    for powerup in powerups:
        if player.rect.colliderect(powerup.rect):
            score += 5  # 아이템을 먹으면 점수 증가
            powerups.remove(powerup)  # 아이템 제거

    # 플레이어 그리기
    player.draw()

    # 장애물 그리기
    for obstacle in obstacles:
        obstacle.draw()

    # 아이템 그리기
    for powerup in powerups:
        powerup.draw()

    # 점수 표시
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f'Score: {score}', True, WHITE)
    high_score_text = font.render(f'High Score: {high_score}', True, WHITE)
    level_text = font.render(f'Level: {level}', True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 40))
    screen.blit(level_text, (10, 70))

    # 레벨 증가
    if score > level * 5:  # 5점마다 레벨 증가
        level += 1

    # 최고 점수 업데이트
    if score > high_score:
        high_score = score
        save_high_score(high_score)

    if game_over:
        display_game_over()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
