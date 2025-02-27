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


# Example Class for a Cal and parent class
class CalClass:
    def __init__(self, a, b):
        self.value = 0
        self.num_1 = a
        self.num_2 = b
    
    def add(self):
        self.value = self.num_1 + self.num_2
        return self.value
    
    def substarct(self):
        self.value = self.num_1 - self.num_2
        return self.value
    
    def divide(self):
        self.value = self.num_1 / self.num_2
        return self.value
    
    def multipy(self):
        self.value = self.num_1 * self.num_2
        return self.value
    
    # continue for all oparation
# Child clases
class ChildCal(CalClass):  # Child class contains all the finctios and variables of a parent class
    pass


a = int(input("Num 1: "))
b = int(input("Num 2: "))
# Parent class
cal_1 = CalClass(a, b)
print(cal_1.add())
# Chiled class
cal_2 = ChildCal(a, b)
print(cal_2.add())
