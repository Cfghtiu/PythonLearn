from tkinter import Button, Tk, Entry, StringVar
import ctypes
import sys
kernel32 = ctypes.windll.kernel32


def open_():
    kernel32.AllocConsole()
    sys.stdout = open('CONOUT$', 'w')
    sys.stderr = open('CONOUT$', 'w')
    sys.stdin = open('CONIN$', 'r')


def close():
    kernel32.FreeConsole()
    try:
        sys.stdout.close()
        sys.stderr.close()
        sys.stdin.close()
    except Exception:
        ...


def write(text):
    if not sys.stdout.closed:
        print(text)


close()
root = Tk()
root.title("打开关闭控制台")
root.geometry("270x50")
var = StringVar()
Entry(root, textvariable=var).grid(columnspan=3)
Button(text="写入", command=lambda: write(var.get())).grid(row=1, column=0)
Button(text="打开", command=open_).grid(row=1, column=1)
Button(text="关闭", command=close).grid(row=1, column=2)
root.mainloop()
