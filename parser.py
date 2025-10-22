from textwrap import indent

from lexer import lex
from lexer import tableOfSymb

FSuccess = lex()

print('-' * 50)
print('tableOfSymb:{0}'.format(tableOfSymb))
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
        elif lex in ('if', 'for', 'while', 'repeat', 'switch', 'guard', 'input', 'print', 'func') or tok == 'id':
            parseStatement()
        elif tok == 'comment':  # коментарі
            numRow += 1
        else:
            # жодна з інструкцій не відповідає
            # поточній лексемі у таблиці розбору,
            failParse('incompatibility of instructions',
                      (numLine, lex, tok, ' Declaration | Statement | Comment expected '))
    print("Parser: Syntax analysis completed successfully")


def parseStatement():
    indent = nextIndt()
    print(indent + 'parseStatement():')
    global numRow

    numLine, lex, tok = getSymb()

    if tok == 'id':
        print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))
        numRow += 1
        parseAssign()
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
        failParse('inconsistency of instructions', (numLine, lex, tok, 'statement expected'))

    indent = predIndt()

#WhileStatement = “while” “(“ Condition “)” “{“ StatementList “}
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
    global  numRow
    indent =nextIndt()
    print(indent + 'parseRepeatWhile():')
    parseToken('repeat', 'keyword')
    parseToken('{', 'brackets_op')

    while numRow <= len_tableOfSymb and getSymb()[1] != '}':
        parseStatement()
    parseToken('}', 'brackets_op')
    parseToken('while', 'keyword')
    parseBooleanCondition()

    indent = predIndt()

#Out = print ‘(‘ Ident | String ‘)’
def parsePrint():
    global numRow
    indent = nextIndt()
    print(indent + 'parsePrint():')

    parseToken('print', 'keyword')

    parseToken('(', 'brackets_op')

    numLine, lex, tok = getSymb()

    if tok == 'id':
        print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))
        numRow += 1
    elif  tok == 'str':
        numRow += 1
    else:
        failParse('incompatibility of instructions', (numLine, lex, tok, 'either id or string were expected'))


    parseToken(')', 'brackets_op')


    indent = predIndt()


#InputStatement = Ident “=” “input” “(“ “)”
def parseInput():
    global numRow
    indent = nextIndt()
    print(indent + 'parseInput():')

    #не перевіряємо на наявність Ident, бо це вже виконалось у parseAssign

    parseToken('input', 'keyword')
    parseToken('(', 'brackets_op')
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
    while numRow <= len_tableOfSymb and getSymb()[1] != '}':

        numLine, lex, tok = getSymb()

        if lex == 'case':
            parseCaseBlock()
        elif lex == 'default':
            parseDefaultBlock()
        elif lex == '}':
            break
        elif numRow == len_tableOfSymb:
            failParse('token mismatch', (numLine, lex, tok, 'closing brace "}" expected'))
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
        print(indent + f'in line {numLine} - token {lex, tok}')
        numRow += 1
        parseAssign()
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
        print(indent + f'in line {numLine} - token {lex, tok}')
        numRow += 1
        parseAssign()
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
    if (lex, tok) == ('var', 'keyword'):
        parseVarDeclaration()
    elif (lex, tok) == ('let', 'keyword'):
        parseLetDeclaration()
    else:
        failParse('token mismatch', (numLine, lex, tok, 'var | let'))

    indent = predIndt()


def parseVarDeclaration():
    global numRow
    indent = nextIndt()
    print(indent + 'parseVarDeclaration():')

    parseToken('var', 'keyword')
    parseIdentList()
    parseToken(':', 'punct')
    parseType()

    if numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()
        if tok in ('assign_op', 'add_ass_op', 'mult_ass_op'):
            parseAssign()

    indent = predIndt()


def parseLetDeclaration():
    global numRow
    indent = nextIndt()
    print(indent + 'parseLetDeclaration():')

    parseToken('let', 'keyword')
    parseIdentList()
    parseToken(':', 'punct')
    parseType()

    if numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()
        if tok in ('assign_op', 'add_ass_op', 'mult_ass_op'):
            parseAssign()

    indent = predIndt()


