from textwrap import indent

from lexer import lex
from lexer import tableOfSymb
from lexer import tableOfId
from lexer import tableOfConst

import symbol_table as st

FSuccess = lex()

print('-' * 50)
print('tableOfSymb:{0}'.format(tableOfSymb))
# print('tableOfId:{0}'.format(tableOfId))
# print('tableOfConst:{0}'.format(tableOfConst))
print('-' * 50)

# номер рядка таблиці розбору/лексем/символів ПРОГРАМИ tableOfSymb
numRow = 1

# довжина таблиці символів програми
# він же - номер останнього запису
len_tableOfSymb = len(tableOfSymb)
print(('len_tableOfSymb', len_tableOfSymb))


# Program = { Declaration | Statement | Comment } - кореневий нетермінал
def parseProgram():
    global numRow
    print("Parser: ")
    while numRow <= len_tableOfSymb:
        # прочитаємо поточну лексему в таблиці розбору
        numLine, lex, tok = getSymb()

        if lex == 'var' or lex == 'let':  # декларація
            parseDeclaration()
        elif lex in ('if', 'for', 'while', 'repeat', 'switch', 'guard', 'input', 'print', 'func',
                     'return') or tok == 'id':
            parseStatement()
        elif tok == 'comment':  # коментарі
            numRow += 1
        else:
            # жодна з інструкцій не відповідає
            # поточній лексемі у таблиці розбору,
            failParse('incompatibility of instructions',
                      (numLine, lex, tok, ' Declaration | Statement | Comment expected '))


def parseStatement():
    indent = nextIndt()
    print(indent + 'parseStatement():')
    global numRow

    numLine, lex, tok = getSymb()
    if tok == 'id':
        id_info = (numLine, lex, tok)  # Зберігаємо l-value
        print(indent + 'в рядку {0} - токен {1}'.format(numLine, (lex, tok)))
        numRow += 1
        parseAssign(id_info)  # Передаємо l-value
    elif (lex, tok) == ('if', 'keyword'):
        parseIf()
    elif (lex, tok) == ('while', 'keyword'):
        parseWhile()
    elif (lex, tok) == ('repeat', 'keyword'):
        parseRepeatWhile()
    elif (lex, tok) == ('switch', 'keyword'):
        parseSwitch()
    elif (lex, tok) == ('guard', 'keyword'):
        parseGuard()
    elif (lex, tok) == ('for', 'keyword'):
        parseFor()
    elif (lex, tok) == ('print', 'keyword'):
        parsePrint()
    elif (lex, tok) == ('func', 'keyword'):
        parseFunctionDeclaration()
    elif (lex, tok) == ('return', 'keyword'):
        parseReturnStatement()
    else:
        failParse('невідповідність інструкцій', (numLine, lex, tok, 'очікувався statement'))

    indent = predIndt()


# WhileStatement = “while” “(“ Condition “)” “{“ StatementList “}
def parseWhile():
    global numRow
    indent = nextIndt()
    print(indent + 'parseWhile():')

    parseToken('while', 'keyword')
    parseToken('(', 'brackets_op')
    parseBooleanCondition()
    parseToken(')', 'brackets_op')
    parseToken('{', 'brackets_op')

    while numRow <= len_tableOfSymb and getSymb()[1] != '}':
        parseStatement()

    parseToken('}', 'brackets_op')

    indent = predIndt()


# CycleRep = ‘repeat’ ‘{’  Body ‘while’  BoolExpression ‘}’
def parseRepeatWhile():
    global numRow
    indent = nextIndt()
    print(indent + 'parseRepeatWhile():')
    parseToken('repeat', 'keyword')
    parseToken('{', 'brackets_op')

    while numRow <= len_tableOfSymb and getSymb()[1] != '}':
        parseStatement()
    parseToken('}', 'brackets_op')
    parseToken('while', 'keyword')
    parseBooleanCondition()

    indent = predIndt()


# Out = print ‘(‘ Ident | String | Expression ‘)’
def parsePrint():
    global numRow
    indent = nextIndt()
    print(indent + 'parsePrint():')

    parseToken('print', 'keyword')

    parseToken('(', 'brackets_op')

    numLine, lex, tok = getSymb()

    if tok == 'id':
        # Правило 3: Перевірка r-value
        st.findName(lex, st.currentContext, numLine)
        print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))
        # Ми не робимо numRow += 1, бо parseExpression() це зробить
        parseExpression()
    elif tok == 'str':
        numRow += 1
    else:
        # Дозволимо друкувати будь-який вираз
        parseExpression()

    parseToken(')', 'brackets_op')
    indent = predIndt()


