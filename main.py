import math
import re
import toml
import argparse


constants = {}

def parse_arguments(args=None):
    parser = argparse.ArgumentParser(
        description="Инструмент для преобразования TOML в учебный язык."
    )
    parser.add_argument(
        "--input_file",
        required=True,
        help="Путь к TOML файлу"
    )
    parser.add_argument(
        "--output_file",
        required=True,
        help="Путь к выходному файлу"
    )
    if args:
        return parser.parse_args(args)
    return parser.parse_args()
    
def read_toml_file(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Обработка глобальных констант
        non_const_lines = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith("global"):
                parse_global_const(stripped_line)
            else:
                non_const_lines.append(line)

        # Парсинг остальных данных
        return toml.loads("".join(non_const_lines))
    except toml.TomlDecodeError as e:
        raise ValueError(f"Ошибка в TOML: {e}")
    except FileNotFoundError as e:
        raise ValueError(f"Файл не найден: {e}")

def parse_global_const(line):
    match = re.match(r"global\s+([_a-z]+)\s*=\s*(.+)", line) # регулярное выражение
    """
    r - raw string
    global - нужное нам слово
    \s - любой пробел
    + - обозначает символ, который повторяется несколько раз
    [_a-z]+ - символы из этого алфавита 1 и бболее
    * - мб любое количество символов (0-inf)
    . - любой символ кроме перевода строки
    """
    if not match:
        raise ValueError(f"Строка неправильная: {line}")
    name, value = match.groups()
    if name in constants:
        raise ValueError(f"такая константа {name} уже имеется")
    constants[name] = eval(value)  # Преобразование строки в число или строку
    return constants
    
def evaluate_expression(expr):
    expr = expr.strip()
    for name, value in constants.items():
        expr = expr.replace(name, str(value))
    
    allowed_globals = {"max": max, "pow": pow, "math": math}
    try:
        return eval(expr, {"__builtins__":None}, allowed_globals)
    except Exception as e:
        raise ValueError(f"Ошибка вычисления выражения '{expr}': {e}")
        
def validate_name(name : str):
    """
    Проверка, соответствует ли имя правилам [_a-z]+
    """
    if not re.match(r"^[_a-z]+$",name): # регулярное выражение
        # r - raw string - нужно для интерпретирования \ и другиих символов экранирования
        # ^ - начало строки (совпадение должно начинаться с самого начала)
        # [_a-z] - разрешимый алфавит
        # + - как минимум один символ должен быть
        # $ - конец строки
        raise ValueError(f"Имя неправильное: {name}")
    
def tranform_value(value : int|float|list|dict):
    """
    Преобразование значения в нужный формат
    """
    if isinstance(value, (int,float)):
        result = str(value)
    elif isinstance(value, str):
        if value.startswith("@{") and value.endswith("}"):
            expr = value[2:-1]
            return evaluate_expression(expr)
        result = f'"{value}"'
    elif isinstance(value, list):
        result = "<< "
        for i in value:
            if i != value[-1]:
                result += str(i) + ", "
            else:
                result += str(i) + " >>"
    elif isinstance(value, dict):
        result = "[\n"
        result += ",\n".join(f"   {k} => {tranform_value(v)}" 
                    for k, v in value.items()) + "\n]"
    else:
        raise ValueError(f'Неподдерживаемое значение: {value}')
    return result

def transfotm_toml(data):
    lines = []
    for key, value in data.items():
        validate_name(key)
        transformed = tranform_value(value)
        lines.append(f'{key} = {transformed}')
    return "\n".join(lines)

def write_output(file_path, data):
    try:
        with open(file_path,'w') as file:
            file.write(data)
    except FileNotFoundError as e:
        raise ValueError(f'файл не найден {e}')

if __name__ == "__main__":
    args = parse_arguments()
    #print('___________________________')
    #print(args.input_file)
    print('Чтение...')
    input_file = read_toml_file(args.input_file)
    print('Преобразование...')
    result_data = transfotm_toml(input_file)
    print('Запись...')
    write_output(args.output_file, result_data)
    print(f"Файл успешно сохранён: {args.output_file}")
