import math

# Task 2: Implement functions that perform arithmetic operations
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        print("float division by zero")
        return None

def power(a, b):
    return a ** b

def remainder(a, b):
    try:
        return a % b
    except ZeroDivisionError:
        print("float modulo by zero")
        return None

# Task 1 (Section 2) and Task 3: select_op(choice) function
def select_op(choice):
    if choice == '+':
        num1 = float(input("Enter first number: "))
        num2 = float(input("Enter second number: "))
        result = add(num1, num2)
        print(f"{num1} + {num2} = {result}")
    elif choice == '-':
        num1 = float(input("Enter first number: "))
        num2 = float(input("Enter second number: "))
        result = subtract(num1, num2)
        print(f"{num1} - {num2} = {result}")
    elif choice == '*':
        num1 = float(input("Enter first number: "))
        num2 = float(input("Enter second number: "))
        result = multiply(num1, num2)
        print(f"{num1} * {num2} = {result}")
    elif choice == '/':
        num1 = float(input("Enter first number: "))
        num2 = float(input("Enter second number: "))
        result = divide(num1, num2)
        if result is not None:
            print(f"{num1} / {num2} = {result}")
    elif choice == '^':
        num1 = float(input("Enter first number: "))
        num2 = float(input("Enter second number: "))
        result = power(num1, num2)
        print(f"{num1} ^ {num2} = {result}")
    elif choice == '%':
        num1 = float(input("Enter first number: "))
        num2 = float(input("Enter second number: "))
        result = remainder(num1, num2)
        if result is not None:
            print(f"{num1} % {num2} = {result}")
    elif choice == '#':
        return -1
    elif choice == '$':
        pass  # Reset
    else:
        print("Unrecognized operation")

    return 1

# Task 1 (Section 1): Main loop
while True:
    print("Select operation.")
    print("1.Add : + ")
    print("2.Subtract : - ")
    print("3.Multiply : * ")
    print("4.Divide : / ")
    print("5.Power : ^ ")
    print("6.Remainder: % ")
    print("7.Terminate: # ")
    print("8.Reset : $ ")

    # Take input from the user
    choice = input("Enter choice(+,-,*,/,^,%,#,$): ")

    if select_op(choice) == -1:
        # Program ends here
        print("Done. Terminating")
        exit()