# SwitchStatement = ‘switch’ Ident ‘{’ {CaseElems}
#           [DefaultElems]‘}’
# CaseBlock = ‘case’ [‘-’] Integer ‘:’ StatementList
# DefaultElems = ‘default’ ‘:’ StatementList
def parseSwitch():
    global numRow
    indent = nextIndt()
    print(indent + 'parseSwitch():')

    # switch keyword
    parseToken('switch', 'keyword')

    # ідентифікатор (змінна в дужках)
    numLine, lex, tok = getSymb()
    if tok == 'id':
        print(indent + ' in line {0} - token {1}'.format(numLine, (lex, tok)))
        numRow += 1
    else:
        failParse('switch was expected after identifier', (numLine, lex, tok))

    # фігурна дужка відкриття
    parseToken('{', 'brackets_op')

    # цикл по case або default
    while numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()

        if lex == 'case':
            parseCaseBlock()
        elif lex == 'default':
            parseDefaultBlock()
        elif lex == '}':
            break
        else:
            failParse('case, default або "}" were expected', (numLine, lex, tok))

    # закриваюча дужка
    parseToken('}', 'brackets_op')
    indent = predIndt()


def parseGuard():
    global numRow
    indent = nextIndt()
    print(indent + 'parseGuard():')

    # guard keyword
    parseToken('guard', 'keyword')

    # (
    parseToken('(', 'brackets_op')
    parseBooleanCondition()
    # )
    parseToken(')', 'brackets_op')

    # else
    parseToken('else', 'keyword')

    # { StatementList }
    parseToken('{', 'brackets_op')
    while numRow <= len_tableOfSymb and getSymb()[1] != '}':
        parseStatement()
    parseToken('}', 'brackets_op')

    indent = predIndt()


def parseFor():
    global numRow
    indent = nextIndt()
    print(indent + 'parseFor():')

    # for keyword
    parseToken('for', 'keyword')

    # (
    parseToken('(', 'brackets_op')

    # initialization
    numLine, lex, tok = getSymb()
    if tok == 'id':
        id_info = (numLine, lex, tok)
        print(indent + f'in line {numLine} - token {lex, tok}')
        numRow += 1
        parseAssign(id_info)
    elif lex in ('var', 'let'):
        parseDeclaration()
    else:
        failParse('for initialization expected', (numLine, lex, tok, 'identifier or var/let declaration'))

    # ;
    parseToken(';', 'punct')

    # condition
    parseBooleanCondition()

    # ;
    parseToken(';', 'punct')

    # increment
    numLine, lex, tok = getSymb()
    if tok == 'id':
        id_info = (numLine, lex, tok)
        print(indent + f'in line {numLine} - token {lex, tok}')
        numRow += 1
        parseAssign(id_info)
    else:
        failParse('for increment expected', (numLine, lex, tok, 'identifier'))

    # )
    parseToken(')', 'brackets_op')

    # body { StatementList }
    parseToken('{', 'brackets_op')
    while numRow <= len_tableOfSymb and getSymb()[1] != '}':
        parseStatement()
    parseToken('}', 'brackets_op')

    indent = predIndt()


def parseDefaultBlock():
    global numRow
    indent = nextIndt()
    print(indent + 'parseDefaultBlock():')

    parseToken('default', 'keyword')
    parseToken(':', 'punct')

    # Виконуємо всі statements поки не зустрінемо '}'
    while numRow <= len_tableOfSymb:
        nextLex = getSymb()[1]
        if nextLex == '}':
            break
        parseStatement()

    indent = predIndt()


def parseCaseBlock():
    global numRow
    indent = nextIndt()
    print(indent + 'parseCaseBlock():')

    parseToken('case', 'keyword')

    numLine, lex, tok = getSymb()
    if lex == '-':
        parseToken(lex, 'add_op')
        numLine, lex, tok = getSymb()

    if tok == 'intnum':
        print(indent + f' case number: {lex}')
        numRow += 1
    else:
        failParse('An integer number was expected after case', (numLine, lex, tok))

    parseToken(':', 'punct')

    # Statements до наступного case/default/закриття
    while numRow <= len_tableOfSymb:
        nextLex = getSymb()[1]
        if nextLex in ('case', 'default', '}'):
            break
        parseStatement()

    indent = predIndt()


