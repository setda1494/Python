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
pygame.display.set_caption("Tower Defense Game")


# 타워 클래스
class Tower:

    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.range = 100 if tower_type == "normal" else 150
        self.damage = 10 if tower_type == "normal" else 15
        self.cooldown = 30  # 공격 쿨타임
        self.last_attack = 0
        self.tower_type = tower_type

    def draw(self):
        color = GREEN if self.tower_type == "normal" else BLUE  # 다른 색상으로 구분
        pygame.draw.rect(screen, color, (self.x, self.y, 40, 40))

    def can_attack(self, current_time):
        return current_time - self.last_attack >= self.cooldown

    def upgrade(self):
        global resources
        if resources >= 20:  # 업그레이드 비용
            self.damage += 5
            self.range += 20
            resources -= 20  # 자원 소비


# 적 클래스
class Enemy:

    def __init__(self):
        self.x = 0
        self.y = random.randint(50, HEIGHT - 50)
        self.speed = random.randint(2, 4)  # 속도 다양화
        self.health = random.randint(50, 100)  # 체력 다양화
        self.special_ability = random.choice([None, 'fast', 'tank'])  # 특별한 능력

    def move(self):
        if self.special_ability == 'fast':
            self.x += 5  # 빠른 적
        else:
            self.x += self.speed  # 일반 적

    def draw(self):
        color = RED if self.special_ability != 'tank' else BLUE  # 다른 색상으로 구분
        pygame.draw.rect(screen, color, (self.x, self.y, 30, 30))


# 게임 상태 변수
towers = []
enemies = []
score = 0
resources = 100  # 초기 자원
level = 1
running = True
clock = pygame.time.Clock()
game_over = False


def reset_game():
    global towers, enemies, score, resources, level, game_over
    towers = []
    enemies = []
    score = 0
    resources = 100
    level = 1
    game_over = False


def display_game_over():
    font = pygame.font.SysFont(None, 48)
    game_over_text = font.render("Game Over", True, RED)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)

    screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
    screen.blit(score_text, (WIDTH // 2 - 150, HEIGHT // 2))
    screen.blit(restart_text, (WIDTH // 2 - 150, HEIGHT // 2 + 50))


def display_tower_upgrade(tower):
    font = pygame.font.SysFont(None, 36)
    upgrade_text = font.render("Press U to Upgrade", True, WHITE)
    screen.blit(upgrade_text, (tower.x, tower.y - 30))


def display_level_info():
    font = pygame.font.SysFont(None, 36)
    level_text = font.render(f'Level: {level}', True, WHITE)
    screen.blit(level_text, (10, 70))


while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            if event.button == 1:  # 왼쪽 클릭
                mouse_x, mouse_y = pygame.mouse.get_pos()
                tower_type = "normal" if len(
                    towers) % 2 == 0 else "strong"  # 타워 종류를 번갈아가며 생성
                towers.append(Tower(mouse_x - 20, mouse_y - 20, tower_type))
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                reset_game()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u:  # 업그레이드 키
                for tower in towers:
                    if tower.x < mouse_x < tower.x + 40 and tower.y < mouse_y < tower.y + 40:
                        tower.upgrade()

    # 적 생성
    if random.random() < 0.02 + (level *
                                 0.01) and not game_over:  # 레벨에 따라 적 생성 확률 증가
        enemies.append(Enemy())

    # 타워 공격
    current_time = pygame.time.get_ticks()
    for tower in towers:
        if tower.can_attack(current_time):
            for enemy in enemies:
                if (tower.x < enemy.x < tower.x + 40) and (tower.y < enemy.y <
                                                           tower.y + 40):
                    enemy.health -= tower.damage
                    tower.last_attack = current_time
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        score += 1
                        resources += 10  # 적 처치 시 자원 획득
                        if score % 5 == 0:  # 5점마다 레벨 증가
                            level += 1
                    break

    # 적 이동 및 그리기
    for enemy in enemies:
        enemy.move()
        enemy.draw()
        if enemy.x > WIDTH:  # 적이 화면을 넘어가면 게임 오버
            game_over = True

    # 타워 그리기 및 업그레이드 표시
    for tower in towers:
        tower.draw()
        display_tower_upgrade(tower)

    # 점수 및 자원 표시
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f'Score: {score}', True, WHITE)
    resources_text = font.render(f'Resources: {resources}', True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(resources_text, (10, 40))
    display_level_info()

    if game_over:
        display_game_over()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
