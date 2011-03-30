from turtle import *

def switchupdown(x=0, y=0):
    pen()['pendown'] and not up() or down()

def clear():
    clearscreen()
    init()

def quit():
    bye()

def init():
    onscreenclick(goto,1)
    onscreenclick(switchupdown,3)
    onkey(quit, 'q')
    onkey(clear, 'c')
    listen()

if __name__ == "__main__":
    init()
    mainloop()
