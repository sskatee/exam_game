class Player:
    def __init__(self, name="Искатель"):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.attack = 15
        self.defense = 10
        self.artifacts = []
        self.special_attack_ready = True

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense // 2)
        self.health -= actual_damage
        return actual_damage

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def attack_enemy(self):
        base_damage = self.attack
        # Артефакты увеличивают урон
        artifact_bonus = len(self.artifacts) * 2
        return base_damage + artifact_bonus

    def special_attack(self):
        if self.special_attack_ready:
            self.special_attack_ready = False
            damage = self.attack * 2 + len(self.artifacts) * 3
            print(f"⚡ {self.name} использует специальную атаку!")
            return damage
        else:
            print(" Специальная атака еще не готова!")
            return self.attack_enemy()

    def reset_special(self):
        self.special_attack_ready = True

    def is_alive(self):
        return self.health > 0

    def show_stats(self):
        health_bar = "❤️" * (self.health // 10) + "♡" * (10 - self.health // 10)
        return f"{self.name} | Здоровье: {self.health}/{self.max_health} {health_bar} | Атака: {self.attack} | Защита: {self.defense} | Артефактов: {len(self.artifacts)}"