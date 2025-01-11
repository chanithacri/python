class Operations:
    def __init__(self, num_1, num_2):
        self.num_1 = num_1
        self.num_2 = num_2

    def addition(self):
        return self.num_1 + self.num_2

    def subtraction(self):
        return self.num_1 - self.num_2

    def multiplication(self):
        return self.num_1 * self.num_2

    def division(self):
        if self.num_2 != 0 and self.num_1:
            return self.num_1 / self.num_2
        else:
            return f"self.num_1 / self.num_2 \n float division by zero"

    def power(self):
        return self.num_1 ** self.num_2  

    def remainder(self):
        return self.num_1 % self.num_2


def get_num():
    num_1 = input("Enter first number: ")
    print(num_1)
    num_2 = input("Enter second number: ")
    print(num_2)
    if num_1 == '#' or num_2 == '#':
        return -1
    if num_1.isdecimal() and num_2.isdecimal():
        return float(num_1), float(num_2)


def select_op(op):
    try:
        if op == "#":
            return -1
        else:
            num_1 , num_2 = get_num()
            if op == "+":
                print(f"{num_1} + {num_2} = {Operations(num_1, num_2).addition()}")
            elif op == "-":
                print(f"{num_1} - {num_2} = {Operations(num_1, num_2).subtraction()}")
            elif op == "*":
                print(f"{num_1} * {num_2} = {Operations(num_1, num_2).multiplication()}")
            elif op == "/":
                if num_1 != 0 and num_2 != 0:
                    print(f"{num_1} / {num_2} = {Operations(num_1, num_2).division()}")
                else:
                    print("float division by zero")
                    print(f"{num_1} / {num_2} = None")
            elif op == "^":
                print(f"{num_1} ^ {num_2} = {Operations(num_1, num_2).power()}")
            elif op == "%":
                print(f"{num_1} % {num_2} = {Operations(num_1, num_2).remainder()}")
            elif op == "$":
                # whatever you want to do when op == "$"
                pass
            else:
                print("Invalid operation")
    except ValueError:
        pass
    except ZeroDivisionError as e:
        print(e)


while True:
    print("Select operation.")
    print("1.Add      : + ")
    print("2.Subtract : - ")
    print("3.Multiply : * ")
    print("4.Divide   : / ")
    print("5.Power    : ^ ")
    print("6.Remainder: % ")
    print("7.Terminate: # ")
    print("8.Reset    : $ ")

    choice = input("Enter choice(+,-,*,/,^,%,#,$): ")
    print(choice)
    if(select_op(choice) == -1):
        print("Done. Terminating")
        break
