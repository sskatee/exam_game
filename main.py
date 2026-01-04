import json
import os

from boss import *
from player import *


# Инициализация списков ритуальных предметов
def generate_artifact_files():
    start_items = [
        "🌊 Ракушка Приливов",
        "🔥 Огненный Кремень",
        "🌿 Лист Древнего Древа",
        "💎 Глаз Бури",
        "🐚 Рог Морского Царя",
        "🌙 Лунный Камень",
        "☀️ Солнечный Кристалл",
        "🌀 Перо Ветров"
    ]

    spirit_items = [
        "👁️ Всевидящее Око",
        "🕯️ Свеча Вечности",
        "💀 Череп Предка",
        "🌪️ Амулет Урагана",
        "🕊️ Крыло Феникса",
        "🌺 Цветок Забвения",
        "🗿 Рунический Камень"
    ]

    with open("start_items.txt", "w", encoding="utf-8") as start_file:
        for item in start_items:
            start_file.write(item + "\n")

    with open("spirit_items.txt", "w", encoding="utf-8") as spirit_file:
        for item in spirit_items:
            spirit_file.write(item + "\n")

    print("Файлы с ритуальными предметами созданы.")


# Создание файлов при первом запуске
if not os.path.exists("start_items.txt"):
    generate_artifact_files()

# Глобальные переменные
moves_log = []
start_items = []
spirit_items = []
current_item = ""
visited_locations = set()
collected_items = []
player = None
boss = None


# Загрузка предметов из файлов
def load_items():
    global start_items, spirit_items
    try:
        with open("start_items.txt", "r", encoding="utf-8") as file:
            start_items = [line.strip() for line in file if line.strip()]
        with open("spirit_items.txt", "r", encoding="utf-8") as file:
            spirit_items = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("Файлы не найдены. Создаем новые...")
        generate_artifact_files()
        load_items()


# Сохранение предметов в файлы
def save_items():
    with open("start_items.txt", "w", encoding="utf-8") as file:
        for item in start_items:
            file.write(item + "\n")
    with open("spirit_items.txt", "w", encoding="utf-8") as file:
        for item in spirit_items:
            file.write(item + "\n")


def save_game():
    if not current_item:
        print("⚠️ Нечего сохранять - игра еще не начата!")
        return False

    save_data = {
        "current_item": current_item,
        "collected_items": collected_items,
        "visited_locations": list(visited_locations),
        "moves_log": moves_log,
        "start_items": start_items,
        "spirit_items": spirit_items,
        "player_health": player.health if player else 100,
        "player_name": player.name if player else "Искатель"
    }

    try:
        with open("save_game.json", "w", encoding="utf-8") as file:
            json.dump(save_data, file, ensure_ascii=False, indent=2)
        print("✅ Игра успешно сохранена!")
        return True
    except Exception as e:
        print(f"❌ Ошибка при сохранении: {e}")
        return False


def load_game():
    global current_item, collected_items, visited_locations, moves_log, start_items, spirit_items, player

    if not os.path.exists("save_game.json"):
        print("⚠️ Файл сохранения не найден!")
        return False

    try:
        with open("save_game.json", "r", encoding="utf-8") as file:
            save_data = json.load(file)

        current_item = save_data["current_item"]
        collected_items = save_data["collected_items"]
        visited_locations = set(save_data["visited_locations"])
        moves_log = save_data["moves_log"]
        start_items = save_data["start_items"]
        spirit_items = save_data["spirit_items"]

        # Восстанавливаем игрока
        player_name = save_data.get("player_name", "Искатель")
        player_health = save_data.get("player_health", 100)
        player = Player(player_name)
        player.health = player_health
        player.artifacts = collected_items.copy()

        print("✅ Игра успешно загружена!")
        print(f"🎮 Игрок: {player.name}")
        print(f"❤️  Здоровье: {player.health}")
        print(f"📦 Предметов: {len(collected_items)}")

        if visited_locations:
            last_location = list(visited_locations)[-1]
            if last_location == "Пляж":
                beach_choice()
            elif last_location == "Джунгли":
                jungle_path()
            elif last_location == "Утесы":
                cliffs_path()
            elif last_location == "Пещера":
                cave_path()
            elif last_location == "Руины храма":
                temple_ruins()
            elif last_location == "Финальная битва":
                # Если сохранение в битве, возвращаем в храм
                temple_ruins()
            else:
                beach_choice()
        else:
            beach_choice()

        return True
    except Exception as e:
        print(f"❌ Ошибка при загрузке: {e}")
        return False


