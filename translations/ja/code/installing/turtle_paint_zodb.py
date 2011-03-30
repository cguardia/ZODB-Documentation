from turtle import *

import transaction
from ZODB import DB, FileStorage

storage = FileStorage.FileStorage('drawing.fs')
db = DB(storage)
connection = db.open()
drawing = connection.root()

def switchupdown(x=0, y=0):
    pen()['pendown'] and not up() or down()

def redraw(turtle_buffer):
    ops = [turtle_buffer.pop() for i in range(turtle_buffer.nr_of_items())]
    ops.reverse()
    for op in ops:
        if op[0] == 'go':
            up()
            goto(op[1])
            if op[3][0]:
                down()
            goto(op[2])

def clear():
    clearscreen()
    init()

def quit():
    drawing['turtle_buffer'] = getturtle().undobuffer
    transaction.commit()
    bye()

def init():
    onscreenclick(goto,1)
    onscreenclick(switchupdown,3)
    onkey(quit, 'q')
    onkey(clear, 'c')
    listen()

if __name__ == "__main__":
    if 'turtle_buffer' in drawing:
        redraw(drawing['turtle_buffer'])
    init()
    mainloop()
