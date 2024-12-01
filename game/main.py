import pygame
import random
import sys
import pickle  # 진행 상황 저장을 위한 라이브러리

# 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-Down Shooter")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# 볼륨 설정
volume = 1.0  # 기본 볼륨 값


# 플레이어 클래스
class Player:

    def __init__(self):
        self.image = pygame.Surface((50, 50))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.speed = 5
        self.health = 100
        self.score = 0
        self.level = 1
        self.weapon_type = 'normal'  # 기본 무기
        self.skill_points = 0
        self.attack_power = 10  # 공격력 추가
        self.skills = {
            'speed': 0,
            'health': 0,
            'attack': 0,
            'defense': 0,
            'critical_hit': 0  # 크리티컬 히트 스킬 추가
        }  # 스킬 트리
        self.items = []  # 아이템 리스트
        self.resources = 0  # 자원

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.rect.clamp_ip(screen.get_rect())  # 화면 경계 내에서 이동

    def draw(self):
        screen.blit(self.image, self.rect)

    def level_up(self):
        self.level += 1
        self.skill_points += 1  # 스킬 포인트 추가
        print(
            f"Level Up! Now at level {self.level}. Skill Points available: {self.skill_points}"
        )

    def upgrade_attack(self):
        if self.skill_points > 0:
            self.attack_power += 5  # 공격력 증가
            self.skill_points -= 1
            print(
                f"Attack Power upgraded to {self.attack_power}. Skill Points left: {self.skill_points}"
            )

    def upgrade_speed(self):
        if self.skill_points > 0:
            self.speed += 1  # 속도 증가
            self.skill_points -= 1
            print(
                f"Speed upgraded to {self.speed}. Skill Points left: {self.skill_points}"
            )

    def upgrade_health(self):
        if self.skill_points > 0:
            self.health += 10  # 체력 증가
            self.skill_points -= 1
            print(
                f"Health upgraded to {self.health}. Skill Points left: {self.skill_points}"
            )

    def upgrade_defense(self):
        if self.skill_points > 0:
            self.skills['defense'] += 1  # 방어력 증가
            self.skill_points -= 1
            print(
                f"Defense upgraded to {self.skills['defense']}. Skill Points left: {self.skill_points}"
            )

    def upgrade_critical_hit(self):
        if self.skill_points > 0:
            self.skills['critical_hit'] += 1  # 크리티컬 히트 증가
            self.skill_points -= 1
            print(
                f"Critical Hit level upgraded to {self.skills['critical_hit']}. Skill Points left: {self.skill_points}"
            )

    def reset_items(self):
        self.items.clear()  # 아이템 초기화
        self.resources = 0  # 자원 초기화


# 장비 클래스
class Equipment:

    def __init__(self, name, description, effect):
        self.name = name
        self.description = description
        self.effect = effect
        self.level = 0  # 장비 레벨


# 적 클래스
class Enemy:

    def __init__(self, enemy_type='normal'):
        self.image = pygame.Surface((40, 40))
        self.type = enemy_type
        self.health = 30  # 적의 기본 건강
        self.speed = random.randint(1, 3)
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH),
                                                random.randint(0, HEIGHT)))
        self.state = 'idle'  # 초기 상태

        if self.type == 'normal':
            self.image.fill(RED)
        elif self.type == 'fast':
            self.image.fill(BLUE)
            self.speed += 2
        elif self.type == 'strong':
            self.image.fill(PURPLE)
            self.health += 20
        elif self.type == 'stealth':  # 스텔스 적 추가
            self.image.fill((150, 150, 150))
            self.health = 20
            self.speed += 1
        elif self.type == 'ranged':  # 원거리 적 추가
            self.image.fill(YELLOW)
            self.health = 25
            self.speed -= 1

    def update(self, player):
        distance = self.rect.center.distance_to(player.rect.center)
        # 상태 전환
        if distance < 100:  # 플레이어가 가까이 오면 공격
            self.state = 'attack'
        elif distance < 300:  # 중간 거리에서 추적
            self.state = 'chase'
        else:  # 멀어지면 대기
            self.state = 'idle'

        self.perform_action(player)

    def perform_action(self, player):
        if self.state == 'attack':
            self.attack(player)
        elif self.state == 'chase':
            self.move_towards_player(player)
        elif self.state == 'idle':
            pass  # 대기 상태

    def move_towards_player(self, player):
        if self.rect.x < player.rect.x:
            self.rect.x += self.speed
        elif self.rect.x > player.rect.x:
            self.rect.x -= self.speed
        if self.rect.y < player.rect.y:
            self.rect.y += self.speed
        elif self.rect.y > player.rect.y:
            self.rect.y -= self.speed

    def attack(self, player):
        if player.rect.colliderect(self.rect):
            player.health -= 1  # 플레이어에게 피해를 줌

    def draw(self):
        screen.blit(self.image, self.rect)


