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


main_labelTable = {}
main_rpn_table = []
base_file_name = ""

current_labelTable = None
current_rpn_table = None

toView = True

toView = True
supported_tokens = (
        "int", "float", "bool", "string", "l-val", "r-val",
        "label", "colon", "assign_op", "math_op", "rel_op",
        "pow_op", "out_op", "inp_op", "conv", "bool_op",
        "cat_op", "stack_op", "colon", "jf", "jump", "CALL", "RET"
)

type_map = {
    "intnum": "int",
    "floatnum": "float",
    "boolval": "bool",
    "str": "string",
    "assign_op": "assign_op",
    "add_ass_op": "assign_op",
    "mult_ass_op": "assign_op",
    "add_op": "math_op",
    "mult_op": "math_op",
    "rel_op": "rel_op",
    "logic_op": "bool_op",
    "pow_op": "pow_op"
}

# Program = { Declaration | Statement | Comment } - кореневий нетермінал
def parseProgram():
    global numRow
    print("Parser: ")
    while numRow <= len_tableOfSymb:
        # прочитаємо поточну лексему в таблиці розбору
        numLine, lex, tok = getSymb()
        if tok == 'EOF':
            return True
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

    return True


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

    # початок перевірки умови
    m_cond = createLabel()
    # кінець (вихід) з циклу
    m_end = createLabel()

    # повертатимемося сюди після кожної ітерації
    setValLabel(m_cond)
    current_rpn_table.append(m_cond)
    current_rpn_table.append((':', 'colon'))

    parseToken('while', 'keyword')
    parseToken('(', 'brackets_op')

    parseBooleanCondition()

    parseToken(')', 'brackets_op')

    # Якщо умова 'false', стрибаємо на кінець циклу
    current_rpn_table.append(m_end)
    current_rpn_table.append(('JF', 'jf'))

    parseToken('{', 'brackets_op')

    while numRow <= len_tableOfSymb and getSymb()[1] != '}':
        parseStatement()

    parseToken('}', 'brackets_op')

    # Після виконання тіла, стрибаємо назад на перевірку умови
    current_rpn_table.append(m_cond)
    current_rpn_table.append(('JMP', 'jump'))

    # Встановлюємо кінцеву мітку
    setValLabel(m_end)
    current_rpn_table.append(m_end)
    current_rpn_table.append((':', 'colon'))

    indent = predIndt()




# CycleRep = ‘repeat’ ‘{’  Body ‘while’  BoolExpression ‘}’
def parseRepeatWhile():
    global numRow
    indent = nextIndt()
    print(indent + 'parseRepeatWhile():')

    # Початок тіла циклу (куди повертаємось)
    m_start_body = createLabel()
    # Кінець циклу (куди виходимо)
    m_end = createLabel()

    # Встановлюємо мітку початку тіла
    setValLabel(m_start_body)
    current_rpn_table.append(m_start_body)
    current_rpn_table.append((':', 'colon'))

    parseToken('repeat', 'keyword')
    parseToken('{', 'brackets_op')

    while numRow <= len_tableOfSymb and getSymb()[1] != '}':
        parseStatement()
    parseToken('}', 'brackets_op')

    parseToken('while', 'keyword')

    parseBooleanCondition()

    # Ми хочемо стрибнути на m_start_body, яукщо 'true'
    # Якщо умова 'false', стрибаємо на кінець
    current_rpn_table.append(m_end)
    current_rpn_table.append(('JF', 'jf'))

    # (Якщо ми тут, умова була 'true')
    # Стрибаємо назад на початок тіла
    current_rpn_table.append(m_start_body)
    current_rpn_table.append(('JMP', 'jump'))

    # встановлюємо кінцеву мітку
    setValLabel(m_end)
    current_rpn_table.append(m_end)
    current_rpn_table.append((':', 'colon'))

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
        parseExpression()

    elif tok == 'str':
        postfixCodeGen('str', (lex, tok))
        if toView: configToPrint(lex, numRow)

        numRow += 1
    else:
        # Дозволимо друкувати будь-який вираз
        parseExpression()

    postfixCodeGen('OUT', ('OUT', 'out_op'))
    if toView: configToPrint('OUT', numRow)  # Для дебагу
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

    m_end_switch = createLabel()

    parseToken('switch', 'keyword')

    numLine, lex, tok = getSymb()
    if tok != 'id':
        failParse('switch was expected after identifier', (numLine, lex, tok))

    ident_info = (numLine, lex, tok)
    numRow += 1

    parseToken('{', 'brackets_op')

    while numRow <= len_tableOfSymb:
        numLine_loop, lex_loop, tok_loop = getSymb()

        if lex_loop == 'case':
            parseCaseBlock(ident_info, m_end_switch)

        elif lex_loop == 'default':
            parseDefaultBlock()

        elif lex_loop == '}':
            break  # Кінець 'switch'
        else:
            failParse('case, default or "}" was expected', (numLine_loop, lex_loop, tok_loop))

    setValLabel(m_end_switch)
    current_rpn_table.append(m_end_switch)
    current_rpn_table.append((':', 'colon'))

    parseToken('}', 'brackets_op')
    indent = predIndt()


