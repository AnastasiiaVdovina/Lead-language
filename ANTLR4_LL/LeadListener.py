# Generated from C:/Users/vdovi/PycharmProjects/Lead-language/ANTLR4_LL/Lead.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .LeadParser import LeadParser
else:
    from LeadParser import LeadParser

# This class defines a complete listener for a parse tree produced by LeadParser.
class LeadListener(ParseTreeListener):

    # Enter a parse tree produced by LeadParser#program.
    def enterProgram(self, ctx:LeadParser.ProgramContext):
        pass

    # Exit a parse tree produced by LeadParser#program.
    def exitProgram(self, ctx:LeadParser.ProgramContext):
        pass


    # Enter a parse tree produced by LeadParser#declaration.
    def enterDeclaration(self, ctx:LeadParser.DeclarationContext):
        pass

    # Exit a parse tree produced by LeadParser#declaration.
    def exitDeclaration(self, ctx:LeadParser.DeclarationContext):
        pass


    # Enter a parse tree produced by LeadParser#identList.
    def enterIdentList(self, ctx:LeadParser.IdentListContext):
        pass

    # Exit a parse tree produced by LeadParser#identList.
    def exitIdentList(self, ctx:LeadParser.IdentListContext):
        pass


    # Enter a parse tree produced by LeadParser#type.
    def enterType(self, ctx:LeadParser.TypeContext):
        pass

    # Exit a parse tree produced by LeadParser#type.
    def exitType(self, ctx:LeadParser.TypeContext):
        pass


    # Enter a parse tree produced by LeadParser#functionDeclaration.
    def enterFunctionDeclaration(self, ctx:LeadParser.FunctionDeclarationContext):
        pass

    # Exit a parse tree produced by LeadParser#functionDeclaration.
    def exitFunctionDeclaration(self, ctx:LeadParser.FunctionDeclarationContext):
        pass


    # Enter a parse tree produced by LeadParser#paramList.
    def enterParamList(self, ctx:LeadParser.ParamListContext):
        pass

    # Exit a parse tree produced by LeadParser#paramList.
    def exitParamList(self, ctx:LeadParser.ParamListContext):
        pass


    # Enter a parse tree produced by LeadParser#param.
    def enterParam(self, ctx:LeadParser.ParamContext):
        pass

    # Exit a parse tree produced by LeadParser#param.
    def exitParam(self, ctx:LeadParser.ParamContext):
        pass


    # Enter a parse tree produced by LeadParser#returnStatement.
    def enterReturnStatement(self, ctx:LeadParser.ReturnStatementContext):
        pass

    # Exit a parse tree produced by LeadParser#returnStatement.
    def exitReturnStatement(self, ctx:LeadParser.ReturnStatementContext):
        pass


    # Enter a parse tree produced by LeadParser#statement.
    def enterStatement(self, ctx:LeadParser.StatementContext):
        pass

    # Exit a parse tree produced by LeadParser#statement.
    def exitStatement(self, ctx:LeadParser.StatementContext):
        pass


    # Enter a parse tree produced by LeadParser#assignStatement.
    def enterAssignStatement(self, ctx:LeadParser.AssignStatementContext):
        pass

    # Exit a parse tree produced by LeadParser#assignStatement.
    def exitAssignStatement(self, ctx:LeadParser.AssignStatementContext):
        pass


    # Enter a parse tree produced by LeadParser#inputStatement.
    def enterInputStatement(self, ctx:LeadParser.InputStatementContext):
        pass

    # Exit a parse tree produced by LeadParser#inputStatement.
    def exitInputStatement(self, ctx:LeadParser.InputStatementContext):
        pass


    # Enter a parse tree produced by LeadParser#outputStatement.
    def enterOutputStatement(self, ctx:LeadParser.OutputStatementContext):
        pass

    # Exit a parse tree produced by LeadParser#outputStatement.
    def exitOutputStatement(self, ctx:LeadParser.OutputStatementContext):
        pass


    # Enter a parse tree produced by LeadParser#ifStatement.
    def enterIfStatement(self, ctx:LeadParser.IfStatementContext):
        pass

    # Exit a parse tree produced by LeadParser#ifStatement.
    def exitIfStatement(self, ctx:LeadParser.IfStatementContext):
        pass


    # Enter a parse tree produced by LeadParser#guardStatement.
    def enterGuardStatement(self, ctx:LeadParser.GuardStatementContext):
        pass

    # Exit a parse tree produced by LeadParser#guardStatement.
    def exitGuardStatement(self, ctx:LeadParser.GuardStatementContext):
        pass


    # Enter a parse tree produced by LeadParser#switchStatement.
    def enterSwitchStatement(self, ctx:LeadParser.SwitchStatementContext):
        pass

    # Exit a parse tree produced by LeadParser#switchStatement.
    def exitSwitchStatement(self, ctx:LeadParser.SwitchStatementContext):
        pass


    # Enter a parse tree produced by LeadParser#caseBlock.
    def enterCaseBlock(self, ctx:LeadParser.CaseBlockContext):
        pass

    # Exit a parse tree produced by LeadParser#caseBlock.
    def exitCaseBlock(self, ctx:LeadParser.CaseBlockContext):
        pass


    # Enter a parse tree produced by LeadParser#defaultBlock.
    def enterDefaultBlock(self, ctx:LeadParser.DefaultBlockContext):
        pass

    # Exit a parse tree produced by LeadParser#defaultBlock.
    def exitDefaultBlock(self, ctx:LeadParser.DefaultBlockContext):
        pass


    # Enter a parse tree produced by LeadParser#forStatement.
    def enterForStatement(self, ctx:LeadParser.ForStatementContext):
        pass

    # Exit a parse tree produced by LeadParser#forStatement.
    def exitForStatement(self, ctx:LeadParser.ForStatementContext):
        pass


    # Enter a parse tree produced by LeadParser#whileStatement.
    def enterWhileStatement(self, ctx:LeadParser.WhileStatementContext):
        pass

    # Exit a parse tree produced by LeadParser#whileStatement.
    def exitWhileStatement(self, ctx:LeadParser.WhileStatementContext):
        pass


    # Enter a parse tree produced by LeadParser#repeatWhileStatement.
    def enterRepeatWhileStatement(self, ctx:LeadParser.RepeatWhileStatementContext):
        pass

    # Exit a parse tree produced by LeadParser#repeatWhileStatement.
    def exitRepeatWhileStatement(self, ctx:LeadParser.RepeatWhileStatementContext):
        pass


    # Enter a parse tree produced by LeadParser#expressionStatement.
    def enterExpressionStatement(self, ctx:LeadParser.ExpressionStatementContext):
        pass

    # Exit a parse tree produced by LeadParser#expressionStatement.
    def exitExpressionStatement(self, ctx:LeadParser.ExpressionStatementContext):
        pass


    # Enter a parse tree produced by LeadParser#codeBlock.
    def enterCodeBlock(self, ctx:LeadParser.CodeBlockContext):
        pass

    # Exit a parse tree produced by LeadParser#codeBlock.
    def exitCodeBlock(self, ctx:LeadParser.CodeBlockContext):
        pass


    # Enter a parse tree produced by LeadParser#expression.
    def enterExpression(self, ctx:LeadParser.ExpressionContext):
        pass

    # Exit a parse tree produced by LeadParser#expression.
    def exitExpression(self, ctx:LeadParser.ExpressionContext):
        pass


    # Enter a parse tree produced by LeadParser#condition.
    def enterCondition(self, ctx:LeadParser.ConditionContext):
        pass

    # Exit a parse tree produced by LeadParser#condition.
    def exitCondition(self, ctx:LeadParser.ConditionContext):
        pass


    # Enter a parse tree produced by LeadParser#boolExpression.
    def enterBoolExpression(self, ctx:LeadParser.BoolExpressionContext):
        pass

    # Exit a parse tree produced by LeadParser#boolExpression.
    def exitBoolExpression(self, ctx:LeadParser.BoolExpressionContext):
        pass


    # Enter a parse tree produced by LeadParser#boolTerm.
    def enterBoolTerm(self, ctx:LeadParser.BoolTermContext):
        pass

    # Exit a parse tree produced by LeadParser#boolTerm.
    def exitBoolTerm(self, ctx:LeadParser.BoolTermContext):
        pass


    # Enter a parse tree produced by LeadParser#boolFactor.
    def enterBoolFactor(self, ctx:LeadParser.BoolFactorContext):
        pass

    # Exit a parse tree produced by LeadParser#boolFactor.
    def exitBoolFactor(self, ctx:LeadParser.BoolFactorContext):
        pass


    # Enter a parse tree produced by LeadParser#comparison.
    def enterComparison(self, ctx:LeadParser.ComparisonContext):
        pass

    # Exit a parse tree produced by LeadParser#comparison.
    def exitComparison(self, ctx:LeadParser.ComparisonContext):
        pass


    # Enter a parse tree produced by LeadParser#relOp.
    def enterRelOp(self, ctx:LeadParser.RelOpContext):
        pass

    # Exit a parse tree produced by LeadParser#relOp.
    def exitRelOp(self, ctx:LeadParser.RelOpContext):
        pass


    # Enter a parse tree produced by LeadParser#arithmExpression.
    def enterArithmExpression(self, ctx:LeadParser.ArithmExpressionContext):
        pass

    # Exit a parse tree produced by LeadParser#arithmExpression.
    def exitArithmExpression(self, ctx:LeadParser.ArithmExpressionContext):
        pass


    # Enter a parse tree produced by LeadParser#term.
    def enterTerm(self, ctx:LeadParser.TermContext):
        pass

    # Exit a parse tree produced by LeadParser#term.
    def exitTerm(self, ctx:LeadParser.TermContext):
        pass


    # Enter a parse tree produced by LeadParser#factor.
    def enterFactor(self, ctx:LeadParser.FactorContext):
        pass

    # Exit a parse tree produced by LeadParser#factor.
    def exitFactor(self, ctx:LeadParser.FactorContext):
        pass


    # Enter a parse tree produced by LeadParser#sign.
    def enterSign(self, ctx:LeadParser.SignContext):
        pass

    # Exit a parse tree produced by LeadParser#sign.
    def exitSign(self, ctx:LeadParser.SignContext):
        pass


    # Enter a parse tree produced by LeadParser#funcCall.
    def enterFuncCall(self, ctx:LeadParser.FuncCallContext):
        pass

    # Exit a parse tree produced by LeadParser#funcCall.
    def exitFuncCall(self, ctx:LeadParser.FuncCallContext):
        pass


    # Enter a parse tree produced by LeadParser#argList.
    def enterArgList(self, ctx:LeadParser.ArgListContext):
        pass

    # Exit a parse tree produced by LeadParser#argList.
    def exitArgList(self, ctx:LeadParser.ArgListContext):
        pass



del LeadParser