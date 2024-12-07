import pandas as pd
import random
import json

# 인벤토리 클래스
class Inventory:
    def __init__(self):
        self.items = []  # 인벤토리 아이템 목록 초기화

    def add_item(self, item):
        self.items.append(item)  # 아이템을 인벤토리에 추가
        print(f"{item}이(가) 인벤토리에 추가되었습니다.")

    def use_item(self, player, item_name):
        # 플레이어가 아이템을 사용할 때 호출되는 메서드
        if item_name in self.items:
            item_details = load_item_data().get(item_name)  # 아이템 정보를 로드
            if item_details:
                if item_details['Type'] == 'Consumable':  # 소모품인지 확인
                    effect = item_details['Effect']
                    # 효과 처리
                    if "체력 회복" in effect:
                        heal_amount = int(effect.split()[1])  # 예: "체력 회복 50"
                        player.health += heal_amount  # 플레이어 체력 회복
                        print(f"{item_name}을(를) 사용하여 체력을 {heal_amount} 회복했습니다.")
                    elif "체력 증가" in effect:
                        increase_amount = int(effect.split()[1])  # 예: "체력 증가 20"
                        player.max_health += increase_amount  # 플레이어 최대 체력 증가
                        print(f"{item_name}을(를) 사용하여 최대 체력이 {increase_amount} 증가했습니다.")
                    elif "공격력 증가" in effect:
                        attack_increase = int(effect.split()[1])  # 예: "공격력 증가 5"
                        player.attack += attack_increase  # 플레이어 공격력 증가
                        print(f"{item_name}을(를) 사용하여 공격력이 {attack_increase} 증가했습니다.")
                    elif "방어력 증가" in effect:
                        defense_increase = int(effect.split()[1])  # 예: "방어력 증가 5"
                        player.defense += defense_increase  # 플레이어 방어력 증가
                        print(f"{item_name}을(를) 사용하여 방어력이 {defense_increase} 증가했습니다.")
                    elif "골드 증가" in effect:
                        gold_increase = int(effect.split()[1])  # 예: "골드 증가 100"
                        player.gold += gold_increase  # 플레이어 골드 증가
                        print(f"{item_name}을(를) 사용하여 골드가 {gold_increase} 증가했습니다.")
                    elif "경험치 증가" in effect:
                        exp_increase = int(effect.split()[1])  # 예: "경험치 증가 100"
                        player.gain_experience(exp_increase)  # 플레이어 경험치 증가
                        print(f"{item_name}을(를) 사용하여 경험치가 {exp_increase} 증가했습니다.")
                    elif "아이템 드랍률 증가" in effect:
                        drop_rate_increase = int(effect.split()[1])  # 예: "아이템 드랍률 증가 10"
                        player.drop_rate += drop_rate_increase  # 플레이어 드랍률 증가
                        print(f"{item_name}을(를) 사용하여 아이템 드랍률이 {drop_rate_increase} 증가했습니다.")
                else:
                    print("소모품이 아닌 아이템은 사용할 수 없습니다.")
            else:
                print("아이템 정보를 찾을 수 없습니다.")
        else:
            print("인벤토리에 해당 아이템이 없습니다.")

    def show_inventory(self):
        # 인벤토리의 아이템을 보여주는 메서드
        print("인벤토리:")
        for item in self.items:
            print(f"- {item}")

# 상점 클래스
class Shop:
    def __init__(self, items_for_sale):
        self.items_for_sale = items_for_sale  # 상점에서 판매하는 아이템 목록 초기화

    def show_items(self):
        # 상점에서 판매하는 아이템을 보여주는 메서드
        print("상점에서 판매하는 아이템:")
        for item, details in self.items_for_sale.items():
            print(f"- {item}: {details['Price']}골드 (효과: {details['Effect']})")

    def buy_item(self, player, item_name):
        # 플레이어가 아이템을 구매하는 메서드
        if item_name in self.items_for_sale:
            price = self.items_for_sale[item_name]['Price']  # 아이템 가격 확인
            if player.gold >= price:  # 골드가 충분한지 확인
                player.gold -= price  # 골드 차감
                player.inventory.add_item(item_name)  # 인벤토리에 아이템 추가
                print(f"{item_name}을(를) 구매했습니다.")
            else:
                print("골드가 부족합니다.")
        else:
            print("잘못된 아이템입니다.")