def parseCaseBlock(ident_info, m_end_switch):
    global numRow
    indent = nextIndt()
    print(indent + 'parseCaseBlock():')

    m_next_case = createLabel()

    parseToken('case', 'keyword')

    postfixCodeGen('rval', (ident_info[1], 'r-val'))

    is_negative = False
    numLine_const, lex_const, tok_const = getSymb()

    if (lex_const, tok_const) == ('-', 'add_op'):
        is_negative = True
        parseToken('-', 'add_op')
        numLine_const, lex_const, tok_const = getSymb()

    if tok_const == 'intnum':
        print(indent + f' case number: {"-" if is_negative else ""}{lex_const}')
        postfixCodeGen('rval', (lex_const, tok_const))
        numRow += 1
    else:
        failParse('An integer number was expected after case', (numLine_const, lex_const, tok_const))

    if is_negative:
        postfixCodeGen('NEG', ('NEG', 'math_op'))

    postfixCodeGen('typemap', (lex_const, tok_const))

    # Додаємо m_next_case JF (перейти до наступного 'case', якщо НЕ дорівнює)
    current_rpn_table.append(m_next_case)
    current_rpn_table.append(('JF', 'jf'))

    parseToken(':', 'punct')

    while numRow <= len_tableOfSymb:
        nextLex = getSymb()[1]
        if nextLex in ('case', 'default', '}'):
            break
        parseStatement()

    current_rpn_table.append(m_end_switch)
    current_rpn_table.append(('JMP', 'jump'))


    setValLabel(m_next_case)
    current_rpn_table.append(m_next_case)
    current_rpn_table.append((':', 'colon'))

    indent = predIndt()



#по аналогії елс
def parseDefaultBlock():
    global numRow
    indent = nextIndt()
    print(indent + 'parseDefaultBlock():')

    parseToken('default', 'keyword')
    parseToken(':', 'punct')

    while numRow <= len_tableOfSymb:
        nextLex = getSymb()[1]
        if nextLex == '}':
            break
        parseStatement()

    indent = predIndt()


