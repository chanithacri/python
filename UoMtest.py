def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "float division by zero"
    return a / b

def power(a, b):
    return a ** b

def remainder(a, b):
    return a % b

def select_op(choice):
    if choice == '+':
        return add
    elif choice == '-':
        return subtract
    elif choice == '*':
        return multiply
    elif choice == '/':
        return divide
    elif choice == '^':
        return power
    elif choice == '%':
        return remainder
    elif choice == '$':
        return None
    elif choice == '#':
        return "terminate"
    else:
        return "unrecognized operation"

def calculator():
    while True:
        print("#Select operation.")
        print("1.Add      : +")
        print("2.Subtract : -")
        print("3.Multiply : *")
        print("4.Divide   : /")
        print("5.Power    : ^")
        print("6.Remainder: %")
        print("7.Terminate: #")
        print("8.Reset    : $")

        choice = input("Enter choice(+,-,*,/,^,%,#,$): ")

        if choice == '#':
            print("\nDone. Terminating")
            break

        operation = select_op(choice)

        if operation == "terminate":
            print("\nDone. Terminating")
            break
        elif operation == "unrecognized operation":
            print("Unrecognized operation")
        elif operation is None:
            continue

        try:
            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))
        except ValueError:
            print("Not a valid number, please enter again")
            continue

        result = operation(num1, num2)
        print(f"{num1} {choice} {num2} = {result}")

calculator()
