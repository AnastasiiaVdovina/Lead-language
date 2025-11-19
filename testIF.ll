//оголошення змінних

var a6: float
a6 = 4.0 + 2 * 2 + 3.5

print(a6)

var a7:float
a7 = 2.0 + 2 * 3
print(a7)

var a: int
var b: int = 4
var c: bool = true
a = 1
print(a)

a = input()

for(var i: int = 1; i < 5; i = i + 1){
	a = a * i
	print(a)
}

repeat {
	a = a - 5
	print(a)
}while (a > 0)

while (b > 0) {
    print(b)
	b = b - 1

}

var w: int = 2
var l: int = 5

func area(int width, int length) => int {
    print("Calculate area...")
    return width * length
}


var result: float = area(w, l) * 2.0
print(result)

func sayHello() {
    print("Hi")
}
sayHello()

guard (a > 7) else {
	print("Program executed")
}


var dayOfWeek: int = 4

switch dayOfWeek {
  case 1:
    print("Sunday")
  case 2:
    print("Monday")
  case 3:
    print("Tuesday")
  case 4:
    print("Wednesday")
  case 5:
    print("Thursday")
  case 6:
    print("Friday")
  case 7:
    print("Saturday")
  default:
    print("Invalid day")
}