def parseIf():
    global numRow
    indent = nextIndt()
    print(indent + 'parseIf():')

    # Використовуємо parseToken для чистоти коду
    parseToken('if', 'keyword')
    parseToken('(', 'brackets_op')
    parseBooleanCondition()
    parseToken(')', 'brackets_op')
    parseToken('{', 'brackets_op')

    while numRow <= len_tableOfSymb and getSymb()[1] != '}':
        parseStatement()

    parseToken('}', 'brackets_op')

    # Перевіряємо наявність 'else'
    if numRow <= len_tableOfSymb and getSymb()[1] == 'else':
        print(indent + '  founded else')
        parseToken('else', 'keyword')

        # Перевіряємо, чи це 'else if'
        if numRow <= len_tableOfSymb and getSymb()[1] == 'if':
            parseIf()  # Рекурсивний виклик для обробки 'else if'
        else:
            # Це звичайний 'else', розбираємо його блок
            parseToken('{', 'brackets_op')
            while numRow <= len_tableOfSymb and getSymb()[1] != '}':
                parseStatement()
            parseToken('}', 'brackets_op')

    indent = predIndt()


# Declaration = “var” IdentList “:” Type [ “=” Expression ];
def parseDeclaration():
    indent = nextIndt()
    print(indent + 'parseDeclaration():')
    global numRow

    numLine, lex, tok = getSymb()
    is_const = False

    if (lex, tok) == ('var', 'keyword'):
        kind = 'var'
        parseToken('var', 'keyword')
    elif (lex, tok) == ('let', 'keyword'):
        kind = 'let'
        is_const = True
        parseToken('let', 'keyword')
    else:
        failParse('token mismatch', (numLine, lex, tok, 'var | let'))

    # 1. Отримуємо список ідентифікаторів
    ident_list = parseIdentList()

    parseToken(':', 'punct')

    # 2. Отримуємо їх тип (Правило 1)
    declared_type = parseType()

    # 3. Перевіряємо на ініціалізацію
    val_status = 'undefined'  # Правило 4 (значення за замовчуванням)

    if numRow <= len_tableOfSymb and getSymb()[2] == 'assign_op':
        parseToken('=', 'assign_op')

        # 4. Отримуємо тип виразу
        expr_type = parseExpression()

        # 5. Перевіряємо типи (Правила 5, 16, 17)
        st.check_assign(declared_type, expr_type, numLine)

        val_status = 'assigned'  # Ініціалізовано
    elif is_const:
        # 'let' (константи) мають бути ініціалізовані
        st.failSem(f"The ‘let’ constant must be initialized when declared", numLine)

    # 6. Додаємо всі ідентифікатори в ST
    idx = len(st.tabName[st.currentContext]) - 1  # -1 бо 'declIn'
    for id_line, id_lex, id_tok in ident_list:
        attr = (idx, kind, declared_type, val_status, '-')
        st.insertName(st.currentContext, id_lex, id_line, attr)  # Правило 2 (перевірка на дублікат)
        idx += 1

    indent = predIndt()


# parseIdentList ПОВЕРТАЄ список
def parseIdentList():
    global numRow
    indent = nextIndt()
    print(indent + 'parseIdentList():')

    id_list = []  # Список для (numLine, lex, tok)

    numLine, lex, tok = getSymb()
    if tok != 'id':
        failParse('token mismatch', (numLine, lex, tok, 'identifier was expected'))

    id_list.append((numLine, lex, tok))
    print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))
    numRow += 1

    while numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()
        if (lex, tok) == (',', 'punct'):
            numRow += 1  # Пропускаємо кому

            numLine, lex, tok = getSymb()  # Дивимось на токен після коми
            if tok != 'id':
                failParse('token mismatch', (numLine, lex, tok, 'identifier was expected after comma'))

            id_list.append((numLine, lex, tok))
            print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))
            numRow += 1
        else:
            break

    indent = predIndt()
    return id_list  # Повертаємо список