# 장비 클래스
class Equipment:
    def __init__(self):
        self.weapon = None  # 장착된 무기 초기화
        self.armor = None   # 장착된 방어구 초기화
        self.weapon_level = 0  # 무기 강화 레벨 초기화
        self.armor_level = 0   # 방어구 강화 레벨 초기화

    def equip_weapon(self, weapon):
        self.weapon = weapon  # 무기 장착
        print(f"{weapon}을(를) 장착했습니다.")

    def equip_armor(self, armor):
        self.armor = armor  # 방어구 장착
        print(f"{armor}을(를) 장착했습니다.")

    def show_equipment(self):
        # 현재 장착된 장비를 보여주는 메서드
        print("장착된 장비:")
        if self.weapon:
            print(f"- 무기: {self.weapon} (강화 레벨: {self.weapon_level})")
        else:
            print("- 무기: 없음")
        if self.armor:
            print(f"- 방어구: {self.armor} (강화 레벨: {self.armor_level})")
        else:
            print("- 방어구: 없음")

    def upgrade_weapon(self, player):
        # 무기 강화 메서드
        if self.weapon:
            level = self.weapon_level  # 현재 무기 레벨 확인
            cost = 20 * (level + 1)  # 강화 비용 (레벨에 따라 증가)
            if player.gold >= cost:  # 골드가 충분한지 확인
                player.gold -= cost  # 골드 차감
                success_rate = 100 - (level * 10)  # 기본 성공률 계산

                # 5레벨 이상일 경우 파괴 확률 추가
                destruction_chance = 0
                if level >= 5:
                    destruction_chance = (level - 4) * 5  # 5레벨부터 파괴 확률 증가

                # 강화 성공 여부 판단
                if random.randint(1, 100) <= success_rate:
                    self.weapon_level += 1  # 무기 강화
                    print(f"{self.weapon}이(가) 강화되었습니다. 현재 강화 레벨: {self.weapon_level}")
                else:
                    # 파괴 여부 판단
                    if random.randint(1, 100) <= destruction_chance:
                        print(f"{self.weapon}이(가) 파괴되었습니다!")  # 아이템 파괴
                        self.weapon = None  # 장비 파괴 시 None으로 설정
                        self.weapon_level = 0  # 레벨 초기화
                    else:
                        print(f"{self.weapon} 강화 실패.")
            else:
                print("골드가 부족하여 강화할 수 없습니다.")
        else:
            print("장착된 무기가 없습니다.")

    def upgrade_armor(self, player):
        # 방어구 강화 메서드
        if self.armor:
            level = self.armor_level  # 현재 방어구 레벨 확인
            cost = 20 * (level + 1)  # 강화 비용 (레벨에 따라 증가)
            if player.gold >= cost:  # 골드가 충분한지 확인
                player.gold -= cost  # 골드 차감
                success_rate = 100 - (level * 10)  # 기본 성공률 계산

                # 5레벨 이상일 경우 파괴 확률 추가
                destruction_chance = 0
                if level >= 5:
                    destruction_chance = (level - 4) * 5  # 5레벨부터 파괴 확률 증가

                # 강화 성공 여부 판단
                if random.randint(1, 100) <= success_rate:
                    self.armor_level += 1  # 방어구 강화
                    print(f"{self.armor}이(가) 강화되었습니다. 현재 강화 레벨: {self.armor_level}")
                else:
                    # 파괴 여부 판단
                    if random.randint(1, 100) <= destruction_chance:
                        print(f"{self.armor}이(가) 파괴되었습니다!")  # 아이템 파괴
                        self.armor = None  # 장비 파괴 시 None으로 설정
                        self.armor_level = 0  # 레벨 초기화
                    else:
                        print(f"{self.armor} 강화 실패.")
            else:
                print("골드가 부족하여 강화할 수 없습니다.")
        else:
            print("장착된 방어구가 없습니다.")