def parseBooleanCondition():
    global numRow
    indent = nextIndt()
    print(indent + 'parseBooleanCondition():')

    numLine, lex, tok = getSymb()

    # (true, false, !)
    if tok == 'boolval' or lex == '!':
        parseBoolExpression()

    # (a > 0)
    elif lex == '(':
        # Якщо починається з дужки, використовуємо parseExpression,
        # яка обробить і ( і ) і внутрішній вираз (включно з порівнянням)
        parseToken('(', 'brackets_op')
        parseExpression()
        parseToken(')', 'brackets_op')

    # (a > 0) без зовнішніх дужок
    else:
        # Розбираємо ліву частину (арифметичний вираз, наприклад, 'a' або 'a + 5')
        parseArithmExpression()

        # Тепер ми очікуємо оператор порівняння
        numLine, lex, tok = getSymb()
        if tok == 'rel_op':
            numRow += 1
            print(indent + f'  in line {numLine} - comparison token {(lex, tok)}')
            # Розбираємо праву частину
            parseArithmExpression()
        else:
            # Якщо після ArithmExpression немає rel_op, то це помилка
            failParse('token mismatch', (numLine, lex, tok,
                                         'Relational operator (>, <, ==, etc.) expected after arithmetic term in condition'))

    indent = predIndt()


def parseExpression():
    global numRow
    indent = nextIndt()
    print(indent + 'parseExpression():')
    numLine, lex, tok = getSymb()

    if tok == 'boolval' or lex == '!':
        parseBoolExpression()
        indent = predIndt()
        return
    elif tok == 'str':
        numRow += 1
        indent = predIndt()
        return

    parseArithmExpression()

    if numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()
        if tok == 'rel_op':
            numRow += 1
            print(indent + f'  in line {numLine} - comparison token {(lex, tok)}')
            parseArithmExpression()

    indent = predIndt()


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
        parseExpression()
        parseToken(')', 'brackets_op')
    else:
        failParse('token mismatch', (numLine, lex, tok, 'true | false | ! | (Expression)'))

    indent = predIndt()


# ArithmExpression = [Sign] Term { ("+" | "-") Term }
def parseArithmExpression():
    global numRow
    indent = nextIndt()
    print(indent + 'parseArithmExpression():')

    numLine, lex, tok = getSymb()
    if (lex, tok) in (('+', 'add_op'), ('-', 'add_op')):
        parseSign()

    parseTerm()
    F = True
    while F and numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()
        if tok == 'add_op':
            numRow += 1
            print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))
            parseTerm()
        else:
            F = False

    indent = predIndt()


def parseTerm():
    global numRow
    indent = nextIndt()
    print(indent + 'parseTerm():')
    parsePower()
    F = True
    while F and numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()
        if tok == 'mult_op':
            numRow += 1
            print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))
            parsePower()
        else:
            F = False
    indent = predIndt()


def parsePower():
    global numRow
    indent = nextIndt()
    print(indent + 'parsePower():')
    parseFactor()
    F = True
    while F and numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()
        if tok == 'pow_op':
            numRow += 1
            print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))
            parseFactor()
        else:
            F = False
    indent = predIndt()


def parseFactor():
    global numRow
    indent = nextIndt()
    print(indent + 'parseFactor():')
    numLine, lex, tok = getSymb()

    if tok in ('intnum', 'floatnum'):
        print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))
        numRow += 1
    elif tok == 'id':
        # Заглядаємо наперед, щоб відрізнити змінну від виклику функції
        if numRow + 1 <= len_tableOfSymb and tableOfSymb[numRow + 1][1] == '(':
            parseFunctionCall()
        else:  # Це просто змінна
            print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))
            numRow += 1
    elif lex == '(':
        parseToken('(', 'brackets_op')
        parseExpression()
        parseToken(')', 'brackets_op')
    else:
        failParse('token mismatch', (numLine, lex, tok, 'ident | number | function_call | (arithmexpr)'))
    indent = predIndt()



