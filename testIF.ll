//оголошення змінних
var b2: float
var a6: float
a6 = 4 + 2 * 2 + 3.5
print(a6)
var a7:float
a7 = 2 + 2 * 3
b2 = 2**2**2
print(a7)
print(b2)
var a: int
var b: int = 4
var c: bool = true

var w: int = 2
var l: int = 5

func area(int width, int length) => int {
    print("Calculate area...")
    return width * length
}


var result: float = area(w, l) * 2
var result2: float = 2 * area(w, l)+ 1
print(result)
print(result2)