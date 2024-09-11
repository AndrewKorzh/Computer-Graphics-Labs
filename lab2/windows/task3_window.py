import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


class Task3Window:
    def __init__(self, root: tk.Tk, parent):
        self.root = root
        self.parent = parent
        self.root.configure(bg=parent.back_ground)
        self.root.geometry("230x180+500+20")
        self.root.title("task3")
