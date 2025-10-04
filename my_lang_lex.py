 	
# Таблиця лексем мови
tokenTable = {
    # булеві константи
    'true': 'boolval',
    'false': 'boolval',

    # ключові слова
    'int': 'keyword', 'float': 'keyword', 'bool': 'keyword',
    'string': 'keyword', 'print': 'keyword', 'input': 'keyword',
    'while': 'keyword', 'repeat': 'keyword', 'for': 'keyword',
    'if': 'keyword', 'else': 'keyword', 'switch': 'keyword',
    'case': 'keyword', 'default': 'keyword', 'guard': 'keyword',
    'var': 'keyword', 'let': 'keyword',

    # функції
    'func': 'keyword', 'return': 'keyword', '=>': 'keyword',
    #func pow(int a, int b) => int{}

    # оператори присвоєння зі скороченням
    '+=': 'add_ass_op', '-=': 'add_ass_op',
    '*=': 'mult_ass_op', '/=': 'mult_ass_op',

    # логічні оператори
    '&&': 'logic_op', '||': 'logic_op', '!': 'logic_op',

    # арифметичні оператори
    '+': 'add_op', '-': 'add_op', '*': 'mult_op', '/': 'mult_op',

    # оператори відношення
    '=': 'assign_op',
    '>': 'rel_op', '<': 'rel_op', '>=': 'rel_op', '<=': 'rel_op',
    '==': 'rel_op', '!=': 'rel_op',

    # степеневий оператор
    '**': 'pow_op',

    # дужки
    '(': 'brackets_op', ')': 'brackets_op',
    '{': 'brackets_op', '}': 'brackets_op',
    '[': 'brackets_op', ']': 'brackets_op',

    # пунктуація
    '.': 'punct', ',': 'punct', ':': 'punct', ';': 'punct',

    # лапки
    '"': 'quote',


    # коментарі
    '//': 'comment', '/*': 'comment', '*/': 'comment',

    # пробіл і табуляція
    ' ': 'ws', '\t': 'ws',
    # роздільник рядків
    '\n': 'eol', '\r': 'eol'
}

# Решту токенів визначаємо не за лексемою, а за заключним станом
tokStateTable = {6:'id', 2: 'intnum', 4: 'floatnum', 15:'assign', 18: 'rel_op',  20:'str', 25:'spec_sign', 29:'comment', 31:'comment', 32:'comment', 34: 'newline'}

# Діаграма станів
#               Q                                   q0          F
# M = ({0, 1, 2, 3, 4, 5, 6, 7, 11, 12, 9,
# 8, 10, 19, 20, 21, 13, 16, 15, 14, 17, 18,
# 22, 23, 33, 26, 32, 30, 31, 27, 28, 29, 24, 25}, Σ,  δ , 0 , {2, 4, 6, 7, 12, 9, 10, 21,
#                                                               20, 15, 16, 14, 18, 23, 33, 32,
#                                                                   31, 29, 25})

# δ - state-transition_function
stf={(0,'WhiteSpace'):0,  (0,'Digit'):1, (1,'Digit'):1, (1,'other'):2,
     (1,'dot'):3, (3,'Digit'):3, (3,'other'):4,
     (0, 'Letter'):5, (5,'Letter'):5, (5,'other'):6,
     (0, 'other'):7,
     (0, 'OrP'):11, (11,'OrP'):12,
     (11, 'other'):9,
     (0, 'AndP'):8, (8,'AndP'):10,
     (8,'other'):9,
     (0, 'Quote'):19, (19,'other'):19, (19,'Quote'):20,
     (19,'NewLine'):21,
     (0, 'Equal'):13, (13,'other'):15,
     (13,'More'):16,
     (13,'Equal'):14,
     (0,'Less'):17,(0,'More'):17, (0,'Am'):17, (0,'Exclam'):17, (17,'Equal'):14,
     (17,'other'):18,
     (0,'Star'):22, (22,'other'):18,
     (22,'Star'):23,
     (22,'Equal'):33,
     (0,'FSlash'):26, (26,'Star'):27, (27,'other'):27, (27, 'NewLine'):27, (27,'Star'):28,
     (28,'FSlash'):29,
     (26,'FSlash'):30, (30,'other'):30, (30,'NewLine'):31,
     (26, 'Equal'):33,
     (26, 'other'):32,
     (0, 'SpecialSigns'):24, (24,'other'):25,
     (0, 'NewLine'):34

}

initState = 0   # q0 - стартовий стан
F={2, 4, 6, 7, 12, 9, 10, 21, 20, 15, 16, 14, 18, 23, 33, 32, 31, 29, 25, 34}
Fstar={2, 4, 6, 15, 18, 32, 25}   # зірочка
Ferror={7, 9, 21}# обробка помилок


