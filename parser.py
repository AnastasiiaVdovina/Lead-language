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
            failParse('невідповідність інструкцій',
                      (numLine, lex, tok, 'очікувалось Declaration | Statement | Comment '))


def parseStatement():
    indent = nextIndt()
    print(indent + 'parseStatement():')
    global numRow

    numLine, lex, tok = getSymb()
    if tok == 'id':
        print(indent + 'в рядку {0} - токен {1}'.format(numLine, (lex, tok)))
        numRow += 1
        parseAssign()
    elif (lex, tok) == ('if', 'keyword'): #Настя
        parseIf()
    elif (lex, tok) == ('for', 'keyword'): #Влад
        parseFor()
    elif (lex, tok) == ('while', 'keyword'): #Настя
        parseWhile()
    elif (lex, tok) == ('repeat', 'keyword'): #Таня
        parseRepeatWhile()
    elif (lex, tok) == ('switch', 'keyword'): #Таня
        parseSwitch()
    elif (lex, tok) == ('guard', 'keyword'): #Влад
        parseGuard()
    elif (lex, tok) == ('print', 'keyword'):
        parsePrint()
    elif (lex, tok) == ('input', 'keyword'):
        parseInput()

    else:
        failParse('невідповідність інструкцій', (numLine, lex, tok, 'очікувався statement'))

    indent = predIndt()

#WhileStatement = “while” “(“ Condition “)” “{“ StatementList “}
# ПРАВИЛЬНА версія
def parseWhile():
    global numRow
    indent = nextIndt()
    print(indent + 'parseWhile():')

    parseToken('while', 'keyword')
    parseToken('(', 'brackets_op')
    parseExpression()
    parseToken(')', 'brackets_op')
    parseToken('{', 'brackets_op')

    while numRow <= len_tableOfSymb and getSymb()[1] != '}':
        parseStatement()

    parseToken('}', 'brackets_op')

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
        print(indent + 'в рядку {0} - токен {1}'.format(numLine, (lex, tok)))
        numRow += 1
    elif  tok == 'str':
        numRow += 1
    else:
        failParse('невідповідність інструкцій', (numLine, lex, tok, 'очікувався id або рядок'))


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


def parseIf():
    global numRow
    indent = nextIndt()
    print(indent + 'parseIf():')

    # Використовуємо parseToken для чистоти коду
    parseToken('if', 'keyword')
    parseToken('(', 'brackets_op')
    parseExpression()
    parseToken(')', 'brackets_op')
    parseToken('{', 'brackets_op')

    while numRow <= len_tableOfSymb and getSymb()[1] != '}':
        parseStatement()

    parseToken('}', 'brackets_op')

    # Перевіряємо наявність 'else'
    if numRow <= len_tableOfSymb and getSymb()[1] == 'else':
        print(indent + '  Знайдено else')
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
        failParse('невідповідність токенів', (numLine, lex, tok, 'var | let'))

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
            print(indent + f'  в рядку {numLine} - токен порівняння {(lex, tok)}')
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
            print(indent + 'в рядку {0} - токен {1}'.format(numLine, (lex, tok)))
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
            print(indent + 'в рядку {0} - токен {1}'.format(numLine, (lex, tok)))
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
        failParse('невідповідність токенів', (numLine, lex, tok, 'true | false | ! | (Expression)'))

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
            print(indent + 'в рядку {0} - токен {1}'.format(numLine, (lex, tok)))
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
            print(indent + 'в рядку {0} - токен {1}'.format(numLine, (lex, tok)))
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
            print(indent + 'в рядку {0} - токен {1}'.format(numLine, (lex, tok)))
            parseFactor()
        else:
            F = False
    indent = predIndt()


def parseFactor():
    global numRow
    indent = nextIndt()
    print(indent + 'parseFactor():')
    numLine, lex, tok = getSymb()

    if tok in ('id', 'intnum', 'floatnum'):
        print(indent + 'в рядку {0} - токен {1}'.format(numLine, (lex, tok)))
        numRow += 1
    elif (lex, tok) == ('(', 'brackets_op'):
        parseToken('(', 'brackets_op')
        parseArithmExpression()
        parseToken(')', 'brackets_op')
    else:
        failParse('невідповідність токенів', (numLine, lex, tok, 'ident | number | (arithmexpr)'))

    indent = predIndt()


def parseSign():
    global numRow
    indent = nextIndt()
    print(indent + 'parseSign():')
    numLine, lex, tok = getSymb()

    if (lex, tok) in (('+', 'add_op'), ('-', 'add_op')):
        parseToken(lex, 'add_op')
    else:
        failParse('невідповідність токенів', (numLine, lex, tok, '+ | -'))

    indent = predIndt()


def parseIdentList():
    global numRow
    indent = nextIndt()
    print(indent + 'parseIdentList():')

    numLine, lex, tok = getSymb()
    if tok != 'id':
        failParse('невідповідність токенів', (numLine, lex, tok, 'очікувався ідентифікатор'))

    print(indent + 'в рядку {0} - токен {1}'.format(numLine, (lex, tok)))
    numRow += 1

    while numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()
        if (lex, tok) == (',', 'punct'):
            numRow += 1  # Пропускаємо кому

            numLine, lex, tok = getSymb()  # Дивимось на токен після коми
            if tok != 'id':
                failParse('невідповідність токенів', (numLine, lex, tok, 'очікувався ідентифікатор після коми'))

            print(indent + 'в рядку {0} - токен {1}'.format(numLine, (lex, tok)))
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
        failParse('невідповідність токенів', (numLine, lex, tok, 'int | float | string | bool'))

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
        failParse('неочікуваний кінець програми', (lexeme, token, numRow))

    numLine, lex, tok = getSymb()

    if (lex, tok) == (lexeme, token):
        print(indent + 'parseToken: В рядку {0} токен {1}'.format(numLine, (lexeme, token)))
        numRow += 1
        predIndt()
        return True
    else:
        failParse('невідповідність токенів', (numLine, lex, tok, lexeme, token))
        return False



def getSymb():
    if numRow > len_tableOfSymb:
        failParse('getSymb(): неочікуваний кінець програми', numRow)
    numLine, lexeme, token, _ = tableOfSymb[numRow]
    return numLine, lexeme, token


def failParse(str_msg, details):
    if str_msg == 'неочікуваний кінець програми':
        (lexeme, token, row) = details
        print(
            f'Parser ERROR: \n\t Неочікуваний кінець програми. Очікувався ({lexeme}, {token}) але таблиця символів закінчилась на рядку {row - 1}.')
        exit(1001)
    elif str_msg == 'getSymb(): неочікуваний кінець програми':
        row = details
        print(
            f'Parser ERROR: \n\t Спроба прочитати рядок {row} з таблиці символів, але вона містить лише {len_tableOfSymb} записів.')
        exit(1002)
    elif str_msg == 'невідповідність токенів':
        if len(details) == 5:
            (numLine, lexeme, token, expected_lex, expected_tok) = details
            print(
                f'Parser ERROR: \n\t В рядку {numLine} неочікуваний елемент ({lexeme},{token}). \n\t Очікувався - ({expected_lex},{expected_tok}).')
        else:
            (numLine, lexeme, token, expected) = details
            print(
                f'Parser ERROR: \n\t В рядку {numLine} неочікуваний елемент ({lexeme},{token}). \n\t Очікувався - {expected}.')
        exit(1)
    elif str_msg == 'невідповідність інструкцій':
        (numLine, lex, tok, expected) = details
        print(f'Parser ERROR: \n\t В рядку {numLine} неочікуваний елемент ({lex},{tok}). \n\t Очікувався - {expected}.')
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

