import os
import sys  # для чтения аргументов командной строки
import json

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

def load_vfs(path):#загрузка VFS из json
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ошибка: файл VFS не найден: {path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"ошибка: некорректный JSON в VFS: {e}")
        return {}

def get_node(vfs, path):
    if not path or path == "/":
        return vfs
    parts = [p for p in path.strip("/").split("/") if p]
    current = vfs
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current

def main():
    vfs_path, script_path = parse_args()
    # Отладочный вывод переданных параметров
    print(f"[DEBUG] vfs_path = {vfs_path}")
    print(f"[DEBUG] script_path = {script_path}")
    print("-" * 40)
    vfs = {}
    current_path = "/"
    if vfs_path:
        vfs = load_vfs(vfs_path)
        if not vfs:
            print("VFS не загружена, система пуста.")

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
                    elif cmd == "ls":
                        target = args[0] if args else current_path
                        node = get_node(vfs, target)
                        if node is None:
                            print(f"ls: {target}: Нет такого файла или каталога")
                        elif isinstance(node, dict):
                            print(" ".join(node.keys()))
                        else:
                            print(f"ls: {target}: не каталог")
                    elif cmd == "cd":
                        if not args:
                            current_path = "/"
                        else:
                            target = args[0]
                            if target.startswith("/"):
                                new_path = target
                            else:
                                new_path = f"{current_path.rstrip('/')}/{target}"

                            parts = []
                            for part in new_path.strip("/").split("/"):
                                if part == "..":
                                    if parts:
                                        parts.pop()
                                elif part and part != ".":
                                    parts.append(part)
                            resolved = "/" + "/".join(parts) if parts else "/"

                            node = get_node(vfs, resolved)
                            if node is None:
                                print(f"cd: {target}: Нет такого файла или каталога")
                            elif not isinstance(node, dict):
                                print(f"cd: {target}: не является каталогом")
                            else:
                                current_path = resolved
                    elif cmd == "cat":
                        if not args:
                            print("cat: отсутствует аргумент")
                        else:
                            for filename in args:
                                full_path = filename if filename.startswith("/") else f"{current_path.rstrip('/')}/{filename}"
                                content = get_node(vfs, full_path)
                                if content is None:
                                    print(f"cat: {filename}: Нет такого файла")
                                elif isinstance(content, dict):
                                    print(f"cat: {filename}: это каталог")
                                else:
                                    print(content)
                    elif cmd == "uniq":
                        if not args:
                            lines = []
                            print("Введите строки (двойной Enter для завершения):")
                            while True:
                                try:
                                    line = input()
                                    if not line:
                                        break
                                    lines.append(line)
                                except EOFError:
                                    break
                            if lines:
                                prev = None
                                for line in lines:
                                    if line != prev:
                                        print(line)
                                        prev = line
                        else:
                            filename = args[0]
                            full_path = filename if filename.startswith("/") else f"{current_path.rstrip('/')}/{filename}"
                            content = get_node(vfs, full_path)
                            if content is None:
                                print(f"uniq: {filename}: Нет такого файла")
                            elif isinstance(content, dict):
                                print(f"uniq: {filename}: это каталог")
                            else:
                                lines = content.splitlines()
                                prev = None
                                for line in lines:
                                    if line != prev:
                                        print(line)
                                        prev = line
                    elif cmd == "cp":
                        if len(args) < 2:
                            print("cp: отсутствует аргумент")
                        else:
                            src = args[0]
                            dst = args[1]

                            src_path = src if src.startswith("/") else f"{current_path.rstrip('/')}/{src}"
                            dst_path = dst if dst.startswith("/") else f"{current_path.rstrip('/')}/{dst}"

                            dst_parent_path = "/".join(dst_path.strip("/").split("/")[:-1])
                            dst_name = dst_path.strip("/").split("/")[-1] if dst_path.strip("/") else ""

                            src_node = get_node(vfs, src_path)
                            if src_node is None:
                                print(f"cp: {src}: Нет такого файла или каталога")
                                continue

                            dst_parent = get_node(vfs, dst_parent_path) if dst_parent_path else vfs
                            if dst_parent is None:
                                print(f"cp: {dst_parent_path or '/'}: Нет такого каталога")
                                continue
                            if not isinstance(dst_parent, dict):
                                print(f"cp: {dst_parent_path or '/'}: не является каталогом")
                                continue

                            dst_full_node = get_node(vfs, dst_path)
                            if isinstance(dst_full_node, dict):
                                src_name = src_path.strip("/").split("/")[-1]
                                if src_name:
                                    if src_name in dst_full_node:
                                        print(f"cp: {dst_path}/{src_name}: файл уже существует")
                                    else:
                                        dst_full_node[src_name] = src_node
                                else:
                                    print(f"cp: невозможно определить имя файла")
                            else:
                                if dst_name in dst_parent:
                                    print(f"cp: {dst_path}: файл уже существует")
                                else:
                                    dst_parent[dst_name] = src_node
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
            elif cmd == "ls":
                target = args[0] if args else current_path
                node = get_node(vfs, target)
                if node is None:
                    print(f"ls: {target}: Нет такого файла или каталога")
                elif isinstance(node, dict):
                    print(" ".join(node.keys()))
                else:
                    print(f"ls: {target}: не каталог")
            elif cmd == "cd":
                if not args:
                    current_path = "/"
                else:
                    target = args[0]
                    if target.startswith("/"):
                        new_path = target
                    else:
                        new_path = f"{current_path.rstrip('/')}/{target}"

                    parts = []
                    for part in new_path.strip("/").split("/"):
                        if part == "..":
                            if parts:
                                parts.pop()
                        elif part and part != ".":
                            parts.append(part)
                    resolved = "/" + "/".join(parts) if parts else "/"

                    node = get_node(vfs, resolved)
                    if node is None:
                        print(f"cd: {target}: Нет такого файла или каталога")
                    elif not isinstance(node, dict):
                        print(f"cd: {target}: не является каталогом")
                    else:
                        current_path = resolved
            elif cmd == "cat":
                if not args:
                    print("cat: отсутствует аргумент")
                else:
                    for filename in args:
                        full_path = filename if filename.startswith("/") else f"{current_path.rstrip('/')}/{filename}"
                        content = get_node(vfs, full_path)
                        if content is None:
                            print(f"cat: {filename}: Нет такого файла")
                        elif isinstance(content, dict):
                            print(f"cat: {filename}: это каталог")
                        else:
                            print(content)
            elif cmd == "uniq":
                if not args:
                    lines = []
                    print("Введите строки (двойной Enter для завершения):")
                    while True:
                        try:
                            line = input()
                            if not line:
                                break
                            lines.append(line)
                        except EOFError:
                            break
                    if lines:
                        prev = None
                        for line in lines:
                            if line != prev:
                                print(line)
                                prev = line
                else:
                    filename = args[0]
                    full_path = filename if filename.startswith("/") else f"{current_path.rstrip('/')}/{filename}"
                    content = get_node(vfs, full_path)
                    if content is None:
                        print(f"uniq: {filename}: Нет такого файла")
                    elif isinstance(content, dict):
                        print(f"uniq: {filename}: это каталог")
                    else:
                        lines = content.splitlines()
                        prev = None
                        for line in lines:
                            if line != prev:
                                print(line)
                                prev = line
            elif cmd == "cp":
                if len(args) < 2:
                    print("cp: отсутствует аргумент")
                else:
                    src = args[0]
                    dst = args[1]

                    src_path = src if src.startswith("/") else f"{current_path.rstrip('/')}/{src}"
                    dst_path = dst if dst.startswith("/") else f"{current_path.rstrip('/')}/{dst}"

                    dst_parent_path = "/".join(dst_path.strip("/").split("/")[:-1])
                    dst_name = dst_path.strip("/").split("/")[-1] if dst_path.strip("/") else ""

                    src_node = get_node(vfs, src_path)
                    if src_node is None:
                        print(f"cp: {src}: Нет такого файла или каталога")
                        continue

                    dst_parent = get_node(vfs, dst_parent_path) if dst_parent_path else vfs
                    if dst_parent is None:
                        print(f"cp: {dst_parent_path or '/'}: Нет такого каталога")
                        continue
                    if not isinstance(dst_parent, dict):
                        print(f"cp: {dst_parent_path or '/'}: не является каталогом")
                        continue

                    dst_full_node = get_node(vfs, dst_path)
                    if isinstance(dst_full_node, dict):
                        src_name = src_path.strip("/").split("/")[-1]
                        if src_name:
                            if src_name in dst_full_node:
                                print(f"cp: {dst_path}/{src_name}: файл уже существует")
                            else:
                                dst_full_node[src_name] = src_node
                        else:
                            print(f"cp: невозможно определить имя файла")
                    else:
                        if dst_name in dst_parent:
                            print(f"cp: {dst_path}: файл уже существует")
                        else:
                            dst_parent[dst_name] = src_node
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