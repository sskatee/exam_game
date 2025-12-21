import random
import json
import os


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


# Создаем файлы при первом запуске
if not os.path.exists("start_items.txt"):
    generate_artifact_files()

# Глобальные переменные
moves_log = []
start_items = []
spirit_items = []
current_item = ""
visited_locations = set()
collected_items = []
game_state = {}  # Для сохранения прогресса


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
        "spirit_items": spirit_items
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
    global current_item, collected_items, visited_locations, moves_log, start_items, spirit_items

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

        print("✅ Игра успешно загружена!")
        print(f"📦 Текущий предмет: {current_item}")
        print(f"📍 Посещенные места: {len(visited_locations)}")

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
            else:
                beach_choice()
        else:
            beach_choice()

        return True
    except Exception as e:
        print(f"❌ Ошибка при загрузке: {e}")
        return False


def discard_progress():
    global current_item, collected_items, visited_locations, moves_log

    print("\n⚠️ ВНИМАНИЕ: Весь прогресс будет потерян!")
    print(f"Вы потеряете: {len(collected_items)} собранных предметов")
    print(f"Вы посетили: {len(visited_locations)} мест")

    choice = get_valid_input("Вы уверены? (да/нет): ", ["да", "нет"])

    if choice == "да":
        # Возвращаем все артефакты обратно в копилку
        if current_item and current_item not in start_items:
            start_items.append(current_item)

        for item in collected_items:
            if item not in start_items and item not in spirit_items:
                if item in ["🌊 Ракушка Приливов", "🔥 Огненный Кремень", "🌿 Лист Древнего Древа",
                            "💎 Глаз Бури", "🐚 Рог Морского Царя", "🌙 Лунный Камень",
                            "☀️ Солнечный Кристалл", "🌀 Перо Ветров"]:
                    if item not in start_items:
                        start_items.append(item)
                else:
                    if item not in spirit_items:
                        spirit_items.append(item)

        # Очищаем прогресс
        current_item = ""
        collected_items.clear()
        visited_locations.clear()
        moves_log.clear()

        save_items()

        print("🗑️ Прогресс сброшен! Все предметы возвращены в копилку.")

        if os.path.exists("save_game.json"):
            os.remove("save_game.json")
            print("🗂️ Файл сохранения удален.")

        return True
    else:
        print("❌ Отмена сброса прогресса.")
        return False


def log_move(description):
    moves_log.append(description)
    print(f"📝 {description}")


def choose_starting_item():
    global current_item
    if not start_items:
        print("⚠️ Нет доступных предметов для начала!")
        return False

    current_item = random.choice(start_items)
    start_items.remove(current_item)
    collected_items.append(current_item)
    log_move(f"Вы нашли предмет: {current_item}")
    print(f"🌀 Вы держите в руках: {current_item}")
    print("'Древняя энергия пульсирует в этом предмете...'")
    return True


def get_valid_input(prompt, valid_options):
    while True:
        choice = input(prompt).strip().lower()
        if choice in valid_options:
            return choice
        print("❌ Неверный выбор. Попробуйте снова.")


# НОВОЕ: Простая загадка для первого ответвления
def simple_riddle():
    print("\n🧠 Дух задает загадку:")
    print("'Летит без крыльев, плачет без глаз.'")

    answer = input("Что это? ").strip().lower()

    if answer == "облако" or answer == "туча":
        print("✅ Верно! Это облако.")
        return True
    else:
        print("❌ Неверно! Это облако.")
        return False


# НОВОЕ: Простая игра на угадывание для второго ответвления
def guess_number():
    print("\n🎯 Угадай число от 1 до 3!")
    secret = random.randint(1, 3)

    try:
        guess = int(input("Твой выбор (1, 2 или 3): "))
        if guess == secret:
            print("🎉 Угадал!")
            return True
        else:
            print(f"❌ Не угадал! Было число {secret}.")
            return False
    except:
        print("❌ Нужно ввести число!")
        return False


def show_save_menu(from_location=""):
    print("\n💾 МЕНЮ СОХРАНЕНИЯ")
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
    elif location == "mysterious_path":
        mysterious_path()
    elif location == "secret_cave":
        secret_cave()
    else:
        beach_choice()