def parseGuard():
    global numRow
    indent = nextIndt()
    print(indent + 'parseGuard():')
    # Створюємо дві мітки
    # m_else: куди ми стрибаємо, якщо умова 'false'
    m_else = createLabel()
    # m_end: куди ми стрибаємо, якщо умова 'true' (пропускаючи 'else')
    m_end = createLabel()

    # guard keyword
    parseToken('guard', 'keyword')

    # (
    parseToken('(', 'brackets_op')
    parseBooleanCondition()
    # )
    parseToken(')', 'brackets_op')

    # Якщо умова 'false', стрибаємо на 'm_else:' (де починається блок else)
    current_rpn_table.append(m_else)
    current_rpn_table.append(('JF', 'jf'))

    # Якщо умова була 'true', ми доходимо сюди.
    # Безумовно стрибаємо в кінець (пропускаємо блок 'else')
    current_rpn_table.append(m_end)
    current_rpn_table.append(('JMP', 'jump'))

    # else
    parseToken('else', 'keyword')

    # Це початок блоку else, куди ми стрибали, якщо умова 'false'
    setValLabel(m_else)
    current_rpn_table.append(m_else)
    current_rpn_table.append((':', 'colon'))

    # { StatementList }
    parseToken('{', 'brackets_op')

    while numRow <= len_tableOfSymb and getSymb()[1] != '}':
        parseStatement()
    parseToken('}', 'brackets_op')

    # Це кінець всього 'guard', куди ми стрибали, якщо умова 'true'
    setValLabel(m_end)
    current_rpn_table.append(m_end)
    current_rpn_table.append((':', 'colon'))

    indent = predIndt()


def parseFor():
    global numRow
    indent = nextIndt()
    print(indent + 'parseFor():')

    # m_cond:   Початок перевірки умови
    # m_incr:   Початок коду інкременту
    # m_body:   Початок тіла циклу
    # m_end:    Кінець (вихід) з циклу
    m_cond = createLabel()
    m_incr = createLabel()
    m_body = createLabel()
    m_end = createLabel()

    # for keyword
    parseToken('for', 'keyword')

    # (
    parseToken('(', 'brackets_op')

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

    #Встановлюємо мітку умови
    setValLabel(m_cond)
    current_rpn_table.append(m_cond)
    current_rpn_table.append((':', 'colon'))

    parseBooleanCondition()

    # Переходи після умови
    # Якщо умова 'false' стрибаємо на кінець
    current_rpn_table.append(m_end)
    current_rpn_table.append(('JF', 'jf'))
    # Якщо умова 'true' стрибаємо на тіло
    current_rpn_table.append(m_body)
    current_rpn_table.append(('JMP', 'jump'))

    # ;
    parseToken(';', 'punct')

    # Встановлюємо мітку інкременту
    # Ми стрибнемо сюди ПІСЛЯ тіла циклу
    setValLabel(m_incr)
    current_rpn_table.append(m_incr)
    current_rpn_table.append((':', 'colon'))

    numLine, lex, tok = getSymb()
    if tok == 'id':
        id_info = (numLine, lex, tok)
        print(indent + f'in line {numLine} - token {lex, tok}')
        numRow += 1
        parseAssign(id_info)
    else:
        failParse('for increment expected', (numLine, lex, tok, 'identifier'))

    # Стрибаємо назад на умову
    current_rpn_table.append(m_cond)
    current_rpn_table.append(('JMP', 'jump'))

    # )
    parseToken(')', 'brackets_op')

    # Встановлюємо мітку тіла
    setValLabel(m_body)
    current_rpn_table.append(m_body)
    current_rpn_table.append((':', 'colon'))

    parseToken('{', 'brackets_op')
    while numRow <= len_tableOfSymb and getSymb()[1] != '}':
        parseStatement()
    parseToken('}', 'brackets_op')

    # Стрибаємо на інкремент
    # Це відбувається ПІСЛЯ виконання тіла
    current_rpn_table.append(m_incr)
    current_rpn_table.append(('JMP', 'jump'))

    # становлюємо кінцеву мітку
    setValLabel(m_end)
    current_rpn_table.append(m_end)
    current_rpn_table.append((':', 'colon'))

    indent = predIndt()