# parseType ПОВЕРТАЄ тип
def parseType():
    global numRow
    indent = nextIndt()
    print(indent + 'parseType():')

    numLine, lex, tok = getSymb()

    if lex in ('int', 'float', 'string', 'bool') and tok == 'keyword':
        parseToken(lex, 'keyword')
        indent = predIndt()
        return lex  # Повертаємо рядок з типом
    else:
        failParse('token mismatch', (numLine, lex, tok, 'int | float | string | bool'))


# parseBooleanCondition перевіряє тип bool
def parseBooleanCondition():
    global numRow
    indent = nextIndt()
    print(indent + 'parseBooleanCondition():')

    line, _, _ = getSymb()
    expr_type = parseExpression()

    if expr_type != 'bool':
        st.failSem(f"The condition (in if, while, etc.) must be of type ‘bool’, not ‘{expr_type}’.", line)

    indent = predIndt()
    # Нічого не повертаємо, просто перевіряємо


def parseExpression():
    global numRow
    indent = nextIndt()
    print(indent + 'parseExpression():')
    numLine, lex, tok = getSymb()

    if tok == 'boolval' or lex == '!':
        expr_type = parseBoolExpression()
        indent = predIndt()
        return expr_type
    elif tok == 'str':
        numRow += 1
        indent = predIndt()
        return 'string'

    # Інакше це арифметичний вираз...
    l_type = parseArithmExpression()

    # ...який може бути частиною порівняння
    if numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()
        if tok == 'rel_op':
            op_line, op_lex = numLine, lex
            numRow += 1
            print(indent + f'  in line {numLine} - comparison token {(lex, tok)}')

            r_type = parseArithmExpression()

            # Правила 12, 14: Перевірка типів для операторів порівняння
            st.check_rel_op(l_type, op_lex, r_type, op_line)

            indent = predIndt()
            return 'bool'  # Правило 13: Результат порівняння - bool

    indent = predIndt()
    return l_type  # Якщо порівняння не було, повертаємо тип арифм. виразу


# BoolExpression = BoolTerm { ("||") BoolTerm }
def parseBoolExpression():
    global numRow
    indent = nextIndt()
    print(indent + 'parseBoolExpression():')

    parseBoolTerm()
    F = True
    while F and numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()
        if (lex, tok) == ('||', 'logic_op'):
            numRow += 1
            print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))
            parseBoolTerm()
        else:
            F = False

    indent = predIndt()
    return 'bool'  # Логічний вираз завжди повертає bool


# BoolTerm = BoolFactor { ("&&") BoolFactor }
def parseBoolTerm():
    global numRow
    indent = nextIndt()
    print(indent + 'parseBoolTerm():')

    parseBoolFactor()
    F = True
    while F and numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()
        if (lex, tok) == ('&&', 'logic_op'):
            numRow += 1
            print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))
            parseBoolFactor()
        else:
            F = False

    indent = predIndt()
    return 'bool'  # Логічний вираз завжди повертає bool


def parseBoolFactor():
    global numRow
    indent = nextIndt()
    print(indent + 'parseBoolFactor():')
    numLine, lex, tok = getSymb()

    if (lex, tok) == ('true', 'boolval'):
        parseToken('true', 'boolval')
    elif (lex, tok) == ('false', 'boolval'):
        parseToken('false', 'boolval')
    elif (lex, tok) == ('!', 'logic_op'):
        parseToken('!', 'logic_op')
        parseBoolFactor()
    elif (lex, tok) == ('(', 'brackets_op'):
        parseToken('(', 'brackets_op')
        parseExpression()  # Рекурсивний виклик для виразу в дужках
        parseToken(')', 'brackets_op')
    else:
        failParse('token mismatch', (numLine, lex, tok, 'true | false | ! | (Expression)'))

    indent = predIndt()
    return 'bool'  # Логічний вираз завжди повертає bool


# ArithmExpression = [Sign] Term { ("+" | "-") Term }
def parseArithmExpression():
    global numRow
    indent = nextIndt()
    print(indent + 'parseArithmExpression():')

    numLine, lex, tok = getSymb()
    if (lex, tok) in (('+', 'add_op'), ('-', 'add_op')):
        parseSign()

    l_type = parseTerm()
    F = True
    while F and numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()
        if tok == 'add_op':
            op_line, op_lex = numLine, lex
            numRow += 1
            print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))
            r_type = parseTerm()

            # Правило 15: Перевірка типів для додавання/віднімання
            l_type = st.check_arithm_op(l_type, op_lex, r_type, op_line)
        else:
            F = False

    indent = predIndt()
    return l_type