def discard_progress():
    global current_item, collected_items, visited_locations, moves_log, player

    print("\n⚠️ ВНИМАНИЕ: Весь прогресс будет потерян!")
    print(f"Вы потеряете: {len(collected_items)} собранных предметов")
    print(f"Вы посетили: {len(visited_locations)} мест")

    choice = get_valid_input("Вы уверены? (да/нет): ", ["да", "нет"])

    if choice == "да":
        # Возвращаем все артефакты обратно в копилку
        return_items_to_pool()

        # Очищаем прогресс
        current_item = ""
        collected_items.clear()
        visited_locations.clear()
        moves_log.clear()
        player = None

        save_items()

        print("🗑️ Прогресс сброшен! Все предметы возвращены в копилку.")

        if os.path.exists("save_game.json"):
            os.remove("save_game.json")
            print("🗂️ Файл сохранения удален.")

        return True
    else:
        print("❌ Отмена сброса прогресса.")
        return False


def return_items_to_pool():
    for item in collected_items:
        if item in ["🌊 Ракушка Приливов", "🔥 Огненный Кремень", "🌿 Лист Древнего Древа",
                    "💎 Глаз Бури", "🐚 Рог Морского Царя", "🌙 Лунный Камень",
                    "☀️ Солнечный Кристалл", "🌀 Перо Ветров"]:
            if item not in start_items:
                start_items.append(item)
        else:
            if item not in spirit_items:
                spirit_items.append(item)


def log_move(description):
    moves_log.append(description)
    print(f"📝 {description}")


def choose_starting_item():
    global current_item, player
    if not start_items:
        print("⚠️ Нет доступных предметов для начала!")
        return False

    current_item = random.choice(start_items)
    start_items.remove(current_item)
    collected_items.append(current_item)

    # Создаем игрока
    player = Player()
    player.artifacts = collected_items.copy()

    log_move(f"Начальный предмет: {current_item}")
    print(f"\n🌀 Вы держите в руках: {current_item}")
    print("💫 'Древняя энергия пульсирует в этом предмете...'")
    print(f"\n{player.show_stats()}")
    return True


def get_valid_input(prompt, valid_options):
    while True:
        choice = input(prompt).strip().lower()
        if choice in valid_options:
            return choice
        print("❌ Неверный выбор. Попробуйте снова.")


def show_save_menu(from_location=""):
    print("\n💾 Меню Сохранения")
    print("1. Сохранить игру")
    print("2. Продолжить без сохранения")
    print("3. Сбросить прогресс и выйти")
    print("4. Вернуться в игру")

    choice = get_valid_input("Выберите действие (1-4): ", ["1", "2", "3", "4"])

    if choice == "1":
        if save_game():
            print("✅ Прогресс сохранен!")
            return_to_location(from_location)
    elif choice == "2":
        print("⚠️ Игра не сохранена! Прогресс может быть потерян.")
        return_to_location(from_location)
    elif choice == "3":
        if discard_progress():
            print("\n🏝️ Возвращаемся на пляж...")
            beach_choice()
    elif choice == "4":
        return_to_location(from_location)


def return_to_location(location):
    if location == "beach":
        beach_choice()
    elif location == "jungle":
        jungle_path()
    elif location == "cliffs":
        cliffs_path()
    elif location == "cave":
        cave_path()
    elif location == "temple":
        temple_ruins()
    else:
        beach_choice()


