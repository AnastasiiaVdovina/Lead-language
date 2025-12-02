import sys
from antlr4 import *
from LeadLexer import LeadLexer
from LeadParser import LeadParser
from interpreter import LeadInterpreter


def main():

    code = 'test.txt'

    input_stream = FileStream(code, encoding='utf-8')
    lexer = LeadLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = LeadParser(stream)
    tree = parser.program()

    print("--- START INTERPRETER ---")
    visitor = LeadInterpreter()
    visitor.visit(tree)
    print("--- END INTERPRETER ---")


if __name__ == '__main__':
    main()