tableOfId={}   # Таблиця ідентифікаторів
tableOfConst={} # Таблиця констант
tableOfSymb={}  # Таблиця символів програми (таблиця розбору)

state=initState # поточний стан

f = open('test.my_lang', 'r', encoding="utf-8")
sourceCode=f.read()
f.close()

# FSuccess - ознака успішності/неуспішності розбору
FSuccess = ('Lexer', False)

lenCode=len(sourceCode)-1       # номер останнього символа у файлі з кодом програми
numLine=1                       # лексичний аналіз починаємо з першого рядка
numChar=-1                      # з першого символа (в Python'і нумерація - з 0)
char=''                         # ще не брали жодного символа
lexeme=''                       # ще не починали розпізнавати лексеми


def lex():
  global state,numLine,char,lexeme,numChar,FSuccess
  try:
    while numChar<lenCode:
      char=nextChar()				  # прочитати наступний символ
      classCh=classOfChar(char)		  # до якого класу належить
      state=nextState(state,classCh)  # обчислити наступний стан
      if (is_final(state)): 		  # якщо стан заключний
        processing()				  # виконати семантичні процедури
      elif state==initState:
        lexeme=''       # якщо стан НЕ заключний, а стартовий - нова лексема
      else:
        if char=="\n":
            numLine+=1
        lexeme+=char	# якщо стан НЕ закл. і не стартовий - додати символ до лексеми
    print('Lexer: Lexical analysis completed successfully')
    FSuccess = ('Lexer', True)
  except SystemExit as e:
    # Повідомити про факт виявлення помилки
    print('Lexer: Program terminated with code {0}'.format(e))

def processing():
    global state, lexeme, char, numLine, numChar, tableOfSymb

    # --- числа та ідентифікатори ---
    if state in (2, 4, 6):  # intnum, floatnum, id
        token = getToken(state, lexeme)
        if token != 'keyword':  # звичайний id/число
            index = indexIdConst(state, lexeme)
            print(f"{numLine:<3d} {lexeme:<10s} {token:<10s} {index:<5d}")
            tableOfSymb[len(tableOfSymb)+1] = (numLine, lexeme, token, index)
        else:  # ключове слово
            print(f"{numLine:<3d} {lexeme:<10s} {token:<10s}")
            tableOfSymb[len(tableOfSymb)+1] = (numLine, lexeme, token, '')
        lexeme = ''
        numChar = putCharBack(numChar)  # зірочка
        state = initState
        return


    # --- оператор "=" ---
    if state == 15:
        token = getToken(state, lexeme)
        print(f"{numLine:<3d} {lexeme:<10s} {token:<10s}")
        tableOfSymb[len(tableOfSymb)+1] = (numLine, lexeme, token, '')
        lexeme = ''
        state = initState
        return

    # --- оператори з двох символів  ---
    if state in (10, 12, 14, 16, 23, 33):
        lexeme += char
        token = getToken(state, lexeme)
        print(f"{numLine:<3d} {lexeme:<10s} {token:<10s}")
        tableOfSymb[len(tableOfSymb)+1] = (numLine, lexeme, token, '')
        lexeme = ''
        state = initState
        return

    # --- дужки та пунктуація  ---
    if state == 25:
        token = getToken(state, lexeme)
        print(f'{numLine:<3d} {lexeme:<10s} {token:<10s}')
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        numChar = putCharBack(numChar)
        state = initState
        return



    # --- рядкові константи ---
    if state == 20:
        token = getToken(state, lexeme)
        index = indexIdConst(state, lexeme)
        print(f"{numLine:<3d} {lexeme:<10s} {token:<10s} {index:<5d}")
        tableOfSymb[len(tableOfSymb)+1] = (numLine, lexeme, token, index)
        lexeme = ''
        state = initState
        return

    # --- коментарі однорядкові ---
    if state == 31:  # кінець однорядкового коментаря
        token = getToken(state, lexeme.strip())
        marker = ''
        if token == 'comment':
            for key, val in tokenTable.items():
                if val == 'comment' and lexeme.strip().startswith(key):
                    marker = key
                    break

        print(f"{numLine:<3d} {lexeme.strip():<10s} {token:<10s}")
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, marker, token, '')
        lexeme = ''
        state = initState
        numLine += 1  # підвищуємо рядок саме тут
        return


    # --- кінець блочного коментаря ---
    if state == 29:  # фінальний стан для блочного коментаря
        lexeme += char  # додати останні символи (*/)
        token = getToken(state, lexeme)
        marker = ''
        if token == 'comment':
            for key, val in tokenTable.items():
                if val == 'comment' and lexeme.strip().startswith(key):
                    marker = key
                    break

        print(f"{numLine:<3d} {lexeme.strip():<10s} {token:<10s}")
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, marker + marker[::-1], token, '')
        lexeme = ''
        state = initState
        return

    # --- перенос строки ---

    if state == 34:
        lexeme = ''
        state = initState
        numLine = numLine + 1
        return

    # --- одиничні математичні оператори (+, -, *, /) ---

    if state in (18, 32):
        token = getToken(state, lexeme)
        print(f"{numLine:<3d} {lexeme:<10s} {token:<10s}")
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        numChar = putCharBack(numChar)
        state = initState
        return



    # --- помилки ---
    if state in Ferror:
        fail()



