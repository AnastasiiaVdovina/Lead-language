# Generated from C:/Users/vdovi/PycharmProjects/Lead-language/ANTLR4_LL/Lead.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .LeadParser import LeadParser
else:
    from LeadParser import LeadParser

# This class defines a complete generic visitor for a parse tree produced by LeadParser.

class LeadVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by LeadParser#program.
    def visitProgram(self, ctx:LeadParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#declaration.
    def visitDeclaration(self, ctx:LeadParser.DeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#identList.
    def visitIdentList(self, ctx:LeadParser.IdentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#type.
    def visitType(self, ctx:LeadParser.TypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#functionDeclaration.
    def visitFunctionDeclaration(self, ctx:LeadParser.FunctionDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#paramList.
    def visitParamList(self, ctx:LeadParser.ParamListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#param.
    def visitParam(self, ctx:LeadParser.ParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#returnStatement.
    def visitReturnStatement(self, ctx:LeadParser.ReturnStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#statement.
    def visitStatement(self, ctx:LeadParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#assignStatement.
    def visitAssignStatement(self, ctx:LeadParser.AssignStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#inputStatement.
    def visitInputStatement(self, ctx:LeadParser.InputStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#outputStatement.
    def visitOutputStatement(self, ctx:LeadParser.OutputStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#ifStatement.
    def visitIfStatement(self, ctx:LeadParser.IfStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#guardStatement.
    def visitGuardStatement(self, ctx:LeadParser.GuardStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#switchStatement.
    def visitSwitchStatement(self, ctx:LeadParser.SwitchStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#caseBlock.
    def visitCaseBlock(self, ctx:LeadParser.CaseBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#defaultBlock.
    def visitDefaultBlock(self, ctx:LeadParser.DefaultBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#forStatement.
    def visitForStatement(self, ctx:LeadParser.ForStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#whileStatement.
    def visitWhileStatement(self, ctx:LeadParser.WhileStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#repeatWhileStatement.
    def visitRepeatWhileStatement(self, ctx:LeadParser.RepeatWhileStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#expressionStatement.
    def visitExpressionStatement(self, ctx:LeadParser.ExpressionStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#codeBlock.
    def visitCodeBlock(self, ctx:LeadParser.CodeBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#expression.
    def visitExpression(self, ctx:LeadParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#condition.
    def visitCondition(self, ctx:LeadParser.ConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#boolExpression.
    def visitBoolExpression(self, ctx:LeadParser.BoolExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#boolTerm.
    def visitBoolTerm(self, ctx:LeadParser.BoolTermContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#boolFactor.
    def visitBoolFactor(self, ctx:LeadParser.BoolFactorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#comparison.
    def visitComparison(self, ctx:LeadParser.ComparisonContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#relOp.
    def visitRelOp(self, ctx:LeadParser.RelOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#arithmExpression.
    def visitArithmExpression(self, ctx:LeadParser.ArithmExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#term.
    def visitTerm(self, ctx:LeadParser.TermContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#factor.
    def visitFactor(self, ctx:LeadParser.FactorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#sign.
    def visitSign(self, ctx:LeadParser.SignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#funcCall.
    def visitFuncCall(self, ctx:LeadParser.FuncCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LeadParser#argList.
    def visitArgList(self, ctx:LeadParser.ArgListContext):
        return self.visitChildren(ctx)



del LeadParser