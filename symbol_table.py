# name:(idx,    kind,     type,     val,     nParam)
# kind: 'var', 'let' (const), 'func'
# val: 'undefined', 'assigned', or literal value for 'let'
tabName = {
    'univ': {'declIn': '-'}
}

# Поточна область видимості
currentContext = 'univ'

# Стек для відстеження функцій (для перевірки return)
# Кожен елемент: {'name': str, 'return_type': str}
functionContextStack = []

#Функція для семантичних помилок
def failSem(message, line_num=''):
    line_info = f"in line {line_num}" if line_num else ""
    print(f"Semantic ERROR {line_info}: \n\t {message}")
    exit(10)

#Додає ім'я в таблицю, перевіряє на повторне оголошення (правило 2)
def insertName(cxt, name, line, attr):
    try:
        if name in tabName[cxt]:

            failSem(f"Repeated announcement ‘{name}’ in visibility area '{cxt}'", line)
        tabName[cxt][name] = attr
        print(f"Semantic: Inserted {name} into {cxt} with {attr}")
        return True
    except KeyError:
        failSem(f"Unknown visibility area '{cxt}'", line)

#Шукає ім'я в поточній та батьківських областях перевіряє на неоголошені (правило 3)
def findName(name, cxt, line):

    contexts = []
    try:
        current_cxt = cxt
        while current_cxt != '-':
            contexts.append(current_cxt)
            if name in tabName[current_cxt]:
                attr = tabName[current_cxt][name]
                res = (current_cxt, name, attr)
                # print(f"DEBUG: Found {name} in {current_cxt}")
                return res
            current_cxt = tabName[current_cxt]['declIn']


        failSem(f"Use of undeclared variable ‘{name}’. Checked areas: {contexts}", line)
    except KeyError:
        failSem(f"Error searching for name ‘{name}’ in {cxt}", line)

#Оновлює поле 'val' для змінної (на 'assigned')
def updateNameVal(name, cxt, line, newValue):

    try:
        current_cxt = cxt
        while current_cxt != '-':
            if name in tabName[current_cxt]:
                attr = tabName[current_cxt][name]
                # Оновлюємо значення, зберігаючи решту атрибутів
                tabName[current_cxt][name] = (attr[0], attr[1], attr[2], newValue, attr[4])
                # print(f"DEBUG: Updated {name} in {current_cxt} to val={newValue}")
                return
            current_cxt = tabName[current_cxt]['declIn']

        # Це не мало б статись, якщо findName було викликано раніше
        failSem(f"Cannot update undeclared variable '{name}'", line)

    except KeyError:
        failSem(f"Error updating name ‘{name}’ in {cxt}", line)


# --- Допоміжні функції перевірки типів ---

#Перевіряє типи для арифметичних операцій (правила 11, 12, 15)
def check_arithm_op(l_type, op, r_type, line):

    # --- Правило 12: Обробка String ---
    if l_type == 'string' or r_type == 'string':
        # Дозволяємо 'string' + 'string' (конкатенація)
        if op == '+' and l_type == 'string' and r_type == 'string':
            return 'string'
        else:
            # Забороняємо всі інші операції
            failSem(f"The operation ‘{op}’ cannot be applied to ‘{l_type}’ and '{r_type}'", line)
            return 'type_error'

    # --- Правило 12: Обробка Bool ---
    if l_type == 'bool' or r_type == 'bool':
        failSem(f"The arithmetic operation ‘{op}’ cannot be applied to ‘{l_type}’ and ‘{r_type}’", line)
        return 'type_error'

    # --- Правило 15: int + float -> float ---
    if l_type == 'float' and r_type == 'int':
        return 'float'
    if l_type == 'int' and r_type == 'float':
        return 'float'

    if l_type == 'float' and r_type == 'float':
        return 'float'

    # --- Правило 11: int / int -> int ---
    if l_type == 'int' and r_type == 'int':
        if op == '/':
            return 'int'  # Цілочисельне ділення
        return 'int'

    failSem(f"Unknown combination of types for operation ‘{op}’: ‘{l_type}’ and '{r_type}'", line)
    return 'type_error'


#Перевіряє типи для операцій порівняння (правила 12, 14)
def check_rel_op(l_type, op, r_type, line):

    # Правило 12: bool та string можна порівнювати тільки між собою
    if l_type in ('bool', 'string') or r_type in ('bool', 'string'):
        if l_type != r_type:
            failSem(f"The comparison operation ‘{op}’ cannot be applied to ‘{l_type}’ and '{r_type}'", line)
        return  # 'bool' == 'bool' or 'string' == 'string' - це ОК

    # Правило 14: int та float можна порівнювати
    if l_type in ('int', 'float') and r_type in ('int', 'float'):
        return  # ОК

    failSem(f"The comparison operation ‘{op}’ cannot be applied to ‘{l_type}’ and '{r_type}'", line)


#перевіряє типи для присвоєння (правила 16, 17)
def check_assign(var_type, expr_type, line):

    if var_type == expr_type:
        return  # Типи збігаються

    # Правило 16: float = int
    if var_type == 'float' and expr_type == 'int':
        return  # Дозволено неявне перетворення

    # Правило 17: int = float
    if var_type == 'int' and expr_type == 'float':
        failSem(f"Cannot assign ‘float’ to a variable of type ‘int’ (implicit conversion is not allowed)", line)

    # Правило 12: bool/string
    if var_type in ('bool', 'string') or expr_type in ('bool', 'string'):
        failSem(f"Cannot assign ‘{expr_type}’ to variable of type '{var_type}'", line)

    failSem(f"Cannot assign ‘{expr_type}’ to variable of type '{var_type}'", line)

def check_return_type(var_type, expr_type, line):
    if var_type == expr_type:
        return  # Типи збігаються

    # Правило 16: float = int
    if var_type == 'float' and expr_type == 'int':
        return  # Дозволено неявне перетворення

    # Правило 17: int = float
    if var_type == 'int' and expr_type == 'float':
        failSem(f"Expected return type {var_type}, return typed used {expr_type}", line)

    # Правило 12: bool/string
    if var_type in ('bool', 'string') or expr_type in ('bool', 'string'):
        failSem(f"Expected return type {var_type}, return typed used {expr_type}", line)

