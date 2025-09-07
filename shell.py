import os
import sys  # для чтения аргументов командной строки


def expand_variables(command):
    ## Заменяет $HOME, ${USER} на настоящие значения из системы
    for key, value in os.environ.items():
        command = command.replace(f"${key}", value)
        command = command.replace(f"${{{key}}}", value)
    return command

def parse_command(line):
    ## Разбивает строку на команду и аргументы
    if not line.strip():
        return None, []
    expanded = expand_variables(line.strip())
    parts = expanded.split()
    if not parts:
        return None, []
    cmd = parts[0]
    args = parts[1:]
    return cmd, args

def parse_args():
    # Читаем аргументы: --vfs и --script
    args = sys.argv[1:]
    vfs_path = None
    script_path = None
    i = 0
    while i < len(args):
        if args[i] == "--vfs" and i + 1 < len(args):
            vfs_path = args[i + 1]
            i += 2
        elif args[i] == "--script" and i + 1 < len(args):
            script_path = args[i + 1]
            i += 2
        else:
            i += 1

    return vfs_path, script_path


def main():
    vfs_path, script_path = parse_args()
    # Отладочный вывод переданных параметров
    print(f"[DEBUG] vfs_path = {vfs_path}")
    print(f"[DEBUG] script_path = {script_path}")
    print("-" * 40)

    vfs_name = "VFS"
    prompt = f"{vfs_name}$ "
    # Выполнение команд из файла, если указан --script
    if script_path:
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                print(f"[SCRIPT] Выполняю команды из {script_path}")
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue  # пропускаем пустые и комментарии

                    print(f"{prompt}{line}")  # имитация ввода
                    cmd, args = parse_command(line)
                    if cmd is None:
                        continue

                    if cmd == "exit":
                        print("Выход из эмулятора.")
                        return
                    elif cmd in ["ls", "cd"]:
                        print(f"[заглушка] команда: {cmd}, аргументы: {args}")
                    else:
                        print(f"ошибка: неизвестная команда: {cmd}")

        except FileNotFoundError:
            print(f"ошибка: файл скрипта не найден: {script_path}")
        except Exception as e:
            print(f"ошибка при выполнении скрипта: {e}")
        return  # завершаем после скрипта

    # Интерактивный режим
    while True:
        try:
            user_input = input(prompt)
            cmd, args = parse_command(user_input)

            if cmd is None:
                continue

            if cmd == "exit":
                break

            elif cmd in ["ls", "cd"]:
                print(f"[заглушка] команда: {cmd}, аргументы: {args}")

            else:
                print(f"ошибка: неизвестная команда: {cmd}")

        except KeyboardInterrupt:
            print("\nПрервано пользователем.")
            break
        except EOFError:
            print("\nВыход из эмулятора.")
            break


if __name__ == "__main__":
    main()