# Tpical class in python 
class ExampleClass:  # CamelCase
    def __inint__(self ,input_1, input_n):
        self.input_1 = input_1
        self.input_n = input_n
    
    def func_1(self):
        pass

    def func_2(self):
        a = self.input_1
        b = self.input_n


# Example Class for a Cal 
class CalClass:
    def __init__(self, a, b):
        self.value = 0
        self.num_1 = a
        self.num_2 = b
    
    def add(self):
        self.value = self.num_1 + self.num_2
    
    def substarct(self):
        self.value = self.num_1 - self.num_2
    
    def divide(self):
        self.value = self.num_1 / self.num_2
    
    def multipy(self):
        self.value = self.num_1 * self.num_2
    
    # continue for all oparation
    