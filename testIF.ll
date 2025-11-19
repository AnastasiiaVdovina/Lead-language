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

func area(int width, int length) => int {
    print("Calculate area...")
    return width * length
}


var result: float
result = area(w, l) * 2
var result2: float = 2.0 * area(w, l) + 1
print(result)
print(result2)