def parseIf():
    global numRow
    indent = nextIndt()
    print(indent + 'parseIf():')

    # Ця мітка буде встановлена тількти в самому кінці
    m_end_chain = createLabel()
    # Мітка для переходу на наступну умову (else if) або на else
    m_next_cond = createLabel()

    parseToken('if', 'keyword')
    parseToken('(', 'brackets_op')
    parseBooleanCondition()

    current_rpn_table.append(m_next_cond)
    current_rpn_table.append(('JF', 'jf'))

    parseToken(')', 'brackets_op')
    parseToken('{', 'brackets_op')

    while numRow <= len_tableOfSymb and getSymb()[1] != '}':
        parseStatement()
    parseToken('}', 'brackets_op')

    current_rpn_table.append(m_end_chain)
    current_rpn_table.append(('JMP', 'jump'))

    setValLabel(m_next_cond)
    current_rpn_table.append(m_next_cond)
    current_rpn_table.append((':', 'colon'))

    if numRow <= len_tableOfSymb and getSymb()[1] == 'else':
        print(indent + '  founded else')
        parseToken('else', 'keyword')
        # обробка else if через доп функцію
        if numRow <= len_tableOfSymb and getSymb()[1] == 'if':
            parseElseIfBlock(m_end_chain)  

        # Обробка звичайного 'else'
        else:
            parseToken('{', 'brackets_op')
            while numRow <= len_tableOfSymb and getSymb()[1] != '}':
                parseStatement()
            parseToken('}', 'brackets_op')

    setValLabel(m_end_chain)
    current_rpn_table.append(m_end_chain)
    current_rpn_table.append((':', 'colon'))

    indent = predIndt()


# допоміжна функція для обробки ланцюжка else if
def parseElseIfBlock(m_end_chain):
    global numRow
    indent = nextIndt()
    print(indent + 'parseElseIfBlock():')

    # Мітка для переходу на наступну умову (else if) або на else
    m_next_cond = createLabel()

    parseToken('if', 'keyword')
    parseToken('(', 'brackets_op')

    parseBooleanCondition()

    current_rpn_table.append(m_next_cond)
    current_rpn_table.append(('JF', 'jf'))

    parseToken(')', 'brackets_op')
    parseToken('{', 'brackets_op')

    while numRow <= len_tableOfSymb and getSymb()[1] != '}':
        parseStatement()
    parseToken('}', 'brackets_op')

    current_rpn_table.append(m_end_chain)
    current_rpn_table.append(('JMP', 'jump'))

    setValLabel(m_next_cond)
    current_rpn_table.append(m_next_cond)
    current_rpn_table.append((':', 'colon'))

    # Рекурсивна обробка наступного 'else if' / 'else'
    if numRow <= len_tableOfSymb and getSymb()[1] == 'else':
        print(indent + '  founded else')
        parseToken('else', 'keyword')

        if numRow <= len_tableOfSymb and getSymb()[1] == 'if':
            parseElseIfBlock(m_end_chain) 
        else:
            # Це звичайний 'else'
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
        postfixCodeGen('typemap', ('=', 'assign_op'))
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
    for numLine, lex, tok in id_list:
        postfixCodeGen('lval', (lex,tok))
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

def precedence(operator):
    priorities = {
        '**': 10,

        '!': 9,
        'NEG': 9,  # унарний мінус

        '*': 8,
        '/': 8,

        '+': 7,
        '-': 7,

        '<=': 6,
        '>': 6,
        '>=': 6,
        '==': 6,
        '!=': 6,
        '<': 6,

        '&&': 5,
        '||': 4,

        '=': 3,
        # для складного присвоювання потрібна додаткова обробка
        '+=': 3,
        '-=': 3,
        '*=': 3,
        '/=': 3,

        ')': 2,
        '(': 1
    }
    return priorities.get(operator, 0)


def should_pop_operator(top_op, current_op):
    top_precedence = precedence(top_op)
    current_precedence = precedence(current_op)

    if current_op == '**':
        return top_precedence > current_precedence
    return top_precedence >= current_precedence


