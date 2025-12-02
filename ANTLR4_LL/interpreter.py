import sys
from LeadParser import LeadParser
from LeadVisitor import LeadVisitor


class LeadInterpreter(LeadVisitor):
    def __init__(self):
        self.memory = {}
        self.types = {}
        self.constants = set()

        self.defaults = {
            'int': 0,
            'float': 0.0,
            'bool': False,
            'string': ""
        }

    def check_type_compatibility(self, var_name, target_type, value):
        val_type = type(value)

        if target_type == 'int' and val_type == int: return value
        if target_type == 'float' and val_type == float: return value
        if target_type == 'bool' and val_type == bool: return value
        if target_type == 'string' and val_type == str: return value

        if target_type == 'float' and val_type == int:
            return float(value)

        if target_type == 'int' and val_type == float:
            raise TypeError(f"Semantic Error: Implicit conversion from 'float' to 'int' for '{var_name}' is forbidden.")

        raise TypeError(
            f"Semantic Error: Type mismatch for '{var_name}'. Expected {target_type}, got {val_type.__name__}.")


    def visitOutputStatement(self, ctx: LeadParser.OutputStatementContext):
        if ctx.STRING():

            print(ctx.STRING().getText()[1:-1])
        elif ctx.expression():
            val = self.visit(ctx.expression())
            print(val)
        return None

    def visitInputStatement(self, ctx: LeadParser.InputStatementContext):
        name = ctx.IDENTIFIER().getText()

        if name not in self.memory:
            raise NameError(f"Runtime Error: Variable '{name}' is not defined.")

        target_type = self.types.get(name, 'string')

        while True:
            try:
                user_input = input(f"Input for '{name}' ({target_type}): ")

                val = None
                if target_type == 'int':
                    val = int(user_input)
                elif target_type == 'float':
                    val = float(user_input)
                elif target_type == 'bool':
                    val = user_input.lower() == 'true'
                else:
                    val = user_input  # string

                self.memory[name] = val
                return val

            except ValueError:
                print(f"Invalid input! Variable '{name}' expects type '{target_type}'. Try again.")


    def visitDeclaration(self, ctx: LeadParser.DeclarationContext):
        var_names = [node.getText() for node in ctx.identList().IDENTIFIER()]
        var_type = ctx.type_().getText()

        value = None
        has_init = False
        if ctx.expression():
            value = self.visit(ctx.expression())
            has_init = True
        else:
            value = self.defaults[var_type]

        for name in var_names:
            if name in self.memory:
                raise Exception(f"Semantic Error: Variable '{name}' is already declared in this scope.")

            if has_init:
                final_value = self.check_type_compatibility(name, var_type, value)
            else:
                final_value = value

            self.memory[name] = final_value
            self.types[name] = var_type

        return final_value

    def visitAssignStatement(self, ctx: LeadParser.AssignStatementContext):
        name = ctx.IDENTIFIER().getText()

        if name not in self.memory:
            raise NameError(f"Semantic Error: Variable '{name}' is not declared.")

        if name in self.constants:
            raise Exception(f"Semantic Error: Cannot assign to constant '{name}'.")

        value = self.visit(ctx.expression())
        target_type = self.types[name]

        final_value = self.check_type_compatibility(name, target_type, value)

        self.memory[name] = final_value
        return final_value



    def visitIfStatement(self, ctx: LeadParser.IfStatementContext):
        conditions = ctx.condition()
        code_blocks = ctx.codeBlock()


        for i in range(len(conditions)):
            if self.visit(conditions[i]):
                self.visit(code_blocks[i])
                return


        if len(code_blocks) > len(conditions):
            self.visit(code_blocks[-1])
        return None

    def visitWhileStatement(self, ctx: LeadParser.WhileStatementContext):
        while self.visit(ctx.condition()):
            self.visit(ctx.codeBlock())
        return None

    def visitSwitchStatement(self, ctx: LeadParser.SwitchStatementContext):
        var_name = ctx.IDENTIFIER().getText()
        if var_name not in self.memory:
            raise Exception(f"Error: Variable '{var_name}' is not defined.")

        switch_val = self.memory[var_name]
        matched = False

        for case_ctx in ctx.caseBlock():

            case_num_text = case_ctx.NUMBER().getText()

            # Перевірка на мінус
            is_negative = False
            if case_ctx.getChildCount() > 3 and case_ctx.getChild(1).getText() == '-':
                is_negative = True

            case_val = float(case_num_text)
            if is_negative: case_val = -case_val

            # Якщо switch_val int, а case_val 1.0 -> вони рівні
            if switch_val == case_val:
                matched = True
                for stmt in case_ctx.statement():
                    self.visit(stmt)
                break

        if not matched and ctx.defaultBlock():
            for stmt in ctx.defaultBlock().statement():
                self.visit(stmt)
        return None


    def visitTerm(self, ctx: LeadParser.TermContext):
        result = self.visit(ctx.factor(0))
        child_count = ctx.getChildCount()
        current_factor_idx = 1

        for i in range(1, child_count, 2):
            op = ctx.getChild(i).getText()
            next_val = self.visit(ctx.factor(current_factor_idx))
            current_factor_idx += 1

            if isinstance(result, float) or isinstance(next_val, float):
                if isinstance(result, int): result = float(result)
                if isinstance(next_val, int): next_val = float(next_val)

            if op == '*':
                result *= next_val
            elif op == '/':
                if next_val == 0:
                    raise ZeroDivisionError(f"Runtime Error: Division by zero!")

                is_both_int = isinstance(result, int) and isinstance(next_val, int)
                if is_both_int:
                    result = result // next_val
                else:
                    result = result / next_val

            elif op == '**':
                result **= next_val

        return result

    def visitArithmExpression(self, ctx: LeadParser.ArithmExpressionContext):
        result = self.visit(ctx.term(0))
        if ctx.sign() and ctx.sign().getText() == '-':
            result = -result

        term_idx = 1
        child_count = ctx.getChildCount()
        current_child_idx = 1 if not ctx.sign() else 2

        while current_child_idx < child_count:
            op = ctx.getChild(current_child_idx).getText()
            current_child_idx += 1
            next_val = self.visit(ctx.term(term_idx))
            term_idx += 1
            current_child_idx += 1

            if isinstance(result, float) or isinstance(next_val, float):
                if isinstance(result, int): result = float(result)
                if isinstance(next_val, int): next_val = float(next_val)

            if op == '+':
                result += next_val
            elif op == '-':
                result -= next_val

        return result



    def visitComparison(self, ctx: LeadParser.ComparisonContext):
        left = self.visit(ctx.arithmExpression(0))
        right = self.visit(ctx.arithmExpression(1))
        op = ctx.relOp().getText()

        # Правило: int з float перетворюється на float
        if isinstance(left, float) or isinstance(right, float):
            if isinstance(left, int): left = float(left)
            if isinstance(right, int): right = float(right)

        res = False
        if op == '==':
            res = (left == right)
        elif op == '!=':
            res = (left != right)
        elif op == '<':
            res = (left < right)
        elif op == '>':
            res = (left > right)
        elif op == '<=':
            res = (left <= right)
        elif op == '>=':
            res = (left >= right)

        return bool(res)

    def visitBoolExpression(self, ctx: LeadParser.BoolExpressionContext):
        # BoolExpression = BoolTerm { "||" BoolTerm }
        result = self.visit(ctx.boolTerm(0))
        for i in range(1, len(ctx.boolTerm())):
            next_val = self.visit(ctx.boolTerm(i))
            result = result or next_val
        return result

    def visitBoolTerm(self, ctx: LeadParser.BoolTermContext):
        result = self.visit(ctx.boolFactor(0))
        for i in range(1, len(ctx.boolFactor())):
            next_val = self.visit(ctx.boolFactor(i))
            result = result and next_val
        return result

    def visitBoolFactor(self, ctx: LeadParser.BoolFactorContext):
        if ctx.getText() == 'true': return True
        if ctx.getText() == 'false': return False
        if ctx.comparison(): return self.visit(ctx.comparison())
        if ctx.boolExpression(): return self.visit(ctx.boolExpression())
        if ctx.getChild(0).getText() == '!': return not self.visit(ctx.boolFactor())
        return False


    def visitExpression(self, ctx: LeadParser.ExpressionContext):
        if ctx.arithmExpression():
            return self.visit(ctx.arithmExpression())
        return self.visit(ctx.boolExpression())

    def visitFactor(self, ctx: LeadParser.FactorContext):
        if ctx.NUMBER():
            txt = ctx.NUMBER().getText()
            return float(txt) if '.' in txt else int(txt)


        elif ctx.IDENTIFIER():
            name = ctx.IDENTIFIER().getText()
            if name in self.memory:
                return self.memory[name]
            else:
                raise NameError(f"Runtime Error: Variable '{name}' is not defined.")
        elif ctx.arithmExpression():
            return self.visit(ctx.arithmExpression())
        return 0