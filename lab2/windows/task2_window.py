import os
import tkinter as tk
import numpy as np

from PIL import Image
import matplotlib.pyplot as plt


# Сделать отдельные функции а не использовать встроенные


class Task2Window:
    def __init__(self, root: tk.Tk, parent):
        self.root = root
        self.parent = parent
        self.root.configure(bg=parent.back_ground)
        self.root.geometry("230x40+500+20")
        self.root.title("task2")

        self.start_button = tk.Button(
            root,
            text="start",
            command=self.start,
            width=20,
            bg="#555",
            fg="white",
        )
        self.root.grid_columnconfigure(0, weight=1)

        self.start_button.grid(
            row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
        )

    def start(self):
        print(f"Output path: {self.parent.output_path}")
        print(f"Image: {self.parent.path_entry.get()}")
        image = Image.open(self.parent.path_entry.get())
        image_array = np.array(image)

        R, G, B = image_array[:, :, 0], image_array[:, :, 1], image_array[:, :, 2]

        R_image = np.zeros_like(image_array)
        G_image = np.zeros_like(image_array)
        B_image = np.zeros_like(image_array)

        R_image[:, :, 0] = R
        G_image[:, :, 1] = G
        B_image[:, :, 2] = B

        Image.fromarray(R_image).save(
            os.path.join(self.parent.output_path, "R_channel.jpg")
        )
        Image.fromarray(G_image).save(
            os.path.join(self.parent.output_path, "G_channel.jpg")
        )
        Image.fromarray(B_image).save(
            os.path.join(self.parent.output_path, "B_channel.jpg")
        )

        fig, axs = plt.subplots(1, 3, figsize=(18, 5))

        axs[0].hist(R.ravel(), bins=256, color="red", alpha=0.6)
        print(axs[0])
        axs[0].set_title("hexagram for R-сhanel")

        axs[1].hist(G.ravel(), bins=256, color="green", alpha=0.6)
        axs[1].set_title("hexagram for G-сhanel")

        axs[2].hist(B.ravel(), bins=256, color="blue", alpha=0.6)
        axs[2].set_title("hexagram for B-сhanel")

        plt.show()
        return