def parseExpression():
    global numRow
    indent = nextIndt()
    print(indent + 'parseExpression():')
    numLine, lex, tok = getSymb()

    if tok == 'boolval' or lex == '!':
        expr_type = parseBoolExpression()
        postfixCodeGen("typemap", (lex,tok))
        indent = predIndt()
        return expr_type
    elif tok == 'str':
        numRow += 1
        postfixCodeGen("typemap", (lex, tok))
        indent = predIndt()

        return 'string'

    # Інакше це арифметичний вираз...
    operator_stack = []
    operand_stack = []

    expr_type = parseArithmExpression(operator_stack, operand_stack)

    # ...який може бути частиною порівняння
    if numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()
        if tok == 'rel_op':
            op_line, op_lex = numLine, lex
            numRow += 1
            print(indent + f'  in line {numLine} - comparison token {(lex, tok)}')

            r_type = parseArithmExpression(operator_stack, operand_stack)

            # Правила 12, 14: Перевірка типів для операторів порівняння
            st.check_rel_op(expr_type, op_lex, r_type, op_line)
            postfixCodeGen("typemap", (op_lex, tok))
            expr_type = 'bool'
            indent = predIndt()
            return 'bool'  # Правило 13: Результат порівняння - bool

    while operator_stack:
        op = operator_stack.pop()
        postfixCodeGen('typemap', op)

    indent = predIndt()
    return expr_type

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
def parseArithmExpression(operator_stack=None, operand_stack=None):
    global numRow
    indent = nextIndt()
    print(indent + 'parseArithmExpression():')

    if operator_stack is None: operator_stack = []
    if operand_stack is None: operand_stack = []

    # Перевірка на унарний знак
    numLine, lex, tok = getSymb()
    if (lex, tok) in (('+', 'add_op'), ('-', 'add_op')):
        while operator_stack and should_pop_operator(operator_stack[-1][0], lex):
            op = operator_stack.pop()
            postfixCodeGen('', ('NEG', 'math_op'))
        operator_stack.append(('NEG', 'math_op'))
        parseSign()
        # Уточнити штуку


    l_type = parseTerm(operator_stack, operand_stack)

    while True:
        buffer = getSymb()
        if not buffer:
            break
        numLine, lex, tok = buffer
        if tok == 'add_op':
            while operator_stack and should_pop_operator(operator_stack[-1][0], lex):
                op = operator_stack.pop()
                postfixCodeGen('typemap', op)
            operator_stack.append((lex, tok))
            numRow += 1
            r_type = parseTerm(operator_stack, operand_stack)
            l_type = st.check_arithm_op(l_type, lex, r_type, numLine)
        else:
            break

    indent = predIndt()
    return l_type

def parseTerm(operator_stack=None, operand_stack=None):
    global numRow
    indent = nextIndt()
    print(indent + 'parseTerm():')

    if operator_stack is None: operator_stack = []
    if operand_stack is None: operand_stack = []

    l_type = parsePower(operator_stack, operand_stack)

    while True:
        buffer = getSymb()
        if not buffer:
            break
        numLine, lex, tok = buffer
        if tok == 'mult_op':
            while operator_stack and should_pop_operator(operator_stack[-1][0], lex):
                op = operator_stack.pop()
                postfixCodeGen('typemap', op)
            operator_stack.append((lex, tok))
            numRow += 1
            r_type = parsePower(operator_stack, operand_stack)
            l_type = st.check_arithm_op(l_type, lex, r_type, numLine)
        else:
            break

    indent = predIndt()
    return l_type


