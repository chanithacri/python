import tkinter as tk


def click(event):
    text = event.widget.cget('text')
    if text == '=':
        try:
            result = str(eval(screen.get()))
            screen.set(result)
        except:
            screen.set('Error')
    elif text == 'C':
        screen.set('')
    elif text == '⌫':
        current_screen = screen.get()
        # Deletes last character
        screen.set(current_screen[:-1])
    else:
        screen.set(screen.get() + text)


root = tk.Tk()
root.geometry('350x400')
root.title('Simple Calculator')

screen = tk.StringVar()

entry = tk.Entry(root, textvar=screen, font="lucida 20 bold")
entry.pack(fill=tk.X, ipadx=8, pady=10, padx=10)

button_frame = tk.Frame(root)
button_frame.pack()

list_of_numbers = ['7', '8', '9', 'C',
                   '4', '5', '6', '⌫',
                   '1', '2', '3', '-',
                   '.', '0', '=', '/',
                   '*', '+']

i = 0
for number in list_of_numbers:
    button = tk.Button(button_frame, text=number, font='lucida 15 bold')
    button.grid(row=int(i/4), column=i%4)
    button.bind('<Button-1>', click)
    i += 1

root.mainloop()