def parseTerm():
    global numRow
    indent = nextIndt()
    print(indent + 'parseTerm():')
    l_type = parsePower()
    F = True
    while F and numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()
        if tok == 'mult_op':
            op_line, op_lex = numLine, lex
            numRow += 1
            print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))

            # Правило 10: Ділення на нуль (проста перевірка на літерал)
            r_numLine, r_lex, r_tok = getSymb()
            if op_lex == '/' and r_tok in ('intnum', 'floatnum') and float(r_lex) == 0.0 :
                st.failSem("Division by zero (literal)", op_line)
            r_type = parsePower()

            # Перевірка типів для множення/ділення
            l_type = st.check_arithm_op(l_type, op_lex, r_type, op_line)
        else:
            F = False
    indent = predIndt()
    return l_type


def parsePower():
    global numRow
    indent = nextIndt()
    print(indent + 'parsePower():')
    l_type = parseFactor()
    F = True
    while F and numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()
        if tok == 'pow_op':
            numRow += 1
            print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))
            r_type = parseFactor()

            # Перевірка типів для степеня
            l_type = st.check_arithm_op(l_type, lex, r_type, numLine)
        else:
            F = False
    indent = predIndt()
    return l_type


def parseFactor():
    global numRow
    indent = nextIndt()
    print(indent + 'parseFactor():')
    numLine, lex, tok = getSymb()

    factor_type = 'type_error'  # Початкове значення

    if tok in ('intnum', 'floatnum'):
        print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))
        numRow += 1
        factor_type = 'int' if tok == 'intnum' else 'float'
    elif tok == 'id':
        # Заглядаємо наперед, щоб відрізнити змінну від виклику функції
        if numRow + 1 <= len_tableOfSymb and tableOfSymb[numRow + 1][1] == '(':
            factor_type = parseFunctionCall()
        else:  # Це просто змінна (r-value)
            # Правило 3: Перевірка r-value
            cxt_found, name, attr = st.findName(lex, st.currentContext, numLine)
            id_type = attr[2]
            id_val_status = attr[3]

            # Правило 4: Використання неініціалізованої змінної
            # if id_val_status == 'undefined':
            #     st.failSem(f"Використання неініціалізованої змінної '{lex}'", numLine)

            print(indent + 'в рядку {0} - токен {1}'.format(numLine, (lex, tok)))
            numRow += 1
            factor_type = id_type

    elif lex == '(':
        parseToken('(', 'brackets_op')
        factor_type = parseExpression()  # Тип того, що в дужках
        parseToken(')', 'brackets_op')
    else:
        failParse('token mismatch', (numLine, lex, tok, 'ident | number | function_call | (arithmexpr)'))

    indent = predIndt()
    return factor_type  # Повертаємо тип


