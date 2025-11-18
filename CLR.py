codeCLR = [] #буфер для мейну
current_code_block = codeCLR # Вказівник на поточний буфер (для функцій)

# Тут будемо зберігати інформацію про поточну функцію під час генерації її коду
# Щоб знати, де аргументи (ldarg), а де локальні змінні (ldloc)
current_func_context = {
    "is_function": False,
    "args": [], # Список імен аргументів
    "name": ""
}
# Словник сигнатур функцій, щоб знати типи аргументів при виклику CALL
func_signatures = {}
tl = "    "

def suffixTypeCLR(Type):
    if Type in ('int', 'intnum', 'int32'):
        return 'i4'
    elif Type in ('float', 'floatnum', 'float32'):
        return 'r4'
    elif Type in ('string', 'str'):
        return 'string' # Для ldstr і типів
    elif Type in ('boolval', 'bool')== 'bool':
        return 'i4' # bool у CIL це int32 (0 або 1)
    return 'i4' # default

def mapTypeToCIL(Type):
    if Type in ('int', 'intnum'): return 'int32'
    if Type in ('float', 'floatnum'): return 'float32'
    if Type == 'bool': return 'bool'
    if Type == 'string': return 'string'
    if Type == 'void': return 'void'
    return 'void'

# Функція для перемикання контексту
def switchContextToFunction(funcName, args_names, code_list_ref):
    global current_code_block, current_func_context
    current_code_block = code_list_ref # Перемикаємо запис у список кодів функції
    current_func_context["is_function"] = True
    current_func_context["args"] = args_names
    current_func_context["name"] = funcName

def switchContextToMain():
    global current_code_block, current_func_context
    current_code_block = codeCLR
    current_func_context["is_function"] = False
    current_func_context["args"] = []


def postfixCLR_codeGen(case, toTran):
    global val, current_code_block

    if case == 'lval':
        lex = toTran
        # Перевіряємо, чи це аргумент функції
        if current_func_context["is_function"] and lex in current_func_context["args"]:
            arg_idx = current_func_context["args"].index(lex)
            current_code_block.append(tl + f'ldarga {arg_idx} // arg: {lex}')
        else:
            current_code_block.append(tl + 'ldloca ' + lex)

    elif case == 'rval':
        lex = toTran
        # Перевіряємо, чи це аргумент функції
        if current_func_context["is_function"] and lex in current_func_context["args"]:
            arg_idx = current_func_context["args"].index(lex)
            current_code_block.append(tl + f'ldarg {arg_idx} // arg: {lex}')
        else:
            current_code_block.append(tl + 'ldloc ' + lex)

    elif case == '=':
        typeVar = toTran
        current_code_block.append(tl + 'stind.' + suffixTypeCLR(typeVar))

    elif case == '+':
        current_code_block.append(tl + 'add')
    elif case == '-':
        current_code_block.append(tl + 'sub')
    elif case == '*':
        current_code_block.append(tl + 'mul')
    elif case == '/':
        current_code_block.append(tl + 'div')
    elif case == 'NEG':
        current_code_block.append(tl + 'neg')

    elif case == '**':
        current_code_block.append(tl + 'call float64 [mscorlib]System.Math::Pow(float64, float64)')

    elif case == 'const':
        lex, typeVar = toTran
        suffix = suffixTypeCLR(typeVar)
        if suffix == 'r4' and '.' not in str(lex):
            lex = str(lex) + '.0'
        current_code_block.append(tl + 'ldc.' + suffix + ' ' + str(lex))

    elif case == 'boolval':
        val = '1' if toTran == 'true' else '0'
        current_code_block.append(tl + 'ldc.i4 ' + val)

    elif case == 'str':
        current_code_block.append(tl + 'ldstr ' + toTran)

    elif case == 'rel_op':
        lex = toTran
        relopCLR = ''
        if lex == '<':
            relopCLR = 'clt'
        elif lex == '>':
            relopCLR = 'cgt'
        elif lex == '==':
            relopCLR = 'ceq'
        elif lex == '<=':
            # (a <= b) це заперечення (a > b)
            relopCLR = 'cgt\n' + tl + 'ldc.i4.0\n' + tl + 'ceq'
        elif lex == '>=':
            # (a >= b) це заперечення (a < b)
            relopCLR = 'clt\n' + tl + 'ldc.i4.0\n' + tl + 'ceq'
        elif lex == '!=':
            # (a != b) це заперечення (a == b)
            relopCLR = 'ceq\n' + tl + 'ldc.i4.0\n' + tl + 'ceq'

        current_code_block.append(tl + relopCLR)

    elif case == 'jf':
        lex = toTran
        current_code_block.append(tl + 'brfalse ' + lex)

    elif case == 'jump':
        lex = toTran
        current_code_block.append(tl + 'br ' + lex)

    elif case == 'label':
        lex = toTran + ':'
        current_code_block.append(lex)

    elif case == 'CALL':
        funcName = toTran[0]
        if funcName in func_signatures:
            sig = func_signatures[funcName]
            retType = sig['ret']
            argsTypes = sig['args']  # Список типів аргументів ['int32', 'float32']

            argsStr = ", ".join(argsTypes)

            cmd = f"call {retType} Program::'<Main>{funcName}'({argsStr})"
            current_code_block.append(tl + cmd)
        else:
            print(f"Warning: Function signature for '{funcName}' not found in CLR table.")

    # Повернення з функції
    elif case == 'RET':
        current_code_block.append(tl + 'ret')


    elif case == 'out_op':
        values = ""

        lex, type = toTran

        if type in ('bool', 'boolval'):
            values += "\t" + "call void [mscorlib]System.Console::WriteLine(bool) \n"
        elif type in ('int', 'intnum'):
            values += '\t' + "call void [mscorlib]System.Console::WriteLine(int32) \n"
        elif type in ('float', 'floatnum'):
            values +=  '\t' + "call void [mscorlib]System.Console::WriteLine(float32) \n"
        elif type in ('string', 'str'):
            values += '\t' + "call void [mscorlib]System.Console::WriteLine(string) \n"

        current_code_block.append(values)

    # elif case == 'out_op':
    #     values = ""
    #     lex = toTran
    #
    #     tp = "int"
    #     tp += '32'
    #     values += "\t" + "call void [mscorlib]System.Console::WriteLine(" + tp + ") \n"
    #
    #     codeCLR.append(values)


    elif case == 'out':
        values = ""
        lex = toTran
        #values += "\tldstr \"" + lex + "\"\n"
        values += "\tcall void [mscorlib]System.Console::WriteLine(string) \n"
        current_code_block.append(values + '\n')

    # INPUT з підтримкою аргументів
    elif case == 'input':
        varname, Type = toTran  # varname потрібен лише для prompt text

        # prompt
        current_code_block.append(tl + f'ldstr \"{varname} -> \"')
        current_code_block.append(tl + 'call void [mscorlib]System.Console::Write(string)')

        # read
        current_code_block.append(tl + 'call string [mscorlib]System.Console::ReadLine()')

        # conversion - leave converted value on the stack
        if Type in ('int', 'intnum', 'int32'):
            current_code_block.append(tl + 'call int32 [mscorlib]System.Convert::ToInt32(string)')
        elif Type in ('float', 'floatnum', 'float32'):
            current_code_block.append(tl + 'call float32 [mscorlib]System.Convert::ToSingle(string)')
        # for string: do nothing, string already on stack

    elif case == 'i2f':
        current_code_block.append(tl + 'conv.r4')

    return True
