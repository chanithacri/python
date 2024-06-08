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
            return "float division by zero"

    def power(self):
        return self.num_1 ** self.num_2  

    def remainder(self):
        return self.num_1 % self.num_2


def select_op(op):
    try:
        if op == "#":
            return -1
        else:
            num_1 = input("Enter first number: ")
            print(int(num_1))
            num_2 = input("Enter second number: ")
            print(num_2)
            if num_1 or num_2 == "#":
                return -1
                pass
            else:
                num_1 = float(num_1)
                num_2 = float(num_2)
                if op == "+":
                    print(f"{num_1} + {num_2} = {Operations(num_1, num_2).addition()}")
                elif op == "-":
                    print(f"{num_1} - {num_2} = {Operations(num_1, num_2).subtraction()}")
                elif op == "*":
                    print(f"{num_1} * {num_2} = {Operations(num_1, num_2).multiplication()}")
                elif op == "/":
                    if num_1 and num_2 != 0:
                        print(f"{num_1} / {num_2} = {Operations(num_1, num_2).division()}")
                    else:
                        print(Operations(num_1, num_2).division())
                        print(f"{num_1} / {num_2} = None")
                elif op == "^":
                    print(f"{num_1} ^ {num_2} = {Operations(num_1, num_2).power()}")
                elif op == "%":
                    print(f"{num_1} % {num_2} = {Operations(num_1, num_2).remainder()}")
                elif op == "$":
                    pass
                else:
                    print("inalid oparation")
                    pass
    except ValueError:
        pass
   

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
    

    # take input from the user
    choice = input("Enter choice(+,-,*,/,^,%,#,$): ")
    print(choice)
    if(select_op(choice) == -1):
        #program ends here
        print("Done. Terminating")
        exit()