def parseFunctionCall():
    global numRow
    indent = nextIndt()
    print(indent + 'parseFunctionCall():')

    # 1. Знаходимо функцію в ST
    numLine, lex, tok = getSymb()
    if tok != 'id':
        failParse('expected function name', getSymb())

    cxt_found, name, attr = st.findName(lex, st.currentContext, numLine)
    func_kind = attr[1]
    func_return_type = attr[2]
    func_params_count = attr[4]  # Це 'nParam', тобто кількість

    if func_kind != 'func':
        st.failSem(f"'{lex}‘ is not a function, it is ’{func_kind}'", numLine)

    numRow += 1
    parseToken('(', 'brackets_op')


    # 2. Отримуємо очікувані типи з області видимості функції
    expected_types = []
    if func_params_count > 0:
        try:
            func_scope = st.tabName[name]

            # Створюємо список [None, None, ...] розміром nParam
            param_list = [None] * func_params_count

            for param_name, param_attr in func_scope.items():
                if param_name == 'declIn': continue

                param_idx = param_attr[0]  # Індекс параметра (0, 1, ...)
                param_kind = param_attr[1]

                # Перевіряємо, що це параметр (визначений в `parseFunctionDeclaration`)
                if param_kind == 'var' and 0 <= param_idx < func_params_count:
                    param_list[param_idx] = param_attr[2]  # Зберігаємо тип, напр. 'int'

            # Перевіряємо, чи всі параметри знайдені (на випадок помилки)
            if None in param_list:
                st.failSem(f"Error reading parameters for function '{name}'", numLine)

            expected_types = param_list

        except KeyError:
            # Ця помилка не має виникнути, якщо `findName` спрацював
            st.failSem(f"No scope found for function '{name}'", numLine)

    # 3. Отримуємо реальні типи аргументів з виклику
    actual_types = []
    # Якщо є аргументи (наступний токен не ')')
    if numRow <= len_tableOfSymb and getSymb()[1] != ')':
        actual_types = parseArgumentList()  # Отримуємо список типів

    # 4. Перевіряємо кількість
    if len(actual_types) != len(expected_types):
        st.failSem(f"The function ‘{name}’ expects {len(expected_types)} arguments, but received",
                   numLine)

    # 5. Перевіряємо типи (
    for i, (actual_t, expected_t) in enumerate(zip(actual_types, expected_types)):
        # Використовуємо check_assign, щоб перевірити, чи можна
        # 'actual_t' (тип виразу) присвоїти 'expected_t' (тип параметра)
        # Це дозволяє неявне приведення
        st.check_assign(expected_t, actual_t, numLine)


    parseToken(')', 'brackets_op')
    indent = predIndt()

    # 6. Повертаємо тип, який повертає функція
    return func_return_type


def parseReturnStatement():
    global numRow
    indent = nextIndt()
    print(indent + 'parseReturnStatement():')

    ret_line, _, _ = getSymb()
    parseToken('return', 'keyword')

    if not st.functionContextStack:
        st.failSem("'return' cannot be outside the function body", ret_line)

    st.functionContextStack[-1]['has_return'] = True
    expected_type = st.functionContextStack[-1]['return_type']

    # Перевіряємо, чи є вираз після return
    next_lex = getSymb()[1]
    has_expression = next_lex != '}'

    if has_expression:
        expr_type = parseExpression()
        # Правило 8:
        if expected_type == 'void':
            st.failSem(f"A function with type ‘void’ must not return a value.", ret_line)

        # Перевірка типу, що повертається
        st.check_return_type(expected_type, expr_type, ret_line)

    else:
        # Правило 9 (модифіковане):
        if expected_type != 'void':
            st.failSem(
                f"The function must return a value of type '{expected_type}', but ‘return’ is used without an expression",
                ret_line)

    indent = predIndt()


def parseArgumentList():
    global numRow
    indent = nextIndt()
    print(indent + 'parseArgumentList():')

    actual_types = []  # Список для типів

    # Перший аргумент
    arg_type = parseExpression()
    actual_types.append(arg_type)  # Додаємо тип

    # Цикл для наступних аргументів через кому
    while numRow <= len_tableOfSymb and getSymb()[1] == ',':
        parseToken(',', 'punct')
        arg_type = parseExpression()
        actual_types.append(arg_type)  # Додаємо тип

    indent = predIndt()
    return actual_types  # Повертаємо список типів


