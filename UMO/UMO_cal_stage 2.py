to_remember = []


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
        if self.num_2 != 0:
            return self.num_1 / self.num_2
        else:
            return "float division by zero \n{num_1} / {num_2} = None".format(num_1=self.num_1, num_2=self.num_2)

    def power(self):
        return self.num_1 ** self.num_2  

    def remainder(self):
        if self.num_2 != 0:
            return self.num_1 % self.num_2
        else:
            return "Error: Division by zero"


def get_num():
    num_1 = input("Enter first number: ")
    print(num_1)
    if num_1 == '#':
        return -1
    if "$" in num_1:
        return None
        pass
    num_2 = input("Enter second number: ")
    print(num_2)
    if num_2 == '#':
        return -1
    if "$" in num_2:
        return None
        pass
    try:
        num_1 = float(num_1)
        num_2 = float(num_2)
        return num_1, num_2
    except ValueError:
        if "$" or "#" in num_1 or num_2:
            return None
        else:
            print("Invalid input. Please enter numeric values.")
            return None


def select_op(op,to_remember):
    if op == "#":
        return -1
    nums = get_num()
    if nums == -1:
        return -1
    if nums is None:
        return 0
    num_1, num_2 = nums
    operation = Operations(num_1, num_2)
    if op == "+":
        a = f"{num_1} + {num_2} = {operation.addition()}"
        print(a)
        to_remember.append(a)
    elif op == "-":
        b = f"{num_1} - {num_2} = {operation.subtraction()}"
        print(b)
        to_remember.append(b)
    elif op == "*":
        c = f"{num_1} * {num_2} = {operation.multiplication()}"
        print(c)
        to_remember.append(c)
    elif op == "/":
        result = operation.division()
        if isinstance(result, str):
            print(result)
            to_remember.append(f"{num_1} / {num_2} = None")
        else:
            d = f"{num_1} / {num_2} = {result}"
            print(d)
            to_remember.append(d)
    elif op == "^":
        e = f"{num_1} ^ {num_2} = {operation.power()}"
        print(e)
        to_remember.append(e)
    elif op == "%":
        result = operation.remainder()
        if isinstance(result, str):
            print(result)
            to_remember.append(result)
        else:
            f = f"{num_1} % {num_2} = {result}"
            print(f)
            to_remember.append(f)
    elif op == "$":
        pass
    else:
        print("Invalid operation")
    return 0


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
    print("8.History  : ?")

    choice = input("Enter choice(+,-,*,/,^,%,#,$,?): ")
    print(choice)
    if choice == "?":
        if len(to_remember) == 0:
            print("No past calculations to show")
            continue
        else:
            for x in to_remember:
                print(x)
            continue
    if select_op(choice, to_remember) == -1:
        print("Done. Terminating")
        exit()
