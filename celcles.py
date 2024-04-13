import turtle
num = int(input())
turtle.bgcolor("Black")
t = turtle.pen()
for i in range(num):
    t.left(360 / num)
    