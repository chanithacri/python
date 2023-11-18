class Calculator:
    def __init__(self, input_str):
        self.input = input_str
        self.result = 0

    def process_input(self):
        while '--' in self.input:
            self.input = self.input.replace('--', '+')
        while '++' in self.input or '+-' in self.input or '-+' in self.input:
            self.input = self.input.replace('++', '+').replace('+-', '-').replace('-+', '-')

    def calculate(self):
        self.process_input()
        try:
            result = eval(self.input)
            return result
        except:
            return "Invalid expression"
        

def process_input():
    print("Calculator is ready. Enter numbers or type '/help' for assistance.")
    while True:
        user_input = input()

        if user_input.startswith("/"):
            if user_input == "/help":
                print("This is a simple calculator. It can handle operations like '+', '-'")
            elif user_input == "/exit":
                print("Bye!")
                break
            else:
                print("Unknown command")
        elif len(user_input.strip()) == 0:
            continue
        else:
            calc = Calculator(user_input)
            result = calc.calculate()
            if isinstance(result, str):
                print(result)
            else:
                print(str(result))


if __name__ == "__main__":
    process_input()
