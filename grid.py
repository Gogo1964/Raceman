'''Example of how to use the grid() method to create a GUI layout'''
from tkinter import *

root  =  Tk()  # create root window
root.title("Basic GUI Layout with Grid")
root.maxsize(800, 480)  # width x height
root.geometry("800x480")
root.config(bg="skyblue")

# Create left and right frames
left_frame  =  Frame(root,  width=20,  height=400,  bg='red')
left_frame.grid(row=0,  column=0,  padx=10,  pady=5)

right_frame  =  Frame(root,  width=200,  height=400,  bg='blue')
right_frame.grid(row=0,  column=1,  padx=10,  pady=5)

# Create frames and labels in left_frame
Label(left_frame,  text="Original Image",  relief=RAISED).grid(row=0,  column=0,  padx=5,  pady=5)
image  =  PhotoImage(file="025.gif")  # edit the file name to use a different image
original_image  =  image.subsample(3,3)

Label(left_frame,  image=original_image).grid(row=1,  column=0,  padx=5,  pady=5)
Label(right_frame,  image=image,  bg='grey').grid(row=0,  column=0,  padx=5,  pady=5)

tool_bar  =  Frame(left_frame,  width=180,  height=185,  bg='grey')
tool_bar.grid(row=2,  column=0,  padx=5,  pady=5)

def clicked():
    '''if button is clicked, display message'''
    print("Clicked.")

# Example labels that serve as placeholders for other widgets
Label(tool_bar,  text="Tools",  relief=RAISED).grid(row=0,  column=0,  padx=5,  pady=3,  ipadx=10)
Label(tool_bar,  text="Filters",  relief=RAISED).grid(row=0,  column=1,  padx=5,  pady=3,  ipadx=10)

# For now, when the buttons are clicked, they only call the clicked() method. We will add functionality later.
Button(tool_bar,  text="Select",  command=clicked).grid(row=1,  column=0,  padx=5,  pady=5,  sticky='w'+'e'+'n'+'s')
Button(tool_bar,  text="Crop",  command=clicked).grid(row=2,  column=0,  padx=5,  pady=5,  sticky='w'+'e'+'n'+'s')
Button(tool_bar,  text="Rotate &amp; Flip",  command=clicked).grid(row=3,  column=0,  padx=5,  pady=5,  sticky='w'+'e'+'n'+'s')
Button(tool_bar,  text="Resize",  command=clicked).grid(row=4,  column=0,  padx=5,  pady=5,  sticky='w'+'e'+'n'+'s')
Button(tool_bar,  text="Black &amp; White",  command=clicked).grid(row=1,  column=1,  padx=5,  pady=5,  sticky='w'+'e'+'n'+'s')
root.mainloop()