#сФинальная битва с боссом
def final_battle():
    visited_locations.add("Финальная битва")

    global boss
    boss = Boss("👹 Хранитель Проклятия")

    print("\n" + "*" * 50)
    print("⚔️ ФИНАЛЬНАЯ БИТВА ⚔️")
    print("*" * 50)
    print("Перед вами появляется Хранитель Проклятия!")
    print("Его сила питается древним проклятием острова.")
    print("Только победа над ним может освободить остров!")

    input("\nНажмите Enter чтобы начать битву...")

    battle_round = 1

    while player.is_alive() and boss.is_alive():
        print(f"\n{'*' * 30}")
        print(f"РАУНД {battle_round}")
        print(f"{'*' * 30}")

        # Показываем статистику
        print(player.show_stats())
        print(boss.show_stats())

        # Ход игрока
        print(f"\n{player.name}, выберите действие:")
        print("1. Атаковать ⚔️")
        print("2. Специальная атака ⚡ (раз в 3 раунда)")
        print("3. Защищаться 🛡️ (уменьшает урон в этом раунде)")
        print("4. Использовать артефакт для лечения 💊")

        choice = get_valid_input("Ваш выбор (1-4): ", ["1", "2", "3", "4"])

        player_damage = 0
        player_defending = False

        if choice == "1":
            player_damage = player.attack_enemy()
            print(f"⚔️ {player.name} атакует и наносит {player_damage} урона!")

        elif choice == "2":
            player_damage = player.special_attack()
            print(f"⚡ {player.name} наносит {player_damage} урона!")

        elif choice == "3":
            player_defending = True
            player.defense += 5  # Временное увеличение защиты
            print(f"🛡️ {player.name} занимает оборонительную позицию!")

        elif choice == "4":
            if len(player.artifacts) >= 2:
                # Используем артефакт для лечения
                heal_amount = 20 + len(player.artifacts) * 5
                player.heal(heal_amount)
                print(f"💊 {player.name} использует энергию артефактов и восстанавливает {heal_amount} здоровья!")
                print(f"❤️ Теперь здоровье: {player.health}/{player.max_health}")
            else:
                print("⚠️ Нужно минимум 2 артефакта для лечения!")
                continue

        # Босс получает урон
        if player_damage > 0:
            actual_damage = boss.take_damage(player_damage)
            print(f"💢 {boss.name} получает {actual_damage} урона!")

        # Проверяем, побежден ли босс
        if not boss.is_alive():
            print(f"\n🎉 {boss.name} побежден!")
            victory_ending()
            return

        # Ход босса
        print(f"\nХод {boss.name}:")
        boss_damage = boss.attack_player(player)

        if player_defending:
            print(f"🛡️ Защита снизила урон до {boss_damage}!")
            player.defense -= 5  # Возвращаем защиту к исходному значению

        print(f"💔 {player.name} получает {boss_damage} урона!")

        # Проверяем, жив ли игрок
        if not player.is_alive():
            print(f"\n💀 {player.name} пал в бою...")
            defeat_ending()
            return

        # Восстанавливаем специальную атаку каждые 3 раунда
        if battle_round % 3 == 0:
            player.reset_special()
            print("✨ Специальная атака снова доступна!")

        battle_round += 1

        # Небольшая пауза между раундами
        input("\nНажмите Enter чтобы продолжить...")


def victory_ending():
    print("\n" + "🎊" * 25)
    print("🎊 ПОБЕДА! 🎊")
    print("🎊" * 25)

    # Разные концовки в зависимости от количества артефактов
    if len(collected_items) >= 5:
        ending = "Вы не только победили Хранителя Проклятия, но и собрали все древние артефакты. Остров процветает под вашим правлением как нового хранителя!"
    elif len(collected_items) >= 3:
        ending = "Победа над Хранителем сняла проклятие с острова. Вы находите корабль и возвращаетесь домой героем, унося с собой легендарные артефакты!"
    else:
        ending = "Вы победили Хранителя, но с малым количеством артефактов не смогли полностью снять проклятие. Остров начинает медленно восстанавливаться..."

    log_move(f"Победа в финальной битве! Артефактов: {len(collected_items)}")
    end_game(ending, True)


def defeat_ending():
    print("\n" + "💀" * 25)
    print("💀 ПОРАЖЕНИЕ 💀")
    print("💀" * 25)

    ending = "Хранитель Проклятия оказался сильнее. Ваша неудача позволяет проклятию распространиться дальше. Остров навсегда остается во тьме..."

    log_move("Поражение в финальной битве")
    end_game(ending, False)


