import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image


class ImageCompressor:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Image Compressor")
        self.root.geometry("420x260")
        self.root.resizable(False, False)

        self.image_path = None

        title = tk.Label(
            self.root,
            text="Image Compressor",
            font=("Arial", 18, "bold")
        )

        title.pack(pady=10)

        self.label = tk.Label(
            self.root,
            text="No image selected",
            wraplength=350
        )

        self.label.pack(pady=5)

        browse_btn = tk.Button(
            self.root,
            text="Select Image",
            width=20,
            command=self.select_image
        )

        browse_btn.pack(pady=10)

        quality_label = tk.Label(
            self.root,
            text="Compression Quality (1-100)"
        )

        quality_label.pack()

        self.quality = tk.Scale(
            self.root,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            length=250
        )

        self.quality.set(70)
        self.quality.pack()

        compress_btn = tk.Button(
            self.root,
            text="Compress and Save",
            width=20,
            command=self.compress_image
        )

        compress_btn.pack(pady=15)

        self.root.mainloop()

    def select_image(self):

        path = filedialog.askopenfilename(
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.webp")
            ]
        )

        if path:
            self.image_path = path
            self.label.config(text=os.path.basename(path))

    def compress_image(self):

        if not self.image_path:
            messagebox.showwarning("Warning", "Select an image first.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[
                ("JPEG", "*.jpg"),
                ("PNG", "*.png")
            ]
        )

        if not save_path:
            return

        try:

            img = Image.open(self.image_path)

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            img.save(
                save_path,
                optimize=True,
                quality=self.quality.get()
            )

            original = os.path.getsize(self.image_path)
            compressed = os.path.getsize(save_path)

            reduction = (
                (original - compressed)
                / original
            ) * 100

            messagebox.showinfo(
                "Success",
                f"""Image Saved!

Original Size : {original/1024:.2f} KB
Compressed Size : {compressed/1024:.2f} KB
Reduction : {reduction:.2f}%"""
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )


if __name__ == "__main__":
    ImageCompressor()