def start_game():
    global moves_log, visited_locations, collected_items
    moves_log = []
    visited_locations.clear()
    collected_items.clear()

    print("\n" + "=" * 50)
    print("🏝️  ДОБРО ПОЖАЛОВАТЬ НА ОСТРОВ ПРОКЛЯТЫХ! 🏝️")
    print("=" * 50)
    print("Ваш корабль разбился о скалы. Вы очнулись на берегу таинственного острова...")

    if not choose_starting_item():
        return

    log_move("Начало игры на острове")
    beach_choice()


def beach_choice():
    visited_locations.add("Пляж")
    print("\n" + "=" * 30)
    print("🌊 ВЫ НА ПЛЯЖЕ")
    print("=" * 30)
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
        if current_item and current_item not in start_items:
            start_items.append(current_item)
        save_items()
        print("📦 Предмет возвращен в копилку")


def jungle_path():
    visited_locations.add("Джунгли")
    print("\n" + "=" * 30)
    print("🌴 ВЫ В ДЖУНГЛЯХ")
    print("=" * 30)
    print("Воздух густой и влажный.")
    print("Вдруг перед вами появляется древний дух острова! 👻")
    print("Дух предлагает испытание мудрости...")

    print("\n1. Принять испытание")
    print("2. Отказаться и вернуться")
    print("3. Искать другой путь")
    print("4. Сохранить игру 💾")

    choice = get_valid_input("Ваш выбор (1-4): ", ["1", "2", "3", "4"])

    if choice == "1":
        wisdom_test()
    elif choice == "2":
        safe_return("Вы отказались от испытания и вернулись на пляж")
    elif choice == "3":
        # НОВОЕ ПЕРВОЕ ОТВЕТВЛЕНИЕ: Таинственная тропа
        mysterious_path()
    elif choice == "4":
        show_save_menu("jungle")


def wisdom_test():
    print("\n🧠 Дух задает загадку:")
    print("'Что можно сломать, даже не прикасаясь к нему?'")

    answer = input("Ваш ответ: ").strip().lower()
    log_move(f"Ответ на загадку: {answer}")

    if answer == "обещание" or answer == "молчание" or answer == "слово":
        print("✅ Дух доволен вашей мудростью!")
        temple_ruins()
    else:
        print("❌ Дух качает головой...")
        print("Правильный ответ: 'Обещание'")
        lose_item_to_spirit()


# НОВОЕ ПЕРВОЕ ОТВЕТВЛЕНИЕ: Таинственная тропа
def mysterious_path():
    visited_locations.add("Таинственная тропа")
    print("\n" + "=" * 30)
    print("🛤️ ТАИНСТВЕННАЯ ТРОПА")
    print("=" * 30)
    print("Вы нашли скрытую тропу в джунглях...")
    print("Она ведет к древнему камню с надписями.")

    print("\n1. Прочитать надписи")
    print("2. Обойти камень")
    print("3. Вернуться назад")

    choice = get_valid_input("Ваш выбор (1-3): ", ["1", "2", "3"])

    if choice == "1":
        print("\n📖 Надпись гласит: 'Тот, кто разгадает загадку ветра, найдет истинный путь.'")

        if simple_riddle():
            print("\n🌀 Ветер подхватывает вас и уносит в небо!")
            print("Вы парите над островом и видите путь к спасению!")

            # НОВАЯ КОНЦОВКА 1
            end_game(
                "Загадка ветра открыла вам секреты острова. Вы нашли древний летающий корабль и уплыли в закат, став легендой.",
                True)
        else:
            print("\n💨 Ничего не происходит...")
            mysterious_path()
    elif choice == "2":
        print("\nВы обходите камень и находите маленький сундук!")
        if spirit_items:
            item = random.choice(spirit_items)
            spirit_items.remove(item)
            collected_items.append(item)
            print(f"✨ Вы нашли: {item}")
            save_items()
        else:
            print("Но сундук пуст...")
        mysterious_path()
    elif choice == "3":
        jungle_path()