def parseFunctionDeclaration():
    global numRow
    indent = nextIndt()
    print(indent + 'parseFunctionDeclaration():')

    parseToken('func', 'keyword')

    # 1. Ім'я функції
    func_line, func_name, func_tok = getSymb()
    if func_tok != 'id':
        failParse('expected function name', getSymb())
    numRow += 1

    # 2. Створюємо нову область видимості
    parentContext = st.currentContext
    st.currentContext = func_name
    st.tabName[st.currentContext] = {'declIn': parentContext}

    print(f"DEBUG: Entering scope {st.currentContext}, parent {parentContext}")

    parseToken('(', 'brackets_op')

    # 3. Список параметрів
    num_params = 0
    while numRow <= len_tableOfSymb and getSymb()[1] != ')':
        param_type = parseType()

        p_line, p_lex, p_tok = getSymb()
        if p_tok == 'id':
            # Додаємо параметр в ST *нової* області видимості
            attr = (num_params, 'var', param_type, 'assigned', '-')  # Параметри завжди ініціалізовані
            st.insertName(st.currentContext, p_lex, p_line, attr)
            num_params += 1
            numRow += 1
        else:
            failParse('expected parameter identifier', getSymb())

        if getSymb()[1] == ',':
            parseToken(',', 'punct')

    parseToken(')', 'brackets_op')

    # 4. Тип, що повертається
    return_type = 'void'  # За замовчуванням
    if getSymb()[1] == '=>':
        parseToken('=>', 'keyword')
        return_type = parseType()

    # 5. Додаємо функцію в ST *батьківської* області
    func_attr = (len(st.tabName[parentContext]) - 1, 'func', return_type, 'assigned', num_params)
    st.insertName(parentContext, func_name, func_line, func_attr)

    # 6. Додаємо в стек для перевірки 'return'
    st.functionContextStack.append({'name': func_name, 'return_type': return_type,'has_return': False })

    # 7. Розбираємо тіло функції
    parseToken('{', 'brackets_op')

    # Цикл, поки не дійдемо до '}'
    while numRow <= len_tableOfSymb and getSymb()[1] != '}':

        # Перевіряємо, що перед нами - оголошення чи інструкція
        numLine, lex, tok = getSymb()

        if lex == 'var' or lex == 'let':
            # Якщо це 'var' або 'let', викликаємо parseDeclaration()
            parseDeclaration()
        else:
            # В іншому випадку - це звичайна інструкція
            parseStatement()

    parseToken('}', 'brackets_op')
    func_context = st.functionContextStack[-1]
    if return_type != 'void' and not func_context['has_return']:
        st.failSem(f"The function ‘{func_name}’ has type ‘{return_type}’, but does not contain ‘return’", func_line)

    # 8. Виходимо з області видимості
    st.currentContext = parentContext
    st.functionContextStack.pop()
    print(f"DEBUG: Exiting scope, back to {st.currentContext}")

    indent = predIndt()


def parseSign():
    global numRow
    indent = nextIndt()
    print(indent + 'parseSign():')
    numLine, lex, tok = getSymb()

    if (lex, tok) in (('+', 'add_op'), ('-', 'add_op')):
        parseToken(lex, 'add_op')
    else:
        failParse('token mismatch', (numLine, lex, tok, '+ | -'))

    indent = predIndt()


def parseAssign(id_info):
    global numRow
    indent = nextIndt()
    print(indent + 'parseAssign():')

    id_line, id_lex, id_tok = id_info

    # 1. Перевіряємо l-value (правило 3)
    cxt_found, name, attr = st.findName(id_lex, st.currentContext, id_line)
    id_kind = attr[1]
    id_type = attr[2]

    # 2. Перевіряємо на присвоєння константі (правило 6)
    if id_kind == 'let':
        st.failSem(f"Impossible to change the value of a constant (let) '{id_lex}'", id_line)

    # 3. Отримуємо оператор присвоєння
    assign_line, assign_lex, assign_tok = getSymb()
    if assign_tok not in ('assign_op', 'add_ass_op', 'mult_ass_op'):
        failParse('token mismatch', (assign_line, assign_lex, assign_tok, 'assignment operator (=, +=, *=, etc)'))

    parseToken(assign_lex, assign_tok)

    # 4. Перевіряємо, чи це input()
    numLine, lex, tok = getSymb()
    if (lex, tok) == ('input', 'keyword') and assign_tok == 'assign_op':
        # Особливий випадок для input()
        parseInput()
        if id_type not in ('int', 'float', 'string'):
            st.failSem(f"input() can only be assigned to ‘int’, ‘float’, or ‘string’, but not to'{id_type}'",
                       assign_line)
        print(f"Semantic: Semantically accepting input() into var of type '{id_type}'")

    else:
        # 5. Або це звичайний вираз
        expr_type = parseExpression()

        if assign_tok == 'assign_op':
            # Просте присвоєння (a = b)
            # (Правила 16, 17)
            st.check_assign(id_type, expr_type, assign_line)

        elif assign_tok in ('add_ass_op', 'mult_ass_op'):
            # Складне присвоєння (a += b)

            op_map = {
                '+=': '+',
                '-=': '-',
                '*=': '*',
                '/=': '/'
            }
            # Отримуємо '+', '-', '*' або '/' з лексеми '+='
            arith_op = op_map.get(assign_lex)

            if arith_op is None:
                st.failSem(f"Unaccounted operator  '{assign_lex}'", assign_line)
                return  # Виходимо, щоб уникнути подальших помилок

            if assign_lex == '/=' and tok in ('intnum', 'floatnum') and float(lex) == 0.0:
                st.failSem("Division by zero in the /= operator", assign_line)

            # Перевіряємо, чи сама операція (a + b) валідна
            # (Правила 11, 12, 15)
            # 'string' * 'string' тут видасть помилку
            result_type = st.check_arithm_op(id_type, arith_op, expr_type, assign_line)

            # Перевіряємо, чи можна результат присвоїти назад до 'a'
            # (Правила 16, 17)
            # Наприклад, a(int) += b(float) дасть result_type 'float'
            # і check_assign('int', 'float') видасть помилку.
            st.check_assign(id_type, result_type, assign_line)

        else:
            st.failSem(f"Unknown assignment operator type '{assign_tok}'", assign_line)

    # 7. Позначаємо змінну як ініціалізовану
    st.updateNameVal(id_lex, st.currentContext, id_line, 'assigned')

    indent = predIndt()