def start_game():
    global moves_log, visited_locations, collected_items
    moves_log = []
    visited_locations.clear()
    collected_items.clear()

    print("\n" + "*" * 50)
    print("🏝️  ДОБРО ПОЖАЛОВАТЬ НА ОСТРОВ ПРОКЛЯТЫХ! 🏝️")
    print("*" * 50)
    print("Ваш корабль разбился о скалы. Вы очнулись на берегу таинственного острова...")

    if not choose_starting_item():
        return

    log_move("Начало игры на острове")
    beach_choice()


def beach_choice():
    visited_locations.add("Пляж")
    print("\n" + "*" * 30)
    print("🌊 ВЫ НА ПЛЯЖЕ")
    print("*" * 30)
    print("1. Джунгли - темная чаща деревьев")
    print("2. Утесы - высокие скалы")
    print("3. Пещера - темный проход в скале")
    print("4. Сохранить игру 💾")
    print("5. Вернуться в главное меню")

    choice = get_valid_input("Куда пойдете? (1-5): ", ["1", "2", "3", "4", "5"])

    if choice == "1":
        jungle_path()
    elif choice == "2":
        cliffs_path()
    elif choice == "3":
        cave_path()
    elif choice == "4":
        show_save_menu("beach")
    elif choice == "5":
        return_items_to_pool()
        save_items()
        print("📦 Предметы возвращены в копилку")


def jungle_path():
    visited_locations.add("Джунгли")
    print("\n" + "*" * 30)
    print("🌴 ВЫ В ДЖУНГЛЯХ")
    print("*" * 30)
    print("Воздух густой и влажный.")
    print("Вдруг перед вами появляется древний дух острова! 👻")
    print("Дух предлагает испытание мудрости...")

    print("\n1. Принять испытание")
    print("2. Отказаться и вернуться")
    print("3. Сохранить игру 💾")

    choice = get_valid_input("Ваш выбор (1-3): ", ["1", "2", "3"])

    if choice == "1":
        wisdom_test()
    elif choice == "2":
        safe_return("Вы отказались от испытания и вернулись на пляж")
    elif choice == "3":
        show_save_menu("jungle")


def wisdom_test():
    print("\n🧠 Дух задает загадку:")
    print("'Что можно нарушить, даже не прикасаясь к нему?'")

    answer = input("Ваш ответ: ").strip().lower()
    log_move(f"Ответ на загадку: {answer}")

    if answer == "обещание" or answer == "молчание" or answer == "слово":
        print("✅ Дух доволен вашей мудростью!")
        temple_ruins()
    else:
        print("❌ Дух качает головой...")
        print("Правильный ответ: 'Обещание'/'молчание'/'слово'")
        lose_item_to_spirit()


def temple_ruins():
    visited_locations.add("Руины храма")
    print("\n" + "*" * 30)
    print("🏛️ РУИНЫ ХРАМА")
    print("*" * 30)
    print("На алтаре лежат ритуальные предметы...")

    if spirit_items:
        print("\n🎭 ДОСТУПНЫЕ ПРЕДМЕТЫ ДУХОВ:")
        for i, item in enumerate(spirit_items, 1):
            print(f"{i}. {item}")

        print(f"\n{len(spirit_items) + 1}. Не брать ничего")
        print(f"{len(spirit_items) + 2}. Начать финальную битву ⚔️")
        print(f"{len(spirit_items) + 3}. Сохранить игру 💾")
        print(f"{len(spirit_items) + 4}. Вернуться на пляж")

        try:
            choice = input(f"Выберите действие (1-{len(spirit_items) + 4}): ")

            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(spirit_items):
                    selected = spirit_items.pop(choice_num - 1)
                    collected_items.append(selected)
                    player.artifacts.append(selected)
                    log_move(f"Получен предмет духа: {selected}")
                    print(f"✨ Вы взяли: {selected}")
                    print("'Энергия острова усиливается...'")
                    save_items()
                    temple_ruins()
                elif choice_num == len(spirit_items) + 1:
                    print("Вы ничего не берете...")
                    temple_ruins()
                elif choice_num == len(spirit_items) + 2:
                    # ФИНАЛЬНАЯ БИТВА
                    if len(collected_items) >= 2:
                        final_battle()
                    else:
                        print("⚠️ Нужно минимум 2 артефакта для битвы с Хранителем!")
                        temple_ruins()
                elif choice_num == len(spirit_items) + 3:
                    show_save_menu("temple")
                elif choice_num == len(spirit_items) + 4:
                    beach_choice()
                else:
                    print("⚠️ Неверный выбор!")
                    temple_ruins()
            else:
                print("⚠️ Нужно ввести число!")
                temple_ruins()

        except ValueError:
            print("⚠️ Ошибка ввода!")
            temple_ruins()
    else:
        print("⚠️ Нет доступных предметов духа")
        # Предлагаем финальную битву
        if len(collected_items) >= 2:
            print("\n⚔️ Вы собрали все доступные артефакты!")
            print("Готовы к финальной битве?")
            choice = get_valid_input("Начать битву? (да/нет): ", ["да", "нет"])
            if choice == "да":
                final_battle()
            else:
                beach_choice()
        else:
            print("⚠️ Нужно больше артефактов для финальной битвы!")
            beach_choice()


