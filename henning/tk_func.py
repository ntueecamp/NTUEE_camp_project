from tkinter import *
from PIL import Image, ImageTk

def display_logo(url, row, column):
    img = Image.open(url)

    img = img.resize((int(img.size[0]/18),int(img.size[1]/18)))
    img = ImageTk.PhotoImage(img)
    img_label = Label(image=img, bg="white")
    img_label.image = img
    img_label.grid(column=column, row=row, columnspan=5, rowspan=5, sticky=NW, padx=40, pady=40)
