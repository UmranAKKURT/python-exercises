import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Sürükle Bırak Desteği için (Opsiyonel)
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES

    HAS_DND = True


    class CustomWindow(ttk.Window, TkinterDnD.DnDWrapper):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.TkdndVersion = TkinterDnD._require(self)
except ImportError:
    HAS_DND = False
    CustomWindow = ttk.Window

from compressor import ImageCompressor
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

        self.root = CustomWindow(
            title="Image Compressor",
            themename="darkly",
            size=(1150, 780),
            resizable=(False, False)
        )

        self.build_ui()
        self.setup_dnd()

    def run(self):
        self.root.mainloop()

    def build_ui(self):
        self.create_topbar()
        ttk.Separator(self.root).pack(fill=X, padx=15)
        self.create_preview_area()
        self.create_controls()
        ttk.Separator(self.root).pack(fill=X, padx=15, pady=(10, 0))
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
        frame = ttk.Frame(self.root, padding=(15, 15, 15, 10))
        frame.pack(fill=X)

        title = ttk.Label(frame, text="🖼️ Image Compressor", font=("Segoe UI", 22, "bold"))
        title.pack(side=LEFT)

        ttk.Button(
            frame, text="📊 Statistics", bootstyle="info-outline", command=self.show_statistics
        ).pack(side=LEFT, padx=25)

        theme_frame = ttk.Frame(frame)
        theme_frame.pack(side=RIGHT)

        ttk.Button(
            theme_frame, text="☀️ Light", bootstyle=INFO, command=lambda: self.change_theme("cosmo")
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            theme_frame, text="🌙 Dark", bootstyle=SECONDARY, command=lambda: self.change_theme("darkly")
        ).pack(side=LEFT)

    def create_preview_area(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill=BOTH, expand=True, padx=15, pady=15)

        self.before_frame = ttk.Labelframe(frame, text=" Original Image ", padding=10, bootstyle=INFO)
        self.before_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        self.after_frame = ttk.Labelframe(frame, text=" Compressed Image ", padding=10, bootstyle=SUCCESS)
        self.after_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=(10, 0))

        self.before_image = ttk.Label(
            self.before_frame,
            text="📥\nDrag & Drop Image Here\n— or Click to Browse —",
            font=("Segoe UI", 13), justify=CENTER, foreground="gray", cursor="hand2"
        )
        self.before_image.pack(expand=True)
        # Resim yoksa seçtir, varsa zoom yap
        self.before_image.bind("<Button-1>",
                               lambda e: self.select_image() if not self.input_path else self.show_image_preview(
                                   self.input_path, "Original Image"))

        self.after_image = ttk.Label(
            self.after_frame,
            text="✨\nCompressed Preview",
            font=("Segoe UI", 13), justify=CENTER, foreground="gray"
        )
        self.after_image.pack(expand=True)

    def create_controls(self):
        main_control_frame = ttk.Frame(self.root, padding=(15, 10))
        main_control_frame.pack(fill=X)
        main_control_frame.columnconfigure(0, weight=0)
        main_control_frame.columnconfigure(1, weight=0)
        main_control_frame.columnconfigure(2, weight=1)

        # 1. ACTIONS FRAME
        actions_frame = ttk.Labelframe(main_control_frame, text=" 🛠️ Actions ", padding=15)
        actions_frame.grid(row=0, column=0, sticky=NSEW, padx=(0, 10))

        ttk.Button(actions_frame, text="📁 Select", bootstyle=PRIMARY, command=self.select_image).pack(side=LEFT, padx=5,
                                                                                                      fill=X,
                                                                                                      expand=True)
        ttk.Button(actions_frame, text="✨ Compress", bootstyle=SUCCESS, command=self.compress_image).pack(side=LEFT,
                                                                                                          padx=5,
                                                                                                          fill=X,
                                                                                                          expand=True)
        ttk.Button(actions_frame, text="📦 Batch", bootstyle=WARNING, command=self.batch_compress).pack(side=LEFT,
                                                                                                       padx=5, fill=X,
                                                                                                       expand=True)

        # 2. SETTINGS FRAME (Format, EXIF ve Kalite eklendi)
        settings_frame = ttk.Labelframe(main_control_frame, text=" ⚙️ Settings ", padding=10)
        settings_frame.grid(row=0, column=1, sticky=NSEW, padx=10)

        # Üst Satır: Toggles
        toggles_frame = ttk.Frame(settings_frame)
        toggles_frame.pack(fill=X, pady=(0, 5))

        self.smart_var = tk.BooleanVar(value=False)
        self.smart_switch = ttk.Checkbutton(toggles_frame, text="Smart Mode", variable=self.smart_var,
                                            bootstyle="success-round-toggle", command=self.toggle_smart_mode)
        self.smart_switch.pack(side=LEFT, padx=(0, 15))

        self.exif_var = tk.BooleanVar(value=True)
        self.exif_switch = ttk.Checkbutton(toggles_frame, text="Keep EXIF", variable=self.exif_var,
                                           bootstyle="info-round-toggle")
        self.exif_switch.pack(side=LEFT)

        ttk.Separator(settings_frame, orient=HORIZONTAL).pack(fill=X, pady=5)

        # Alt Satır: Format ve Slider
        bottom_settings = ttk.Frame(settings_frame)
        bottom_settings.pack(fill=X)

        ttk.Label(bottom_settings, text="Format:").pack(side=LEFT)
        self.format_var = tk.StringVar(value="Original")
        self.format_cb = ttk.Combobox(bottom_settings, textvariable=self.format_var,
                                      values=["Original", "JPG", "PNG", "WEBP"], state="readonly", width=8)
        self.format_cb.pack(side=LEFT, padx=(5, 15))

        ttk.Label(bottom_settings, text="Quality:").pack(side=LEFT, padx=(0, 5))
        self.quality_label = ttk.Label(bottom_settings, text="80%", font=("Segoe UI", 11, "bold"), width=4)
        self.quality = ttk.Scale(bottom_settings, from_=1, to=100, orient=HORIZONTAL, command=self.slider_changed,
                                 length=100)
        self.quality.set(80)

        self.quality.pack(side=LEFT, padx=5)
        self.quality_label.pack(side=LEFT)

        # 3. DETAILS FRAME
        details_frame = ttk.Labelframe(main_control_frame, text=" 📄 Image Details ", padding=15, bootstyle=INFO)
        details_frame.grid(row=0, column=2, sticky=NSEW, padx=(10, 0))

        self.info = ttk.Label(details_frame, text="No image selected.", font=("Segoe UI", 10), foreground="gray",
                              justify=LEFT)
        self.info.pack(side=LEFT, anchor=NW, expand=True, fill=BOTH)

    def create_statusbar(self):
        status_frame = ttk.Frame(self.root, padding=(15, 10))
        status_frame.pack(fill=X, side=BOTTOM)

        self.status = ttk.Label(status_frame, text="Ready", anchor=W, font=("Segoe UI", 9, "italic"))
        self.status.pack(side=LEFT, fill=X, expand=True)

        self.progress = ttk.Progressbar(status_frame, mode='determinate', length=350, bootstyle=SUCCESS)
        self.progress.pack(side=RIGHT)

    ####################################################
    # 2. YARDIMCI VE ZOOM FONKSİYONLARI
    ####################################################

    def show_image_preview(self, path, title_text):
        """Resme tıklandığında büyük haliyle yeni pencerede açar (Zoom)"""
        if not path or not os.path.exists(path): return

        top = ttk.Toplevel(self.root)
        top.title(title_text)
        top.geometry("850x650")

        try:
            img = Image.open(path)
            img.thumbnail((800, 600), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            lbl = ttk.Label(top, image=photo)
            lbl.image = photo
            lbl.pack(expand=True, fill=BOTH, pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot preview image.\n{e}")

    def change_theme(self, theme):
        self.root.style.theme_use(theme)
        if not self.input_path:
            fg_color = "gray" if theme == "darkly" else "dim gray"
            self.before_image.configure(foreground=fg_color)
            self.after_image.configure(foreground=fg_color)
            if "No image" in self.info.cget("text"):
                self.info.configure(foreground=fg_color)

    def slider_changed(self, value):
        if not self.smart_var.get():
            value = int(float(value))
            if hasattr(self, 'quality_label'):
                self.quality_label.configure(text=f"{value}%")

    def toggle_smart_mode(self):
        if self.smart_var.get():
            self.quality.state(['disabled'])
            self.quality_label.configure(text="Auto", bootstyle=SUCCESS)
        else:
            self.quality.state(['!disabled'])
            self.quality_label.configure(bootstyle=DEFAULT)
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
    # 3. İŞLEMLER (MULTITHREADING EKLENDİ)
    ####################################################

    def load_image_to_ui(self, filename):
        self.input_path = filename
        thumb = create_thumbnail(filename)

        self.before_image.configure(image=thumb, text="")
        self.before_image.image = thumb

        self.after_image.configure(image='', text="✨\nCompressed Preview", font=("Segoe UI", 13), cursor="arrow")
        self.after_image.image = None
        # Önceki Tıklamaları Sıfırla (Zoom Ataması create_preview_area içinde halledildi)

        width, height = image_resolution(filename)
        orig_size = readable_size(file_size(filename))

        self.info.configure(
            text=f"📁 Name: {os.path.basename(filename)}\n📐 Res: {width}x{height}\n💽 Size: {orig_size}",
            foreground=DEFAULT
        )
        self.status.configure(text="Image Loaded Successfully")
        self.progress['value'] = 0

    def select_image(self):
        filename = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.webp")])
        if filename and validate_image(filename):
            self.load_image_to_ui(filename)
        elif filename:
            messagebox.showerror("Error", "Unsupported image.")

    def compress_image(self):
        if not self.input_path:
            messagebox.showwarning("Warning", "Please select or drop an image first.")
            return

        # Format Dönüştürme Kontrolü
        selected_format = self.format_var.get()
        target_fmt = f".{selected_format.lower()}" if selected_format != "Original" else None

        ext = target_fmt if target_fmt else os.path.splitext(self.input_path)[1]
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]
        suggested_out_path = unique_filename(
            os.path.join(os.path.dirname(self.input_path), f"compressed_{base_name}{ext}"))

        out_path = filedialog.asksaveasfilename(
            initialfile=os.path.basename(suggested_out_path),
            defaultextension=ext,
            filetypes=[("Image File", f"*{ext}"), ("All Files", "*.*")],
            title="Save Compressed Image"
        )
        if not out_path: return
        self.output_path = out_path

        quality = self.get_smart_quality(self.input_path) if self.smart_var.get() else int(float(self.quality.get()))
        self.compressor.keep_exif = self.exif_var.get()  # EXIF Ayarını Aktar

        self.status.configure(text=f"Compressing... (Quality: {quality})")
        self.progress.start(15)

        # UI Donmasını Engellemek İçin Threading Kullanıyoruz
        def task():
            try:
                self.compressor.compress(self.input_path, self.output_path, quality=quality, target_format=target_fmt)
                orig_size = file_size(self.input_path)
                comp_size = file_size(self.output_path)
                ratio = 100 - ((comp_size / orig_size) * 100) if orig_size > 0 else 0

                history_record = create_history_item(self.input_path, orig_size, comp_size, ratio)
                save_history(history_record)

                # UI güncellemeleri ana thread'e yönlendirilmeli
                self.root.after(0, self._compress_success_ui, comp_size, ratio, quality)
            except Exception as e:
                self.root.after(0, self._compress_error_ui, str(e))

        threading.Thread(target=task, daemon=True).start()

    def _compress_success_ui(self, comp_size, ratio, quality):
        self.progress.stop()
        self.progress['value'] = 100

        thumb = create_thumbnail(self.output_path)
        self.after_image.configure(image=thumb, text="", cursor="hand2")
        self.after_image.image = thumb
        self.after_image.bind("<Button-1>", lambda e: self.show_image_preview(self.output_path, "Compressed Image"))

        current_info = self.info.cget("text").split("\n✅ New Size:")[0]
        self.info.configure(
            text=current_info + f"\n✅ New Size: {readable_size(comp_size)} (Q: {quality})\n🔥 Saved: %{ratio:.2f}")
        self.status.configure(text=f"Compression successful! Saved %{ratio:.2f}")

    def _compress_error_ui(self, error_msg):
        self.progress.stop()
        self.status.configure(text="Error occurred.")
        messagebox.showerror("Error", f"An error occurred:\n{error_msg}")

    def batch_compress(self):
        files = filedialog.askopenfilenames(title="Select Multiple Images",
                                            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp")])
        if not files: return
        out_dir = filedialog.askdirectory(title="Select Output Folder")
        if not out_dir: return

        total_files = len(files)
        self.progress['mode'] = 'determinate'
        self.progress['maximum'] = total_files
        self.progress['value'] = 0

        selected_format = self.format_var.get()
        target_fmt = f".{selected_format.lower()}" if selected_format != "Original" else None
        self.compressor.keep_exif = self.exif_var.get()  # EXIF Ayarını Aktar

        def task():
            success_count = 0
            total_saved_bytes = 0
            for i, file_path in enumerate(files):
                filename = os.path.basename(file_path)
                base_name = os.path.splitext(filename)[0]
                ext = target_fmt if target_fmt else os.path.splitext(filename)[1]
                out_path = unique_filename(os.path.join(out_dir, f"compressed_{base_name}{ext}"))

                quality = self.get_smart_quality(file_path) if self.smart_var.get() else int(float(self.quality.get()))

                self.root.after(0, self._update_batch_status, i + 1, total_files, filename)

                if validate_image(file_path):
                    try:
                        self.compressor.compress(file_path, out_path, quality=quality, target_format=target_fmt)
                        orig_size = file_size(file_path)
                        comp_size = file_size(out_path)
                        ratio = 100 - ((comp_size / orig_size) * 100) if orig_size > 0 else 0
                        total_saved_bytes += (orig_size - comp_size)

                        history_record = create_history_item(file_path, orig_size, comp_size, ratio)
                        save_history(history_record)
                        success_count += 1
                    except Exception as e:
                        print(f"Error compressing {file_path}: {e}")

            self.root.after(0, self._batch_complete, success_count, total_files, total_saved_bytes)

        threading.Thread(target=task, daemon=True).start()

    def _update_batch_status(self, current, total, filename):
        self.progress['value'] = current
        self.status.configure(text=f"Batch Compressing ({current}/{total}): {filename}")

    def _batch_complete(self, success_count, total_files, total_saved_bytes):
        saved_str = readable_size(max(0, total_saved_bytes))
        self.status.configure(text=f"Batch Completed. ({success_count}/{total_files}) - Total Saved: {saved_str}")
        messagebox.showinfo("Done",
                            f"Batch compression finished.\nSuccess: {success_count}/{total_files}\nTotal Space Saved: {saved_str}")

    ####################################################
    # 4. İSTATİSTİKLER PENCERESİ (STATISTICS)
    ####################################################

    def show_statistics(self):
        stats_window = ttk.Toplevel(self.root)
        stats_window.title("Compression Statistics")
        stats_window.geometry("400x380")
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