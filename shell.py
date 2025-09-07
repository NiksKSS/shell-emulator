import os

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

def main():
    vfs_name = "VFS"
    prompt = f"{vfs_name}$ "

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