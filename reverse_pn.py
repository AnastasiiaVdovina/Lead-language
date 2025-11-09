from symbol_table import tabName
from parser import tableOfId
from parser import tableOfConst
from parser import tableOfSymb
import json
#token allowed in PSM використовувати суто їх щоб не писати потім свою стекову машину
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

reverse_pn_table = []
buffer = []
last_index = 0

# менше значення - вищий пріорітет
PRIORITY = {
    '**' : 1,

    '!' : 2,
    '@' : 2, #унарний мінус

    '*': 3,
    '/': 3,

    '+' : 4,
    '-' : 4,

    '<=' : 5,
    '>' : 5,
    '>=' : 5,
    '==' : 5,
    '!=' : 5,
    '<' : 5,

    '&&' : 6,
    '||' : 7,

    '=' : 8,
    #для складного присвоювання потрібна додаткова обробка
    '+=' : 8,
    '-=' : 8,
    '*=' : 8,
    '/=' : 8,

    ')' : 9,
    '(' : 10
}

def postfix_generatro() :
    print()

#алгоритм дейкстри для запису арифметичних дій у поліз
#та рекурсивний спуск по таблиці лексера в цілому(оскільки поліз запускається після усіх аналізаторів то норм)
def dijkstra_rpn(table):
    buffer = []
    reverse_pn_table = []

    #необхідно окремо обробляти всі інструкції та функції з урахуванням JMP JF та міток
    for _, (_, lex, tok, _) in table.items():
        if tok in ("comment", "keyword", "ws", "eol"):
            # функції
            # if tok == "func":
            #  керуючі конструкції
            # elif lex == "if":
            # elif lex == "for":
            # elif lex == "switch":

            continue

        # операнди
        if tok == "id":
            reverse_pn_table.append((lex, "l-val"))
        elif tok in ("intnum", "realnum", "boolval", "str"):
            reverse_pn_table.append((lex, type_map[tok]))

        # оператори
        elif tok in type_map and type_map[tok] in ("math_op", "rel_op", "assign_op", "pow_op", "bool_op"):
            while buffer and PRIORITY.get(buffer[-1][0], 99) <= PRIORITY.get(lex, 99):
                reverse_pn_table.append(buffer.pop())
            buffer.append((lex, type_map[tok]))

        # дужки
        elif tok == "brackets_op":
            if lex == '(':
                buffer.append((lex, tok))
            elif lex == ')':
                while buffer and buffer[-1][0] != '(':
                    reverse_pn_table.append(buffer.pop())
                buffer.pop()  # remove '('



        # оператори вводу-виводу
        elif tok == "print":
            reverse_pn_table.append((lex, "out_op"))
        elif tok == "input":
            reverse_pn_table.append((lex, "inp_op"))


    # спорожнити стек
    while buffer:
        reverse_pn_table.append(buffer.pop())
    for i in reverse_pn_table:
        print(i)

    return reverse_pn_table


def generate_postfix_file(filename, vars_table, reverse_pn_table, labels_table=None):
    output_path = f"{filename}.postfix"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(".target: Postfix Machine\n")
        f.write(".version: 0.3\n\n")

        f.write(".vars(\n")
        for scope, vars_dict in vars_table.items():
            for var_name, attributes in vars_dict.items():
                if var_name == "declIn":
                    continue
                # attributes[2] це тип int, float, bool, string
                f.write(f"\t{var_name}\t{attributes[2]}\n")
        f.write(")\n\n")

        #для міток. окремо треба штуку зробити для кожної малої функції(як у прикладах psm)
        f.write(".labels(\n")
        if labels_table:
            for lbl, addr in labels_table.items():
                f.write(f"\t{lbl}\t{addr}\n")
        f.write(")\n\n")

        f.write(".code(\n")
        for lexeme, token_type in reverse_pn_table:
            f.write(f"\t{lexeme:<10}\t{token_type}\n")
        f.write(")\n")

    print(f"Postfix file was generated: {filename}")

if __name__ == '__main__':
    reverse_table = dijkstra_rpn(tableOfSymb)
    generate_postfix_file("test", tabName, reverse_table)