def parseFunctionCall():
    global numRow
    indent = nextIndt()
    print(indent + 'parseFunctionCall():')

    numLine, lex, tok = getSymb()
    if tok == 'id':
        print(indent + '  function name: ' + lex)
        numRow += 1

    parseToken('(', 'brackets_op')

    # Перевіряємо, чи є аргументи
    if numRow <= len_tableOfSymb and getSymb()[1] != ')':
        parseArgumentList()

    parseToken(')', 'brackets_op')
    indent = predIndt()


def parseReturnStatement():
    global numRow
    indent = nextIndt()
    print(indent + 'parseReturnStatement():')
    parseToken('return', 'keyword')
    # Після return може йти вираз, який функція повертає
    parseExpression()
    indent = predIndt()

def parseArgumentList():
    global numRow
    indent = nextIndt()
    print(indent + 'parseArgumentList():')

    parseExpression()  # Перший аргумент

    # Цикл для наступних аргументів через кому
    while numRow <= len_tableOfSymb and getSymb()[1] == ',':
        parseToken(',', 'punct')
        parseExpression()

    indent = predIndt()



def parseFunctionDeclaration():
    global numRow
    indent = nextIndt()
    print(indent + 'parseFunctionDeclaration():')

    parseToken('func', 'keyword')

    # Ім'я функції
    if getSymb()[2] == 'id':
        numRow += 1
    else:
        failParse('function name expected', getSymb())

    parseToken('(', 'brackets_op')

    while numRow <= len_tableOfSymb and getSymb()[1] != ')':
        parseType()
        if getSymb()[2] == 'id':
            numRow += 1
        else:
            failParse('parameter name expected', getSymb())

        if getSymb()[1] == ',':
            parseToken(',', 'punct')
        elif getSymb()[1] != ')':
            failParse("',' or ')' expected after parameter", getSymb())

    parseToken(')', 'brackets_op')

    # Тип, що повертається
    if getSymb()[1] == '=>':
        parseToken('=>', 'keyword')
        parseType()

    parseToken('{', 'brackets_op')
    while numRow <= len_tableOfSymb and getSymb()[1] != '}':
        # Всередині функції можуть бути оголошення або інструкції
        if getSymb()[1] in ('var', 'let'):
            parseDeclaration()
        else:
            parseStatement()
    parseToken('}', 'brackets_op')

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


def parseIdentList():
    global numRow
    indent = nextIndt()
    print(indent + 'parseIdentList():')

    numLine, lex, tok = getSymb()
    if tok != 'id':
        failParse('token mismatch', (numLine, lex, tok, 'identifier was expected'))

    print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))
    numRow += 1

    while numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()
        if (lex, tok) == (',', 'punct'):
            numRow += 1  # Пропускаємо кому

            numLine, lex, tok = getSymb()  # Дивимось на токен після коми
            if tok != 'id':
                failParse('token mismatch', (numLine, lex, tok, 'identifier was expected after comma'))

            print(indent + 'in line {0} - token {1}'.format(numLine, (lex, tok)))
            numRow += 1
        else:
            break

    indent = predIndt()


def parseType():
    global numRow
    indent = nextIndt()
    print(indent + 'parseType():')

    numLine, lex, tok = getSymb()

    if lex in ('int', 'float', 'string', 'bool') and tok == 'keyword':
        parseToken(lex, 'keyword')
    else:
        failParse('token mismatch', (numLine, lex, tok, 'int | float | string | bool'))

    indent = predIndt()


def parseAssign():
    global numRow
    indent = nextIndt()
    print(indent + 'parseAssign():')

    assign_line, assign_lex, assign_tok = getSymb()
    parseToken(assign_lex, assign_tok)

    # Заглядаємо наперед на наступний токен
    numLine, lex, tok = getSymb()

    if (lex, tok) == ('input', 'keyword') and assign_tok == 'assign_op':
        parseInput()
    else:
        #звичайне присвоєння з виразом
        parseExpression()

    indent = predIndt()


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
                f'Unexpected element ({lexeme},{token}) in line {numLine}. \n\t Expected - {expected}.')
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