def parsePower(operator_stack=None, operand_stack=None):
    global numRow
    indent = nextIndt()
    print(indent + 'parsePower():')

    if operator_stack is None: operator_stack = []
    if operand_stack is None: operand_stack = []

    l_type = parseFactor()

    while True:
        buffer = getSymb()
        if not buffer:
            break
        numLine, lex, tok = buffer
        if tok == 'pow_op':
            while operator_stack and should_pop_operator(operator_stack[-1][0], lex):
                op = operator_stack.pop()
                postfixCodeGen('pow_op', op)
            operator_stack.append((lex, tok))
            numRow += 1
            r_type = parseFactor()
            l_type = st.check_arithm_op(l_type, lex, r_type, numLine)
        else:
            break

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
        postfixCodeGen('typemap',(lex,tok))
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
            postfixCodeGen('rval', (lex, tok))
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
    global current_rpn_table

    indent = nextIndt()
    print(indent + 'parseFunctionCall():')

    # 1. Знаходимо функцію в ST
    numLine, func_name, func_tok = getSymb()  # Зберігаємо func_name
    if func_tok != 'id':
        failParse('expected function name', getSymb())

    cxt_found, name, attr = st.findName(func_name, st.currentContext, numLine)
    func_kind = attr[1]
    func_return_type = attr[2]
    func_params_count = attr[4]
    if func_kind != 'func':
        st.failSem(f"'{func_name}‘ is not a function, it is ’{func_kind}'", numLine)

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
                param_idx = param_attr[0]
                param_kind = param_attr[1]

                # Перевіряємо, що це параметр (визначений в `parseFunctionDeclaration`)
                if param_kind == 'var' and 0 <= param_idx < func_params_count:
                    param_list[param_idx] = param_attr[2]
            if None in param_list:
                st.failSem(f"Error reading parameters for function '{name}'", numLine)

            expected_types = param_list

        except KeyError:

            st.failSem(f"No scope found for function '{name}'", numLine)

    # 3. Отримуємо типи аргументів з виклику
    actual_types = []
    # Якщо є аргументи (наступний токен не ')')
    if numRow <= len_tableOfSymb and getSymb()[1] != ')':
        actual_types = parseArgumentList()
    if len(actual_types) != len(expected_types):
        st.failSem(f"The function ‘{name}’ expects {len(expected_types)} arguments, but received {len(actual_types)}",
                   numLine)

    # 5. Перевіряємо типи
    for i, (actual_t, expected_t) in enumerate(zip(actual_types, expected_types)):
        # Використовуємо check_assign, щоб перевірити, чи можна
        # 'actual_t' (тип виразу) присвоїти 'expected_t' (тип параметра)
        # Це дозволяє неявне приведення
        st.check_assign(expected_t, actual_t, numLine)


    parseToken(')', 'brackets_op')
    postfixCodeGen(func_name, (func_name, 'CALL'))
    if toView: configToPrint(func_name, numRow)

    indent = predIndt()

    # 6. Повертаємо тип, який повертає функція
    return func_return_type