def fail():
  global state,numLine,char
  print(numLine)
  if state == 7:
    print(f'ERROR 7: in line {numLine}  unexpected character  was met -> "{char}"')
    exit(7)
  if state == 9:
    print(f'ERROR 9: unexpected character  was met -> "{char}" in line {numLine}. SUGGESTED CORRECTION: might be symbols || or &&')
    exit(9)
  if state == 21:
    print(f'ERROR 21: unexpected character  was met -> "{char}" in line {numLine}. Multiline strings are not allowed. ')
    exit(21)
  
  
def is_final(state):
  if (state in F):
    return True
  else:
    return False

def nextState(state,classCh):
  try:
    return stf[(state,classCh)]
  except KeyError:
  	return stf[(state,'other')]

def nextChar():
  global numChar
  numChar+=1
  return sourceCode[numChar]

def putCharBack(numChar):
  return numChar-1

def classOfChar(char):
    if char == '.':
        res = "dot"
    elif char.isalpha():
        res = "Letter"
    elif char.isdigit():
        res = "Digit"
    elif char == "\t" or char == " ":
        res = "WhiteSpace"
    elif char == "\n" or char == "\r":
        res = "NewLine"
    elif char == '=':
        res = "Equal"
    elif char == '>':
        res = "More"
    elif char == '<':
        res = "Less"
    elif char == '&':
        res = "AndP"
    elif char == '|':
        res = "OrP"
    elif char == '"':
        res = "Quote"
    elif char == '!':
        res = "Exclam"
    elif char == '*':
        res = "Star"
    elif char == '/':
        res = "FSlash"
    elif char in '(){}[],:;':
        res = "SpecialSigns"
    elif char in '+-':
        res = 'Am'

    else:
        res = "other"
    return res


def getToken(state,lexeme):
  try:
    return tokenTable[lexeme]
  except KeyError:
    return tokStateTable[state]


def indexIdConst(state,lexeme):
  indx=0
  if state==6:
    indx=tableOfId.get(lexeme)
    if indx is None:
      indx=len(tableOfId)+1
      tableOfId[lexeme]=indx
  if state in (2,4):
    obj=tableOfConst.get(lexeme)
    if obj is not None:
        indx=obj[1]

    else:
        indx=len(tableOfConst)+1
        tableOfConst[lexeme]=(tokStateTable[state],indx)

  return indx


# запуск лексичного аналізатора	
lex()


# Таблиці: розбору, ідентифікаторів та констант
# print('-'*100)
# print('tableOfSymb:{0}'.format(tableOfSymb))
# print('tableOfId:{0}'.format(tableOfId))
# print('tableOfConst:{0}'.format(tableOfConst))

print('-' * 100)
print('--- Lexical analysis tables ---')


def format_table_of_symb_tabular(symb_table):
    # Заголовки стовпців
    header = f"| {'Line':<10} | {'Lexeme':<35} | {'Token':<15} | {'Index':<5}"
    separator = "-" * len(header)

    output = f"{header}\n{separator}\n"

    for k, v in symb_table.items():
        line, lexeme, token, index = v
        index_str = str(index) if index != '' else ''
        row = f"| {str(line):<10} | {lexeme:<35} | {token:<15} | {index_str:<5}"
        output += f"{row}\n"

    return output


def format_id_const_tabular(data_table, name):

    if name == 'tableOfId':
        header = f"| {'Identifier':<15} | {'Index':<5}"
    else:  # tableOfConst
        header = f"| {'Constant':<15} | {'Type':<10} | {'Index':<5}"

    separator = "-" * len(header)
    output = f"\n{name}:\n{header}\n{separator}\n"

    k_list = list(data_table.keys())

    for k in k_list:
        v = data_table[k]

        if name == 'tableOfId':
            row = f"| {k:<15} | {v:<5}"  # # = Index
        else:
            # v = (type, index)
            c_type, c_index = v
            row = f"| {k:<15} | {c_type:<10} | {c_index:<5}"

        output += f"{row}\n"

    return output



print("\ntableOfSymb:")
print(format_table_of_symb_tabular(tableOfSymb))
print(format_id_const_tabular(tableOfId, 'tableOfId'))
print(format_id_const_tabular(tableOfConst, 'tableOfConst'))