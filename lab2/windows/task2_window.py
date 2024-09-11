import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


class Task2Window:
    def __init__(self, root, parent):
        self.root = root
        self.parent = parent
        self.root.configure(bg=parent.back_ground)
        self.root.geometry("230x180+500+20")
        self.root.title("task2")

        print(f"from w2: output path: {self.parent.output_path}")


# image = Image.open("dog.jpg")
# image_array = np.array(image)

# R, G, B = image_array[:, :, 0], image_array[:, :, 1], image_array[:, :, 2]

# R_image = np.zeros_like(image_array)
# G_image = np.zeros_like(image_array)
# B_image = np.zeros_like(image_array)

# R_image[:, :, 0] = R
# G_image[:, :, 1] = G
# B_image[:, :, 2] = B


# Image.fromarray(R_image).save("R_channel.jpg")
# Image.fromarray(G_image).save("G_channel.jpg")
# Image.fromarray(B_image).save("B_channel.jpg")

# fig, axs = plt.subplots(1, 3, figsize=(18, 5))

# axs[0].hist(R.ravel(), bins=256, color="red", alpha=0.6)
# print(axs[0])
# axs[0].set_title("Гистограмма для R-канала")

# axs[1].hist(G.ravel(), bins=256, color="green", alpha=0.6)
# axs[1].set_title("Гистограмма для G-канала")

# axs[2].hist(B.ravel(), bins=256, color="blue", alpha=0.6)
# axs[2].set_title("Гистограмма для B-канала")

# plt.show()
