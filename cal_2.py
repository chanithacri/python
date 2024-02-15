import math


class Calculator:
    def __init__(self):
        self.value = 0

    def add(self, x):
        self.value += x
        return self.value

    def subtract(self, x):
        self.value -= x
        return self.value
    
    def multiply(self, x):
        self.value *= x
        return self.value

    def divide(self, x):
        if x != 0:
           self.value /= x
        else:
            print("Error: Division by zero.")
        return self.value

    def clear(self):
        self.value = 0
        return self.value

    def current_value(self):
        return self.value

    def square(self):
        self.value = self.value**2
        return self.value

    def square_root(self):
        if self.value >= 0:
            self.value = math.sqrt(self.value)
        else:
            print("Error: Negative number.")
        return self.value

    def sin(self):
        self.value = math.sin(self.value)
        return self.value

    def cos(self):
        self.value = math.cos(self.value)
        return self.value

    def tan(self):
        self.value = math.tan(self.value)
        return self.value

    def log(self):
        if self.value > 0:
            self.value = math.log(self.value)
        else:
            print("Error: Non-positive number.")
        return self.value


if __name__ == "__main__":
    cal = Calculator
    