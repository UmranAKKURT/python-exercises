import os
import tkinter as tk
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Sürükle Bırak Desteği için (Opsiyonel)
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES

    HAS_DND = True


    # ttkbootstrap Window'u ve TkinterDnD Wrapper'ı birleştiren özel sınıf
    class CustomWindow(ttk.Window, TkinterDnD.DnDWrapper):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.TkdndVersion = TkinterDnD._require(self)
except ImportError:
    HAS_DND = False
    CustomWindow = ttk.Window

from compressor import ImageCompressor

# utils.py modülünden projenizde yazılmış tüm gerekli fonksiyonları dahil ediyoruz
from utils import (
    create_thumbnail,
    file_size,
    readable_size,
    image_resolution,
    validate_image,
    save_history,
    create_history_item,
    load_history,
    clear_history,
    unique_filename
)


class ImageCompressorApp:

    def __init__(self):
        self.compressor = ImageCompressor()
        self.input_path = None
        self.output_path = None

        # DnD destekli (veya normal) ana pencereyi oluştur
        self.root = CustomWindow(
            title="Image Compressor",
            themename="darkly",
            size=(1150, 750),
            resizable=(False, False)
        )

        self.build_ui()
        self.setup_dnd()

    def run(self):
        self.root.mainloop()

    def build_ui(self):
        self.create_topbar()
        self.create_preview_area()
        self.create_controls()
        self.create_statusbar()

    def setup_dnd(self):
        if HAS_DND:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.handle_drop)
        else:
            self.status.configure(text="Ready (Install 'tkinterdnd2' for Drag & Drop support)")

    ####################################################
    # 1. ARAYÜZ (UI) OLUŞTURMA
    ####################################################

    def create_topbar(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=X)

        title = ttk.Label(
            frame,
            text="Image Compressor",
            font=("Segoe UI", 20, "bold")
        )
        title.pack(side=LEFT)

        ttk.Button(
            frame,
            text="📊 Statistics",
            bootstyle="info-outline",
            command=self.show_statistics
        ).pack(side=LEFT, padx=15)

        ttk.Button(
            frame,
            text="Light",
            bootstyle=INFO,
            command=lambda: self.change_theme("flatly")
        ).pack(side=RIGHT, padx=5)

        ttk.Button(
            frame,
            text="Dark",
            bootstyle=SECONDARY,
            command=lambda: self.change_theme("darkly")
        ).pack(side=RIGHT)

    def create_preview_area(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill=BOTH, expand=True, padx=15)

        self.before_frame = ttk.Labelframe(
            frame,
            text="Original Image (Drag & Drop Here)",
            padding=10
        )
        self.before_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10)

        self.after_frame = ttk.Labelframe(
            frame,
            text="Compressed Image",
            padding=10
        )
        self.after_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10)

        self.before_image = ttk.Label(self.before_frame, text="No Image")
        self.before_image.pack(expand=True)

        self.after_image = ttk.Label(self.after_frame, text="Compressed Preview")
        self.after_image.pack(expand=True)

    def create_controls(self):
        frame = ttk.Frame(self.root, padding=15)
        frame.pack(fill=X)

        ttk.Button(
            frame,
            text="Select Image",
            bootstyle=PRIMARY,
            command=self.select_image
        ).grid(row=0, column=0, padx=10)

        ttk.Button(
            frame,
            text="Compress",
            bootstyle=SUCCESS,
            command=self.compress_image
        ).grid(row=0, column=1, padx=10)

        ttk.Button(
            frame,
            text="Batch Compress",
            bootstyle=WARNING,
            command=self.batch_compress
        ).grid(row=0, column=2, padx=10)

        self.smart_var = tk.BooleanVar(value=False)
        self.smart_switch = ttk.Checkbutton(
            frame,
            text="Smart Mode",
            variable=self.smart_var,
            bootstyle="success-round-toggle",
            command=self.toggle_smart_mode
        )
        self.smart_switch.grid(row=0, column=3, padx=(20, 10))

        ttk.Label(frame, text="Quality").grid(row=0, column=4, padx=(10, 0))

        self.quality = ttk.Scale(
            frame,
            from_=1,
            to=100,
            orient=HORIZONTAL,
            command=self.slider_changed,
            length=180
        )
        self.quality.set(80)
        self.quality.grid(row=0, column=5, padx=10)

        self.quality_label = ttk.Label(frame, text="80%")
        self.quality_label.grid(row=0, column=6)

        self.info = ttk.Label(
            frame,
            text="Choose an image or drop it here...",
            font=("Segoe UI", 10)
        )
        self.info.grid(row=1, column=0, columnspan=7, pady=15, sticky=W, padx=10)

    def create_statusbar(self):
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=X, side=BOTTOM, padx=10, pady=5)

        self.status = ttk.Label(status_frame, text="Ready", anchor=W)
        self.status.pack(side=LEFT, fill=X, expand=True)

        self.progress = ttk.Progressbar(
            status_frame,
            mode='determinate',
            length=250,
            bootstyle=SUCCESS
        )
        self.progress.pack(side=RIGHT, padx=10)

    ####################################################
    # 2. YARDIMCI FONKSİYONLAR
    ####################################################

    def change_theme(self, theme):
        self.root.style.theme_use(theme)

    def slider_changed(self, value):
        if not self.smart_var.get():
            value = int(float(value))
            self.quality_label.configure(text=f"{value}%")

    def toggle_smart_mode(self):
        if self.smart_var.get():
            self.quality.state(['disabled'])
            self.quality_label.configure(text="Auto")
        else:
            self.quality.state(['!disabled'])
            self.slider_changed(self.quality.get())

    def get_smart_quality(self, file_path):
        size_bytes = file_size(file_path)
        mb = size_bytes / (1024 * 1024)
        if mb > 5:
            return 50
        elif mb > 2:
            return 60
        elif mb > 1:
            return 75
        else:
            return 85

    def handle_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = files[0]
            if validate_image(file_path):
                self.load_image_to_ui(file_path)
            else:
                messagebox.showerror("Error", "Unsupported image file format.")

    ####################################################
    # 3. İŞLEMLER (SEÇME, YÜKLEME & SIKIŞTIRMA)
    ####################################################

    def load_image_to_ui(self, filename):
        self.input_path = filename
        thumb = create_thumbnail(filename)
        self.before_image.configure(image=thumb, text="")
        self.before_image.image = thumb
        self.after_image.configure(image='', text="Compressed Preview")
        self.after_image.image = None

        width, height = image_resolution(filename)
        orig_size = readable_size(file_size(filename))

        self.info.configure(
            text=f"File : {os.path.basename(filename)}\nResolution : {width} x {height}\nOriginal Size : {orig_size}"
        )
        self.status.configure(text="Image Loaded Successfully")
        self.progress['value'] = 0

    def select_image(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp")]
        )
        if filename and validate_image(filename):
            self.load_image_to_ui(filename)
        elif filename:
            messagebox.showerror("Error", "Unsupported image.")

    def compress_image(self):
        if not self.input_path:
            messagebox.showwarning("Warning", "Please select or drop an image first.")
            return

        ext = os.path.splitext(self.input_path)[1]

        # Orijinal dosyanın bulunduğu dizini ve önerilen ismi alıp,
        # benzersiz bir isim ile varsayılan olarak sunuyoruz (unique_filename kullanarak)
        suggested_out_path = unique_filename(
            os.path.join(os.path.dirname(self.input_path), f"compressed_{os.path.basename(self.input_path)}")
        )

        out_path = filedialog.asksaveasfilename(
            initialfile=os.path.basename(suggested_out_path),
            defaultextension=ext,
            filetypes=[("Image File", f"*{ext}"), ("All Files", "*.*")],
            title="Save Compressed Image"
        )

        if not out_path:
            return

        self.output_path = out_path

        if self.smart_var.get():
            quality = self.get_smart_quality(self.input_path)
        else:
            quality = int(float(self.quality.get()))

        self.status.configure(text=f"Compressing... (Quality: {quality})")
        self.progress.start(15)
        self.root.update()

        try:
            self.compressor.compress(self.input_path, self.output_path, quality=quality)
            orig_size = file_size(self.input_path)
            comp_size = file_size(self.output_path)
            ratio = 100 - ((comp_size / orig_size) * 100) if orig_size > 0 else 0

            thumb = create_thumbnail(self.output_path)
            self.after_image.configure(image=thumb, text="")
            self.after_image.image = thumb

            current_info = self.info.cget("text").split("\nCompressed Size:")[0]
            new_info = (
                    current_info +
                    f"\nCompressed Size: {readable_size(comp_size)} (Quality: {quality})" +
                    f"\nSpace Saved: %{ratio:.2f}"
            )
            self.info.configure(text=new_info)

            # utils.py modülünü kullanarak kaydediyoruz
            history_record = create_history_item(self.input_path, orig_size, comp_size, ratio)
            save_history(history_record)

            self.status.configure(text=f"Compression successful! Saved %{ratio:.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self.status.configure(text="Error occurred.")
        finally:
            self.progress.stop()
            self.progress['value'] = 100

    def batch_compress(self):
        files = filedialog.askopenfilenames(
            title="Select Multiple Images",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp")]
        )
        if not files: return
        out_dir = filedialog.askdirectory(title="Select Output Folder")
        if not out_dir: return

        total_files = len(files)
        success_count = 0
        total_saved_bytes = 0

        self.progress['mode'] = 'determinate'
        self.progress['maximum'] = total_files
        self.progress['value'] = 0

        for i, file_path in enumerate(files):
            filename = os.path.basename(file_path)

            # utils modülündeki unique_filename kullanılarak üzerine yazma engelleniyor
            out_path = unique_filename(os.path.join(out_dir, f"compressed_{filename}"))

            if self.smart_var.get():
                quality = self.get_smart_quality(file_path)
            else:
                quality = int(float(self.quality.get()))

            self.status.configure(text=f"Batch Compressing ({i + 1}/{total_files}): {filename}")
            self.root.update()

            if validate_image(file_path):
                try:
                    self.compressor.compress(file_path, out_path, quality=quality)
                    orig_size = file_size(file_path)
                    comp_size = file_size(out_path)
                    ratio = 100 - ((comp_size / orig_size) * 100) if orig_size > 0 else 0
                    total_saved_bytes += (orig_size - comp_size)

                    # utils.py üzerinden kayıt gerçekleştirme
                    history_record = create_history_item(file_path, orig_size, comp_size, ratio)
                    save_history(history_record)

                    success_count += 1
                except Exception as e:
                    print(f"Error compressing {file_path}: {e}")

            self.progress['value'] = i + 1
            self.root.update()

        saved_str = readable_size(max(0, total_saved_bytes))
        self.status.configure(text=f"Batch Completed. ({success_count}/{total_files}) - Total Saved: {saved_str}")
        messagebox.showinfo("Done",
                            f"Batch compression finished.\nSuccess: {success_count}/{total_files}\nTotal Space Saved: {saved_str}")

    ####################################################
    # 4. İSTATİSTİKLER PENCERESİ (STATISTICS)
    ####################################################

    def show_statistics(self):
        """utils.py içindeki history verilerini kullanarak arayüzü doldurur."""
        stats_window = ttk.Toplevel(self.root)
        stats_window.title("Compression Statistics")
        stats_window.geometry("400x380")  # Butonların sığması için biraz yükseltildi
        stats_window.resizable(False, False)

        history_data = load_history()
        total_files = len(history_data)

        total_orig_size = sum(item.get("original", 0) for item in history_data)
        total_comp_size = sum(item.get("compressed", 0) for item in history_data)
        total_saved = sum(item.get("saved", 0) for item in history_data)

        ttk.Label(stats_window, text="App Statistics", font=("Segoe UI", 16, "bold")).pack(pady=20)
        data_frame = ttk.Frame(stats_window)
        data_frame.pack(fill=X, padx=40, pady=10)

        ttk.Label(data_frame, text="Total Files Compressed:", font=("Segoe UI", 11)).grid(row=0, column=0, sticky=W,
                                                                                          pady=5)
        ttk.Label(data_frame, text=str(total_files), font=("Segoe UI", 11, "bold")).grid(row=0, column=1, sticky=E,
                                                                                         pady=5)

        ttk.Label(data_frame, text="Original Total Size:", font=("Segoe UI", 11)).grid(row=1, column=0, sticky=W,
                                                                                       pady=5)
        ttk.Label(data_frame, text=readable_size(total_orig_size), font=("Segoe UI", 11, "bold")).grid(row=1, column=1,
                                                                                                       sticky=E, pady=5)

        ttk.Label(data_frame, text="Compressed Total Size:", font=("Segoe UI", 11)).grid(row=2, column=0, sticky=W,
                                                                                         pady=5)
        ttk.Label(data_frame, text=readable_size(total_comp_size), font=("Segoe UI", 11, "bold")).grid(row=2, column=1,
                                                                                                       sticky=E, pady=5)

        ttk.Separator(data_frame, orient=HORIZONTAL).grid(row=3, column=0, columnspan=2, sticky=EW, pady=10)

        ttk.Label(data_frame, text="Total Space Saved:", font=("Segoe UI", 12, "bold"), bootstyle=SUCCESS).grid(row=4,
                                                                                                                column=0,
                                                                                                                sticky=W,
                                                                                                                pady=5)
        ttk.Label(data_frame, text=readable_size(total_saved), font=("Segoe UI", 12, "bold"), bootstyle=SUCCESS).grid(
            row=4, column=1, sticky=E, pady=5)

        # Temizleme ve Kapatma Butonları
        def on_clear():
            if messagebox.askyesno("Confirm", "Are you sure you want to clear all history?"):
                clear_history()
                stats_window.destroy()
                messagebox.showinfo("Success", "History cleared successfully.")

        button_frame = ttk.Frame(stats_window)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Clear History", command=on_clear, bootstyle=DANGER).pack(side=LEFT, padx=10)
        ttk.Button(button_frame, text="Close", command=stats_window.destroy, bootstyle=SECONDARY).pack(side=LEFT,
                                                                                                       padx=10)


if __name__ == "__main__":
    app = ImageCompressorApp()
    app.run()