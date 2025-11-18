def saveCIL(fileName, tableOfVar, postfixCodeCLR, functions=None):
    if functions is None:
        functions = {}

    fname = fileName + ".il"
    with open(fname, 'w') as f:

        # ---------- HEADER ----------
        f.write(f"""// Referenced Assemblies
.assembly extern mscorlib
{{
  .publickeytoken = (B7 7A 5C 56 19 34 E0 89 )
  .ver 4:0:0:0
}}

.assembly {fileName}
{{
  .hash algorithm 0x00008004
  .ver 0:0:0:0
}}

.module {fileName}.exe

.class private auto ansi beforefieldinit Program
       extends [mscorlib]System.Object
{{
""")

        # ---------- MAIN ----------
        f.write("""
  .method private hidebysig static void Main() cil managed
  {
    .entrypoint
    .maxstack 16
    .locals init (
""")

        # MAIN LOCALS
        # tableOfVar format: {'varName': (index, kind, type, ...)}
        cntVars = len(tableOfVar)
        i = 0
        var_list = []
        for name, attr in tableOfVar.items():
            # Фільтруємо func, вони не є локальними змінними Main
            if name == 'declIn': continue
            if attr[1] == 'func': continue

            tp = attr[2]
            clr_tp = "int32"
            if tp in ("float", "floatnum"):
                clr_tp = "float32"
            elif tp in ("string", "str"):
                clr_tp = "string"
            elif tp == "bool":
                clr_tp = "bool"

            var_list.append(f"[{i}] {clr_tp} {name}")
            i += 1

        f.write(",\n      ".join(var_list))
        f.write("\n    )\n")

        # MAIN CODE
        for instr in postfixCodeCLR:
            f.write(instr + "\n")

        # Кінець Main
        f.write("    ret\n")
        f.write("  } // end of method Program::Main\n\n")

        # ---------- FUNCTIONS ----------
        # functions structure: {'funcName': {'ret': 'int32', 'args': [('a','int32')], 'locals': [('x','int32')], 'code': []}}
        for fname_func, fn in functions.items():
            ret = fn["ret"]
            args = fn["args"]  # List of tuples (name, type)
            locals_list = fn["locals"]  # List of tuples (name, type)
            code_list = fn["code"]

            # Формування списку аргументів для сигнатури: int32 a, float32 b
            arglist_str = ", ".join([f"{tp} {name}" for (name, tp) in args])

            f.write(f"  .method assembly hidebysig static {ret} '<Main>{fname_func}'({arglist_str}) cil managed\n")
            f.write("  {\n")
            f.write("    .maxstack 8\n")

            # locals function
            if locals_list:
                f.write("    .locals init (\n")
                loc_str_list = []
                for idx, (lname, ltp) in enumerate(locals_list):
                    loc_str_list.append(f"      [{idx}] {ltp} {lname}")
                f.write(",\n".join(loc_str_list))
                f.write("\n    )\n")

            # code function
            for line in code_list:
                f.write(line + "\n")

            f.write(f"  }} // end of method Program::'<Main>{fname_func}'\n\n")

        # ---------- END OF CLASS ----------
        f.write("} // end of class Program\n")

    print(f"IL-програма збережена у файлі {fname}")