# 보스 클래스
class Boss(Enemy):

    def __init__(self):
        super().__init__(enemy_type='strong')
        self.image.fill(YELLOW)
        self.health = 200  # 보스 건강
        self.attack_power = 5  # 보스 공격력

    def move_towards_player(self, player):
        if self.rect.x < player.rect.x:
            self.rect.x += 3  # 보스의 속도
        elif self.rect.x > player.rect.x:
            self.rect.x -= 3
        if self.rect.y < player.rect.y:
            self.rect.y += 3
        elif self.rect.y > player.rect.y:
            self.rect.y -= 3

    def attack(self, player):
        if player.rect.colliderect(self.rect):
            player.health -= self.attack_power  # 보스가 플레이어에게 더 많은 피해를 줌

    def draw(self):
        super().draw()


# 스테이지 클래스
class Stage:

    def __init__(self, stage_number):
        self.stage_number = stage_number
        self.enemies = self.create_enemies()
        self.boss = None if stage_number < 3 else Boss()  # 3단계 이상에서 보스 생성

    def create_enemies(self):
        if self.stage_number == 1:
            return [Enemy('normal') for _ in range(5)]
        elif self.stage_number == 2:
            return [Enemy(random.choice(['normal', 'fast'])) for _ in range(7)]
        else:
            return [
                Enemy(random.choice(['normal', 'strong'])) for _ in range(10)
            ]


# 진행 상황 저장 및 로드
def save_game(player, enemies):
    with open('save_game.pkl', 'wb') as f:
        pickle.dump((player, enemies), f)


def load_game():
    try:
        with open('save_game.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None, None


# UI 및 레벨 디자인
def draw_ui(player):
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f'Score: {player.score}', True, WHITE)
    health_text = font.render(f'Health: {player.health}', True, WHITE)
    level_text = font.render(f'Level: {player.level}', True, WHITE)
    attack_text = font.render(f'Attack Power: {player.attack_power}', True,
                              WHITE)
    skill_points_text = font.render(f'Skill Points: {player.skill_points}',
                                    True, WHITE)
    critical_hit_text = font.render(
        f'Critical Hit Level: {player.skills["critical_hit"]}', True, WHITE)

    screen.blit(score_text, (10, 10))
    screen.blit(health_text, (10, 50))
    screen.blit(level_text, (10, 90))
    screen.blit(attack_text, (10, 130))
    screen.blit(skill_points_text, (10, 170))
    screen.blit(critical_hit_text, (10, 210))


# 게임 루프
def main():
    clock = pygame.time.Clock()
    player = Player()
    current_stage_number = 1
    stage = Stage(current_stage_number)
    bullets = []
    items = []
    settings_menu = SettingsMenu()  # 설정 메뉴 인스턴스 생성

    while True:
        screen.fill(BLACK)
        player.draw()

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:  # 'S' 키로 설정 메뉴 열기
                    settings_menu.is_open = True
                if event.key == pygame.K_ESCAPE:  # 'ESC' 키로 설정 메뉴 닫기
                    settings_menu.is_open = False
                if event.key == pygame.K_l:  # 'L' 키로 게임 로드
                    loaded_player, loaded_enemies = load_game()
                    if loaded_player and loaded_enemies:
                        player = loaded_player
                        stage.enemies = loaded_enemies
                        print("Game Loaded!")

                # 스킬 포인트 사용
                if event.key == pygame.K_UP:  # 공격력 업그레이드
                    player.upgrade_attack()
                elif event.key == pygame.K_DOWN:  # 속도 업그레이드
                    player.upgrade_speed()
                elif event.key == pygame.K_h:  # 체력 업그레이드
                    player.upgrade_health()
                elif event.key == pygame.K_d:  # 방어력 업그레이드
                    player.upgrade_defense()
                elif event.key == pygame.K_c:  # 크리티컬 히트 업그레이드
                    player.upgrade_critical_hit()

            # 설정 메뉴 이벤트 처리
            settings_menu.handle_event(event)

        # 플레이어 이동
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        player.move(dx, dy)

        # 총알 발사
        if keys[pygame.K_SPACE]:
            bullets.append(
                Bullet(player.rect.centerx, player.rect.top,
                       player.weapon_type))

        # 총알 업데이트 및 그리기
        for bullet in bullets[:]:
            bullet.update()
            if bullet.rect.bottom < 0:
                bullets.remove(bullet)
            else:
                bullet.draw()

        # 적 이동 및 그리기
        for enemy in stage.enemies:
            enemy.update(player)  # 적의 AI 업데이트
            enemy.draw()

            # 적의 체력이 0이 되면 제거
            if enemy.health <= 0:
                stage.enemies.remove(enemy)
                player.score += 10

        # 보스 처리
        if stage.boss:
            stage.boss.update(player)
            stage.boss.draw()
            if stage.boss.health <= 0:
                stage.boss = None  # 보스 처치

        # 모든 적을 처치했는지 체크
        if not stage.enemies and (not stage.boss or stage.boss.health <= 0):
            print("Stage Clear!")
            current_stage_number += 1
            stage = Stage(current_stage_number)  # 다음 스테이지로 전환
            player.level_up()  # 레벨 업

        # 플레이어 사망 체크
        if player.health <= 0:
            print("You died! Restarting stage...")
            player.reset_items()  # 아이템과 자원 초기화
            player.health = 100  # 체력 초기화
            stage = Stage(current_stage_number)  # 현재 스테이지 재시작

        # UI 업데이트
        draw_ui(player)

        # 설정 메뉴 그리기
        settings_menu.draw()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
