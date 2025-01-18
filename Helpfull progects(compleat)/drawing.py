# RainbowRosettes.py
import turtle
import colorsys
t=turtle.Pen()
turtle.bgcolor('black')
t.speed(0)
t.width(3)
# Ask the user for the number of circles in their rosette, default to 30
number_of_circles = int(turtle.numinput("Number of circles",
                                        "How many circles in your rosette?",30))
for x in range(number_of_circles):
    t.pencolor(colorsys.hsv_to_rgb(x/number_of_circles,1,1) )
    t.circle(150)
    t.left(360/number_of_circles)
    t.right(100)