def temple_ruins():
    visited_locations.add("Руины храма")
    print("\n" + "=" * 30)
    print("🏛️ РУИНЫ ХРАМА")
    print("=" * 30)
    print("На алтаре лежат ритуальные предметы...")

    if spirit_items:
        print("\n🎭 ДОСТУПНЫЕ ПРЕДМЕТЫ ДУХОВ:")
        for i, item in enumerate(spirit_items, 1):
            print(f"{i}. {item}")

        print(f"\n{len(spirit_items) + 1}. Не брать ничего")
        print(f"{len(spirit_items) + 2}. Исследовать дальше храм")
        print(f"{len(spirit_items) + 3}. Сохранить игру 💾")
        print(f"{len(spirit_items) + 4}. Вернуться на пляж")

        try:
            choice = input(f"Выберите действие (1-{len(spirit_items) + 4}): ")

            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(spirit_items):
                    selected = spirit_items.pop(choice_num - 1)
                    collected_items.append(selected)
                    log_move(f"Получен предмет духа: {selected}")
                    print(f"✨ Вы взяли: {selected}")
                    print("'Энергия острова усиливается...'")
                    save_items()
                    final_choice()
                elif choice_num == len(spirit_items) + 1:
                    print("Вы ничего не берете...")
                    final_choice()
                elif choice_num == len(spirit_items) + 2:
                    # НОВОЕ ВТОРОЕ ОТВЕТВЛЕНИЕ: Секретная пещера
                    secret_cave()
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
        final_choice()


# НОВОЕ ВТОРОЕ ОТВЕТВЛЕНИЕ: Секретная пещера
def secret_cave():
    visited_locations.add("Секретная пещера")
    print("\n" + "=" * 30)
    print("💎 СЕКРЕТНАЯ ПЕЩЕРА")
    print("=" * 30)
    print("За алтарем вы нашли скрытый проход...")
    print("В пещере светятся кристаллы и стоит странный механизм.")

    print("\n1. Изучить механизм")
    print("2. Собрать кристаллы")
    print("3. Вернуться в храм")

    choice = get_valid_input("Ваш выбор (1-3): ", ["1", "2", "3"])

    if choice == "1":
        print("\n⚙️ Механизм имеет три кнопки с цифрами.")
        print("На стене надпись: 'Только правильный выбор откроет истину.'")

        if guess_number():
            print("\n🔓 Механизм оживает! Стена отодвигается...")
            print("За ней вы видите древний портал!")

            # НОВАЯ КОНЦОВКА 2
            end_game("Портал переносит вас в другое измерение. Вы становитесь хранителем древних знаний между мирами.",
                     True)
        else:
            print("\n🔒 Механизм не реагирует...")
            secret_cave()
    elif choice == "2":
        print("\n💎 Вы собираете светящиеся кристаллы.")
        if len(collected_items) < 3:
            # Добавляем специальный кристалл
            special_item = "💎 Сияющий кристалл"
            collected_items.append(special_item)
            print(f"✨ Вы получили: {special_item}")
            print("Кристаллы наполняют вас энергией!")
        else:
            print("Но у вас уже слишком много предметов...")
        secret_cave()
    elif choice == "3":
        temple_ruins()


def cliffs_path():
    visited_locations.add("Утесы")
    print("\n" + "=" * 30)
    print("🧗 ВЫ НА УТЕСАХ")
    print("=" * 30)
    print("На вершине вы встречаете старого отшельника 🧔")

    print("\n1. Поговорить с отшельником")
    print("2. Вернуться на пляж")
    print("3. Сохранить игру 💾")

    choice = get_valid_input("Ваш выбор (1-3): ", ["1", "2", "3"])

    if choice == "1":
        print("\nОтшельник говорит: 'Остров проклят древним заклинанием...'")
        print("'Собери 3 ритуальных предмета для ритуала очищения.'")
        if len(collected_items) >= 3:
            print("✅ У вас достаточно предметов!")
            perform_ritual()
        else:
            print(f"⚠️ У вас только {len(collected_items)} предмет(ов). Нужно больше!")
            beach_choice()
    elif choice == "2":
        safe_return("Вы спустились с утесов")
    elif choice == "3":
        show_save_menu("cliffs")