def parseReturnStatement():
    global numRow
    global current_rpn_table

    indent = nextIndt()
    print(indent + 'parseReturnStatement():')

    ret_line, _, _ = getSymb()
    parseToken('return', 'keyword')

    if not st.functionContextStack:
        st.failSem("'return' cannot be outside the function body", ret_line)

    st.functionContextStack[-1]['has_return'] = True
    expected_type = st.functionContextStack[-1]['return_type']

    next_lex = getSymb()[1]
    has_expression = next_lex != '}'

    if has_expression:
        expr_type = parseExpression()

        if expected_type == 'void':
            st.failSem(f"A function with type ‘void’ must not return a value.", ret_line)

        st.check_return_type(expected_type, expr_type, ret_line)

    else:
        # Правило 9:
        if expected_type != 'void':
            st.failSem(
                f"The function must return a value of type '{expected_type}', but ‘return’ is used without an expression",
                ret_line)

    postfixCodeGen('RET', ('RET', 'RET'))
    if toView: configToPrint('RET', ret_line)

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
    global current_rpn_table, current_labelTable, base_file_name

    indent = nextIndt()
    print(indent + 'parseFunctionDeclaration():')

    m_skip_end = createLabel()

    parent_rpn_table = current_rpn_table
    parent_labelTable = current_labelTable

    func_rpn_table = []
    func_labelTable = {}

    current_rpn_table = func_rpn_table
    current_labelTable = func_labelTable

    parseToken('func', 'keyword')

    # 1. Ім'я функції
    func_line, func_name, func_tok = getSymb()
    if func_tok != 'id':
        failParse('expected function name', getSymb())
    numRow += 1

    parent_rpn_table.append(m_skip_end)
    parent_rpn_table.append(('JMP', 'jump'))

    parentContext = st.currentContext
    st.currentContext = func_name
    st.tabName[st.currentContext] = {'declIn': parentContext}
    print(f"DEBUG: Entering scope {st.currentContext}, parent {parentContext}")

    num_params = 0
    parseToken('(', 'brackets_op')

    # 3. Список параметрів
    num_params = 0
    while numRow <= len_tableOfSymb and getSymb()[1] != ')':
        param_type = parseType()

        p_line, p_lex, p_tok = getSymb()
        if p_tok == 'id':
            attr = (num_params, 'var', param_type, 'assigned', '-')
            st.insertName(st.currentContext, p_lex, p_line, attr)
            num_params += 1
            numRow += 1
        else:
            failParse('expected parameter identifier', getSymb())

        if getSymb()[1] == ',':
            parseToken(',', 'punct')

    parseToken(')', 'brackets_op')

    return_type = 'void'
    if getSymb()[1] == '=>':
        parseToken('=>', 'keyword')
        return_type = parseType()

    # 5. Додаємо функцію в ST *батьківської* області
    func_attr = (len(st.tabName[parentContext]) - 1, 'func', return_type, 'assigned', num_params)
    st.insertName(parentContext, func_name, func_line, func_attr)
    st.functionContextStack.append({'name': func_name, 'return_type': return_type, 'has_return': False})

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

    # Перевірка на відсутність return (якщо не void)
    if return_type != 'void' and not func_context['has_return']:
        st.failSem(f"The function ‘{func_name}’ has type ‘{return_type}’, but does not contain ‘return’", func_line)

    # Якщо функція void і не має явного return, додаємо RET
    if return_type == 'void' and not func_context['has_return']:
        postfixCodeGen('RET', ('RET', 'RET'))  # Пише у func_rpn_table
        if toView: configToPrint('RET (implicit)', numRow)


    func_file_path = f"{base_file_name}${func_name}"

    # Передаємо ЛОКАЛЬНІ таблиці та ЛОКАЛЬНИЙ скоуп
    generate_postfix_file(func_file_path, st.tabName[func_name], func_rpn_table, func_labelTable)

    st.currentContext = parentContext
    st.functionContextStack.pop()
    print(f"DEBUG: Exiting scope, back to {st.currentContext}")

    current_rpn_table = parent_rpn_table
    current_labelTable = parent_labelTable

    setValLabel(m_skip_end)
    current_rpn_table.append(m_skip_end)
    current_rpn_table.append((':', 'colon'))

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

def postfixCodeGen(case,toTran):
    if case == 'lval':
        lex,tok = toTran
        current_rpn_table.append((lex,'l-val'))
    elif case == 'rval':
        lex,tok = toTran
        current_rpn_table.append((lex,'r-val'))
    elif case in ('typemap', 'pow_op'):
        lex, tok = toTran
        found = False
        if tok == 'pow_op':
            current_rpn_table.append(('^', tok))
        elif case == 'typemap':
            for key, value in type_map.items():
                if tok == key or tok in (value if isinstance(value, list) else [value]):
                    current_rpn_table.append((lex, value))
                    found = True
                    break
            if not found:
                current_rpn_table.append((lex, tok))
    else:
        lex,tok = toTran
        current_rpn_table.append((lex,tok))


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

    postfixCodeGen('lval', (id_lex, id_tok))
    parseToken(assign_lex, assign_tok)


    if toView: configToPrint(id_lex, numRow)

    # 4. Перевіряємо, чи це input()
    numLine, lex, tok = getSymb()
    if (lex, tok) == ('input', 'keyword') and assign_tok == 'assign_op':
        # Особливий випадок для input()
        parseInput()
        if id_type not in ('int', 'float', 'string'):
            st.failSem(f"input() can only be assigned to ‘int’, ‘float’, or ‘string’, but not to'{id_type}'",
                       assign_line)
        print(f"Semantic: Semantically accepting input() into var of type '{id_type}'")
        # postfixCodeGen('', ('input', 'func'))
        # postfixCodeGen('', ('=', 'assign_op'))
    else:
        # 5. Або це звичайний вираз
        expr_type = parseExpression()

        if assign_tok == 'assign_op':
            # Просте присвоєння (a = b)
            # (Правила 16, 17)
            st.check_assign(id_type, expr_type, assign_line)
            current_rpn_table.append(('=', 'assign_op'))
            if toView: configToPrint(lex, numRow)
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
            # postfixCodeGen('lval', (id_lex, id_tok))  # a
            # postfixCodeGen('', (arith_op, 'op'))  # +
            # postfixCodeGen('', ('=', 'assign_op'))  # =
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

    postfixCodeGen('INP', ('INP', 'inp_op'))
    if toView: configToPrint('INP', numRow)
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
       # return None
        failParse('getSymb(): unexpected end of the program', numRow)
    numLine, lexeme, token, _ = tableOfSymb[numRow]
    # if token == 'EOF':
    #     exit(0)
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

