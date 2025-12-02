import sys
from antlr4 import InputStream, CommonTokenStream  # Явний імпорт
from LeadLexer import LeadLexer
from LeadParser import LeadParser


def main():
    # Ваш тестовий код
    code = """
    //оголошення змінних
var b2: float
var a6: float = 4 + 2 * 2 + 3.5
print(a6)
var a7:float
a7 = 2 + 2 * 3
b2 = 2**2**2
print(a7)
print(b2)

var w: int = 2
var l: int = 5

var x: int = 0
print("Enter x:")
x = input()

if (w<x){
    print("w < x")
} else if (w > x){
    print ("w > x")
} else {
    print("w = x")
}

switch x{
    case 1:
        print("x = 1")
    case 2:
        print("x = 2")
    default:
        print("x = smth else")
}


var age: int = 15
	guard (age >= 18) else {
		print("Accesss denied")
}
print("Access granted")

for(var i: int = 0; i < 5; i= i+1) {
    print(i)
}

var counter: int = 0
while (counter < 10){
    counter = counter + 1
    print(counter)
}


repeat{
	print(counter)
	counter = counter + 1
} while counter < 20


var result: float
result = area(w, l) * 2
var result2: float = 2.0 * area(w, l) + 1
print(result)
print(result2)
    """

    # Створення потоку (InputStream для рядка, FileStream для файлу)
    input_stream = InputStream(code)

    # Лексер
    lexer = LeadLexer(input_stream)

    # Потік токенів (саме тут була помилка)
    stream = CommonTokenStream(lexer)

    # Парсер
    parser = LeadParser(stream)

    # Запуск (program - це назва вашого першого правила в .g4 файлі)
    tree = parser.program()

    # Вивід дерева
    print(tree.toStringTree(recog=parser))


if __name__ == '__main__':
    main()