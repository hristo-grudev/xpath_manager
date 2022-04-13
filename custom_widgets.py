import tkinter as tk
from tkinter.ttk import Label, Button, Checkbutton, Frame, Radiobutton


class MyText(tk.Text):
    def __init__(self, master, tags=None, view=None, *args, **kwargs):
        tk.Text.__init__(self, master, *args, **kwargs)
        self.tags = tags
        self.view = view


class MyLabel(Label):
    def __init__(self, master, tags=None, view=None, *args, **kwargs):
        Label.__init__(self, master, *args, **kwargs)
        self.tags = tags
        self.view = view


class MyButton(Button):
    def __init__(self, master, tags=None, view=None, *args, **kwargs):
        Button.__init__(self, master, *args, **kwargs)
        self.tags = tags
        self.view = view


class MyCheckbutton(Checkbutton):
    def __init__(self, master, tags=None, view=None, *args, **kwargs):
        Checkbutton.__init__(self, master, *args, **kwargs)
        self.tags = tags
        self.view = view


class MyRadiobutton(Radiobutton):
    def __init__(self, master, tags=None, view=None, *args, **kwargs):
        Radiobutton.__init__(self, master, *args, **kwargs)
        self.tags = tags
        self.view = view


class MyFrame(Frame):
    def __init__(self, master, frame_list=None, tags=None, view=None, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)
        self.tags = tags
        self.view = view
        self.frame_list = frame_list