def parseInput():
    global numRow
    indent = nextIndt()
    print(indent + 'parseInput():')

    # не перевіряємо на наявність Ident, бо це вже виконалось у parseAssign

    parseToken('input', 'keyword')
    parseToken('(', 'brackets_op')
    parseToken(')', 'brackets_op')

    indent = predIndt()
    return 'string'  # Введення з клавіатури - це завжди рядок


def parseToken(lexeme, token):
    global numRow
    indent = nextIndt()

    if numRow > len_tableOfSymb:
        failParse('unexpected end of the program', (lexeme, token, numRow))

    numLine, lex, tok = getSymb()

    if (lex, tok) == (lexeme, token):
        print(indent + 'parseToken: In line {0}, token {1}'.format(numLine, (lexeme, token)))
        numRow += 1
        predIndt()
        return True
    else:
        failParse('token mismatch', (numLine, lex, tok, lexeme, token))
        return False


def getSymb():
    if numRow > len_tableOfSymb:
        failParse('getSymb(): unexpected end of the program', numRow)
    numLine, lexeme, token, _ = tableOfSymb[numRow]
    return numLine, lexeme, token


def failParse(str_msg, details):
    if str_msg == 'unexpected end of the program':
        (lexeme, token, row) = details
        print(
            f'Parser ERROR: \n\t Unexpected end of the program. Expected ({lexeme}, {token}) but the character table ended at row {row - 1}.')
        exit(1001)
    elif str_msg == 'getSymb(): unexpected end of the program':
        row = details
        print(
            f'Parser ERROR: \n\t Attempt to read row {row} from the character table, but it only contains {len_tableOfSymb} entries.')
        exit(1002)
    elif str_msg == 'token mismatch':
        if len(details) == 5:
            (numLine, lexeme, token, expected_lex, expected_tok) = details
            print(
                f'Parser ERROR: \n\t Unexpected element ({lexeme},{token}) in line {numLine}. \n\t Expected - ({expected_lex},{expected_tok}).')
        else:
            (numLine, lexeme, token, expected) = details
            print(
                f'Parser ERROR: \n\t Unexpected element ({lexeme},{token}) in line {numLine}. \n\t Expected - {expected}.')
        exit(1)
    elif str_msg == 'incompatibility of instructions':
        (numLine, lex, tok, expected) = details
        print(f'Parser ERROR: \n\t  Unexpected element ({lex},{tok}) in line {numLine}. \n\t Expected - {expected}.')
        exit(2)
    else:
        print(f"Parser ERROR: {str_msg} - {details}")
        exit(999)


stepIndt = 2
indt = -2


def nextIndt():
    global indt
    indt += stepIndt
    return ' ' * indt


def predIndt():
    global indt
    indt -= stepIndt
    return ' ' * indt


# запуск парсера
if FSuccess == ('Lexer', True):
    parseProgram()
    print("\nParser: Parsing completed successfully")
    print("\nFinal Symbol Table:")
    import json

    print(json.dumps(st.tabName, indent=2, ensure_ascii=False))
    print("\nSemantic: Semantic analysis completed successfully")