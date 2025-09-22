import os

def expand_variables(command):
    for key, value in os.environ.items():
        placeholder1 = f"${key}"
        placeholder2 = f"${{{key}}}"
        command = command.replace(placeholder1, value)
        command = command.replace(placeholder2, value)

    if '$' in command:
        print("ошибка: переменная не найдена")
        return None

    return command


def parse_command(line):
    if not line.strip():
        return None, []
    expanded = expand_variables(line.strip())
    if expanded is None:
        return None, []
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