def cave_path():
    visited_locations.add("Пещера")
    print("\n" + "=" * 30)
    print("🕳️ ВЫ В ПЕЩЕРЕ")
    print("=" * 30)
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
                temple_ruins()
                return
            else:
                print("❌ Не угадал!")
        except ValueError:
            print("⚠️ Введите число!")

    print("💀 Портал поглощает ваш предмет!")
    lose_item_to_spirit()


def lose_item_to_spirit():
    if current_item in collected_items:
        collected_items.remove(current_item)
        spirit_items.append(current_item)
        save_items()
        log_move(f"Предмет потерян: {current_item}")
        print(f"💨 {current_item} перешел к духам острова")

    if not collected_items:
        end_game("Вы потеряли все предметы. Проклятие острова поглотило вас.", False)
    else:
        beach_choice()


def perform_ritual():
    print("\n" + "🔥" * 20)
    print("🔥 ВЫПОЛНЕНИЕ РИТУАЛА 🔥")
    print("🔥" * 20)
    print("Отшельник помогает вам провести древний обряд...")

    if len(collected_items) >= 3:
        print("✨ Ритуал удался! Проклятие снято!")
        end_game("Вы очистили остров от проклятия и нашли путь домой!", True)
    else:
        print("❌ Недостаточно сил для ритуала!")
        beach_choice()


def final_choice():
    print("\n" + "=" * 30)
    print("🌅 РЕШАЮЩИЙ ВЫБОР")
    print("=" * 30)
    print("1. Попытаться снять проклятие")
    print("2. Построить плот и уплыть")
    print("3. Остаться жить на острове")
    print("4. Сохранить игру 💾")

    choice = get_valid_input("Ваш выбор (1-4): ", ["1", "2", "3", "4"])

    if choice == "1":
        if len(collected_items) >= 3:
            perform_ritual()
        else:
            print("⚠️ У вас недостаточно ритуальных предметов!")
            beach_choice()
    elif choice == "2":
        end_game("Вы построили плот и уплыли с острова... но проклятие последовало за вами.", False)
    elif choice == "3":
        end_game("Вы приняли остров как свой дом и стали его хранителем.", True)
    elif choice == "4":
        show_save_menu("temple")


def safe_return(message):
    log_move(message)
    print(f"\n🛡️ {message}")
    beach_choice()


def end_game(outcome, success):
    log_move(f"Итог: {outcome}")

    print("\n" + "=" * 50)
    print("🎮 ИГРА ЗАВЕРШЕНА")
    print("=" * 50)
    print(f"Концовка: {outcome}")

    if success:
        print("✅ ВЫ ДОСТИГЛИ УСПЕХА!")
    else:
        print("❌ ВЫ ПОТЕРПЕЛИ НЕУДАЧУ")

    print(f"\n📍 Посещенные места: {', '.join(visited_locations)}")
    print(f"📦 Собранные предметы: {', '.join(collected_items) if collected_items else 'нет'}")

    # Запись в файл
    with open("island_log.txt", "a", encoding="utf-8") as file:
        file.write("\n" + "=" * 40 + "\n")
        file.write("Новая игра\n")
        for move in moves_log:
            file.write(f"- {move}\n")
        file.write(f"Результат: {outcome}\n")
        file.write(f"Успех: {success}\n")

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
        # Возвращаем все предметы обратно
        for item in collected_items:
            if item in ["🌊 Ракушка Приливов", "🔥 Огненный Кремень", "🌿 Лист Древнего Древа",
                        "💎 Глаз Бури", "🐚 Рог Морского Царя", "🌙 Лунный Камень",
                        "☀️ Солнечный Кристалл", "🌀 Перо Ветров"]:
                if item not in start_items:
                    start_items.append(item)
            else:
                if item not in spirit_items:
                    spirit_items.append(item)

        # Удаляем файл сохранения если он есть
        if os.path.exists("save_game.json"):
            os.remove("save_game.json")

        save_items()
        print("💰 Все предметы возвращены в копилку!")

    input("\nНажмите Enter чтобы вернуться в главное меню...")


# Главное меню
def main_menu():
    load_items()

    print("\n" + "=" * 50)
    print("🌴 ОСТРОВ ПРОКЛЯТЫХ - ГЛАВНОЕ МЕНЮ")
    print("=" * 50)

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