import turtle
import random
a = int(input())


def random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return (r, g, b)


window = turtle.Screen()
window.bgcolor("black")
window.colormode(255)
draw = turtle.Turtle()
draw.speed(0)  # Setting the speed to 0, which is the fastest

# Draw colorful circle pattern
for i in range(a):
    draw.color(random_color())
    draw.circle(100)
    draw.right(a * 0.1)

turtle.done()
