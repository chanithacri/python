import math


class Calculator:
    def __init__(self):
        self.value = 0

    def add(self, x, y):
        self.value = x + y
        return self.value

    def subtract(self, x, y):
        self.value = x - y
        return self.value

    def multiply(self, x, y):
        self.value = x * y
        return self.value

    def divide(self, x, y):
        if y != 0:
           self.value = x / y
        else:
            print("Error: Division by zero.")
        return self.value
    
    def power(self, x ,y):
        self.value = x ** y
        return self.value 

    def clear(self):
        self.value = 0
        return self.value

    def current_value(self):
        return self.value

    def square(self, x):
        self.value = x**2
        return self.value

    def square_root(self, x):
        if x >= 0:
            self.value = math.sqrt(x)
        else:
            print("Error: Negative number.")
        return self.value

    def sin(self, x):
        self.value = math.sin(x)
        return self.value

    def cos(self, x):
        self.value = math.cos(x)
        return self.value

    def tan(self, x):
        self.value = math.tan(x)
        return self.value

    def log(self, x):
        if x > 0:
            self.value = math.log(x)
        else:
            print("Error: Non-positive number.")
        return self.value


if __name__ == "__main__":
    calculator = Calculator()
    print("Welcome back!")
    while True:
        user_input = input("Enter operation and 2 numbers exept for sin,cos,tan,log,clear,squer and saqurroot. Type "
                           "'exit' to exit: ")
        if user_input == "exit":
            print("Bye!")
            print("Hope to see you soon!")
            break
        
        user_input_lst = user_input.split(" ")
        operation = user_input_lst[0]

        if operation == "+":
            n1 = float(user_input_lst[1])
            n2 = float(user_input_lst[2])
            print(calculator.add(n1, n2))

        elif operation == "-":
            n1 = float(user_input_lst[1])
            n2 = float(user_input_lst[2])
            print(calculator.subtract(n1, n2))

        elif operation == "*":
            n1 = float(user_input_lst[1])
            n2 = float(user_input_lst[2])
            print(calculator.multiply(n1, n2))

        elif operation == "/":
            n1 = float(user_input_lst[1])
            n2 = float(user_input_lst[2])
            print(calculator.divide(n1, n2))

        elif operation == "**":
            n1 = float(user_input_lst[1])
            n2 = float(user_input_lst[2])
            print(calculator.power(n1, n2))

        elif operation == "clear":
            print(calculator.clear())

        elif operation == "square":
            n1 = float(user_input_lst[1])
            print(calculator.square(n1))

        elif operation == "square_root":
            n1 = float(user_input_lst[1])
            print(calculator.square_root(n1))

        elif operation == "sin":
            n1 = float(user_input_lst[1])
            print(calculator.sin(n1))

        elif operation == "cos":
            n1 = float(user_input_lst[1])
            print(calculator.cos(n1))

        elif operation == "tan":
            n1 = float(user_input_lst[1])
            print(calculator.tan(n1))

        elif operation == "log":
            n1 = float(user_input_lst[1])
            print(calculator.log(n1))

        else:
            print("Invalid operation!")