def setValLabel(lbl):
    global current_labelTable, current_rpn_table
    lex,_tok = lbl
    current_labelTable[lex] = len(current_rpn_table)
    return True

def createLabel():
    global current_labelTable
    nmb = len(current_labelTable)+1
    lexeme = "m"+str(nmb)
    val = current_labelTable.get(lexeme)
    if val is None:
        current_labelTable[lexeme] = 'val_undef'
        tok = 'label'
    else:
        tok = 'Labels conflict'
        print(tok)
        exit(1003)

    return (lexeme,tok)

def generate_postfix_file(filename, vars_scope, rpn_table_to_save, labelTable_to_save):
    output_path = f"{filename}.postfix"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(".target: Postfix Machine\n")
        f.write(".version: 0.3\n\n")

        f.write(".vars(\n")
        # Ітеруємо лише по конкретному скоупу
        if vars_scope: # Перевіряємо, чи скоуп не порожній
            for var_name, attributes in vars_scope.items():
                if var_name == "declIn":
                    continue
                # attributes[2] це тип int, float, bool, string
                f.write(f"\t{var_name}\t{attributes[2]}\n")
        f.write(")\n\n")

        #для міток. окремо треба штуку зробити для кожної малої функції(як у прикладах psm)
        f.write(".labels(\n")
        if labelTable_to_save:
            for lbl, addr in labelTable_to_save.items():
                f.write(f"\t{lbl}\t{addr}\n")
        f.write(")\n\n")

        f.write(".code(\n")
        if rpn_table_to_save:
            for lexeme, token_type in rpn_table_to_save:
                f.write(f"\t{lexeme:<10}\t{token_type}\n")
        f.write(")\n")

    print(f"Postfix file was generated: {output_path}")


def compileToPostfix(fileName):
    global len_tableOfSymb, FSuccess
    global base_file_name, current_rpn_table, current_labelTable, main_rpn_table, main_labelTable
    base_file_name = fileName.replace('.ll', '')

    current_rpn_table = main_rpn_table
    current_labelTable = main_labelTable


    print('compileToPostfix: lexer Start Up\n')
    FSuccess = lex()
    print('compileToPostfix: lexer-FSuccess ={0}'.format(FSuccess))

    if ('Lexer', True) == FSuccess:
        len_tableOfSymb = len(tableOfSymb)
        print('-' * 55)
        print('compileToPostfix: Start Up compiler = parser + codeGenerator\n')
        FSuccess = False
        FSuccess = parseProgram()

        if FSuccess == (True):

            generate_postfix_file(base_file_name, st.tabName['univ'], main_rpn_table, main_labelTable)

        if not FSuccess:
            print(f"Postfix-код не було збережено у файл {fileName}")
    return FSuccess

def configToPrint(lex,numRow):
    stage = '\nTranslation step\n'
    stage += 'lex: \'{0}\'\n'
    stage += 'rpn_table = {3}\n'
    print(stage.format(lex,numRow,str(tableOfSymb[numRow]),str(main_rpn_table)))


# запуск парсера

compileToPostfix('testIF')
# if FSuccess == ('Lexer', True):
#     parseProgram()
#     print("\nParser: Parsing completed successfully")
#     print("\nFinal Symbol Table:")
#     import json
#
#     print(json.dumps(st.tabName, indent=2, ensure_ascii=False))
#     print("\nSemantic: Semantic analysis completed successfully")