def cliffs_path():
    visited_locations.add("Утесы")
    print("\n" + "*" * 30)
    print("🧗 ВЫ НА УТЕСАХ")
    print("*" * 30)
    print("На вершине вы встречаете старого отшельника 🧔")

    print("\n1. Поговорить с отшельником")
    print("2. Вернуться на пляж")
    print("3. Сохранить игру 💾")

    choice = get_valid_input("Ваш выбор (1-3): ", ["1", "2", "3"])

    if choice == "1":
        print("\nОтшельник говорит: 'Остров проклят древним заклинанием...'")
        print("'Собери артефакты и сразись с Хранителем в руинах храма!'")
        print("'Каждый артефакт увеличит твою силу в битве.'")

        # Отшельник может дать подсказку или небольшой бонус
        if player and player.health < player.max_health:
            heal_amount = 30
            player.heal(heal_amount)
            print(f"🧙 Отшельник делится с вами целебным зельем! +{heal_amount} здоровья")
            print(f"❤️ Теперь здоровье: {player.health}/{player.max_health}")

        cliffs_path()
    elif choice == "2":
        safe_return("Вы спустились с утесов")
    elif choice == "3":
        show_save_menu("cliffs")


def cave_path():
    visited_locations.add("Пещера")
    print("\n" + "*" * 30)
    print("🕳️ ВЫ В ПЕЩЕРЕ")
    print("*" * 30)
    print("В глубине пещеры светится странный символ на стене.")

    print("\n1. Исследовать символ")
    print("2. Вернуться на пляж")
    print("3. Сохранить игру 💾")

    choice = get_valid_input("Ваш выбор (1-3): ", ["1", "2", "3"])

    if choice == "1":
        print("\n🔮 Символ оживает! Это портал...")
        portal_challenge()
    elif choice == "2":
        print("Вы спешно покидаете пещеру")
        beach_choice()
    elif choice == "3":
        show_save_menu("cave")


def portal_challenge():
    print("\n🌀 Портал предлагает игру:")
    print("Угадай число от 1 до 5, которое задумал портал")

    secret_number = random.randint(1, 5)
    attempts = 3

    for attempt in range(attempts):
        try:
            guess = int(input(f"Попытка {attempt + 1}/{attempts}: "))
            if guess == secret_number:
                print("🎉 Портал открывается!")
                # Портал ведет прямо в храм
                temple_ruins()
                return
            else:
                print("❌ Не угадал!")
        except ValueError:
            print("⚠️ Введите число!")

    print("💀 Портал поглощает ваш предмет!")
    lose_item_to_spirit()


def lose_item_to_spirit():
    if collected_items:
        lost_item = collected_items.pop()
        spirit_items.append(lost_item)
        if player and lost_item in player.artifacts:
            player.artifacts.remove(lost_item)
        save_items()
        log_move(f"Предмет потерян: {lost_item}")
        print(f"💨 {lost_item} перешел к духам острова")

    if not collected_items:
        end_game("Вы потеряли все предметы. Проклятие острова поглотило вас.", False)
    else:
        beach_choice()


