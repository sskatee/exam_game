import random

class Boss:
    def __init__(self, name="Древнее Чудовище"):
        self.name = name
        self.health = 150
        self.max_health = 150
        self.attack = 20
        self.defense = 15
        self.phase = 1  # Фаза битвы

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense // 3)
        self.health -= actual_damage

        # Проверка смены фазы
        if self.health <= self.max_health // 2 and self.phase == 1:
            self.phase = 2
            self.attack += 5
            print(f" {self.name} входит в ярость! Его атака усиливается!")

        return actual_damage

    def attack_player(self, player):
        base_damage = self.attack

        # Разные атаки в разных фазах
        if self.phase == 1:
            attack_type = random.choice(["normal", "normal", "strong"])
        else:
            attack_type = random.choice(["normal", "strong", "special"])

        if attack_type == "strong":
            base_damage = int(base_damage * 1.5)
            print(f"{self.name} использует сильную атаку!")
        elif attack_type == "special" and self.phase == 2:
            base_damage = self.attack * 2
            print(f" {self.name} использует разрушительную атаку!")

        return player.take_damage(base_damage)

    def is_alive(self):
        return self.health > 0

    def show_stats(self):
        health_bar = "💀" * (self.health // 15) + "☠️" * (10 - self.health // 15)
        phase_text = "I" if self.phase == 1 else "II"
        return f"{self.name} (Фаза {phase_text}) | Здоровье: {self.health}/{self.max_health} {health_bar}"