# 플레이어 클래스
class Player:
    def __init__(self):
        self.level = 1  # 초기 레벨
        self.experience = 0  # 초기 경험치
        self.attack = 5  # 초기 공격력
        self.defense = 5  # 초기 방어력
        self.health = 100  # 초기 체력
        self.max_health = 100  # 최대 체력
        self.gold = 100  # 초기 골드 (예시로 100으로 설정)
        self.drop_rate = 0  # 아이템 드랍률 초기화
        self.inventory = Inventory()  # 인벤토리 생성
        self.equipment = Equipment()  # 장비 생성
        self.quests = []  # 퀘스트 진행 상황

    def gain_experience(self, amount):
        self.experience += amount  # 경험치 증가
        print(f"경험치: {self.experience}/{self.experience_needed()}")
        self.check_level_up()  # 레벨업 체크

    def experience_needed(self):
        return 100 * self.level  # 레벨업에 필요한 경험치 계산

    def check_level_up(self):
        # 레벨업 체크 및 처리
        while self.experience >= self.experience_needed():
            self.level += 1
            self.experience -= self.experience_needed()  # 잔여 경험치를 다음 레벨을 위해 남김
            self.attack += 2  # 레벨업 시 공격력 증가
            self.defense += 2  # 레벨업 시 방어력 증가
            self.max_health += 10  # 레벨업 시 최대 체력 증가
            print(f"레벨업! 현재 레벨: {self.level} | 공격력: {self.attack} | 방어력: {self.defense} | 최대 체력: {self.max_health}")

    def take_damage(self, damage):
        self.health -= damage  # 피해를 받아 체력 감소
        print(f"받은 피해: {damage} | 현재 체력: {self.health}")
        if self.health <= 0:
            print("플레이어가 사망했습니다. 게임이 종료됩니다.")
            return True  # 플레이어가 죽었음을 알림
        return False  # 플레이어가 살아있음

    def use_item(self, item_name):
        # 아이템 사용 메서드
        self.inventory.use_item(self, item_name)

    def save(self, filename):
        # 게임 상태 저장 메서드
        data = {
            "level": self.level,
            "experience": self.experience,
            "attack": self.attack,
            "defense": self.defense,
            "health": self.health,
            "max_health": self.max_health,  # 최대 체력 저장
            "gold": self.gold,
            "drop_rate": self.drop_rate,  # 드랍률 저장
            "inventory": self.inventory.items,
            "equipment": {
                "weapon": self.equipment.weapon,
                "armor": self.equipment.armor,
                "weapon_level": self.equipment.weapon_level,
                "armor_level": self.equipment.armor_level,
            },
            "quests": self.quests  # 퀘스트 진행 상황 저장
        }
        with open(filename, 'w') as f:
            json.dump(data, f)
        print("게임이 저장되었습니다.")

    def load(self, filename):
        # 게임 상태 로드 메서드
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.level = data["level"]
                self.experience = data["experience"]
                self.attack = data["attack"]
                self.defense = data["defense"]
                self.health = data["health"]
                self.max_health = data["max_health"]  # 최대 체력 로드
                self.gold = data["gold"]
                self.drop_rate = data["drop_rate"]  # 드랍률 로드
                self.inventory.items = data["inventory"]
                self.equipment.weapon = data["equipment"]["weapon"]
                self.equipment.armor = data["equipment"]["armor"]
                self.equipment.weapon_level = data["equipment"]["weapon_level"]
                self.equipment.armor_level = data["equipment"]["armor_level"]
                self.quests = data["quests"]  # 퀘스트 진행 상황 로드
            print("게임이 로드되었습니다.")
        except FileNotFoundError:
            print("저장된 게임 파일을 찾을 수 없습니다.")
        except json.JSONDecodeError:
            print("게임 파일이 잘못된 형식입니다.")

# 아이템 데이터 로드 함수 (예시)
def load_item_data():
    return {
        "Health Potion": {"Type": "Consumable", "Effect": "체력 회복 50", "Price": 10},
        "Strength Potion": {"Type": "Consumable", "Effect": "공격력 증가 5", "Price": 20},
        "Defense Potion": {"Type": "Consumable", "Effect": "방어력 증가 5", "Price": 20},
        "Max Health Potion": {"Type": "Consumable", "Effect": "체력 증가 20", "Price": 30},
        "Gold Coin": {"Type": "Consumable", "Effect": "골드 증가 100", "Price": 15},
        "Experience Scroll": {"Type": "Consumable", "Effect": "경험치 증가 100", "Price": 25},
        "Drop Rate Boost": {"Type": "Consumable", "Effect": "아이템 드랍률 증가 10", "Price": 50},
    }

# 게임 실행 예시
if __name__ == "__main__":
    player = Player()
    shop = Shop(load_item_data())

    # 상점 아이템 보여주기
    shop.show_items()

    # 아이템 구매 예시
    shop.buy_item(player, "Health Potion")
    player.use_item("Health Potion")

    # 장비 장착 및 강화 예시
    player.equipment.equip_weapon("Iron Sword")
    player.equipment.upgrade_weapon(player)
    player.equipment.show_equipment()