def safe_return(message):
    log_move(message)
    print(f"\n🛡️ {message}")
    beach_choice()


def end_game(outcome, success):
    log_move(f"Итог: {outcome}")

    print("\n" + "*" * 50)
    print("🎮 ИГРА ЗАВЕРШЕНА")
    print("*" * 50)
    print(f"Концовка: {outcome}")

    if success:
        print("✅ ВЫ ДОСТИГЛИ УСПЕХА!")
    else:
        print("❌ ВЫ ПОТЕРПЕЛИ НЕУДАЧУ")

    print(f"\n📍 Посещенные места: {', '.join(visited_locations)}")
    print(f"📦 Собранные артефакты: {', '.join(collected_items) if collected_items else 'нет'}")

    if player:
        print(f"⚔️ Финальное здоровье: {player.health}/{player.max_health}")

    # Запись в файл
    with open("island_log.txt", "a", encoding="utf-8") as file:
        file.write("\n" + "*" * 40 + "\n")
        file.write("Новая игра\n")
        for move in moves_log:
            file.write(f"- {move}\n")
        file.write(f"Результат: {outcome}\n")
        file.write(f"Успех: {success}\n")
        if player:
            file.write(f"Финальное здоровье: {player.health}\n")
            file.write(f"Артефактов собрано: {len(collected_items)}\n")

    print("\n📁 Результат записан в файл 'island_log.txt'")

    # Предлагаем сохранить предметы или вернуть в копилку
    print("\n💾 Что делать с собранными предметами?")
    print("1. Сохранить для следующей игры (в текущих списках)")
    print("2. Вернуть все в копилку (сбросить прогресс)")

    choice = get_valid_input("Выберите (1/2): ", ["1", "2"])

    if choice == "1":
        save_items()
        print("✅ Предметы сохранены для следующих игр!")
    else:
        return_items_to_pool()

        if os.path.exists("save_game.json"):
            os.remove("save_game.json")

        save_items()
        print("💰 Все предметы возвращены в копилку!")

    input("\nНажмите Enter чтобы вернуться в главное меню...")


# Главное меню
def main_menu():
    load_items()

    print("\n" + "*" * 50)
    print("🌴 ОСТРОВ ПРОКЛЯТЫХ - Главное Меню")
    print("*" * 50)

    while True:
        print("\n1. Начать новую игру")
        print("2. Загрузить сохраненную игру")
        print("3. Показать доступные предметы")
        print("4. Сбросить все предметы (начать заново)")
        print("5. Удалить сохранение игры")
        print("6. Выйти из игры")

        choice = get_valid_input("Выберите действие (1-6): ", ["1", "2", "3", "4", "5", "6"])

        if choice == "1":
            if start_items:
                start_game()
            else:
                print("⚠️ Нет стартовых предметов! Сбросьте предметы в меню.")
        elif choice == "2":
            if os.path.exists("save_game.json"):
                load_game()
            else:
                print("⚠️ Нет сохраненной игры!")
        elif choice == "3":
            print("\n📦 СТАРТОВЫЕ ПРЕДМЕТЫ:")
            for item in start_items:
                print(f"  • {item}")
            print(f"  Всего: {len(start_items)} предметов")

            print("\n🎭 ПРЕДМЕТЫ ДУХОВ:")
            for item in spirit_items:
                print(f"  • {item}")
            print(f"  Всего: {len(spirit_items)} предметов")

            if os.path.exists("save_game.json"):
                print("\n💾 Сохранение игры: ДА")
            else:
                print("\n💾 Сохранение игры: НЕТ")
        elif choice == "4":
            generate_artifact_files()
            load_items()
            print("✅ Все предметы сброшены к начальным значениям!")
        elif choice == "5":
            if os.path.exists("save_game.json"):
                os.remove("save_game.json")
                print("🗂️ Файл сохранения удален!")
            else:
                print("⚠️ Файл сохранения не найден!")
        elif choice == "6":
            print("\n🌊 Спасибо за игру! До свидания!")
            break


# Запуск игры
if __name__ == "__main__":
    main_menu()