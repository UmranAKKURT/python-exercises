import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from PIL import Image
except ImportError:
    Image = None

from src.utils.file_manager import FileManager
from src.utils.helpers import (
    format_bytes,
    calculate_saving_percentage,
    get_current_timestamp,
)


class ImageCompressorApp:
    """
    Main graphical user interface for ImageCompressor.

    Responsibilities:
        - Create the main application window
        - Select image files
        - Select image folders
        - Display selected files
        - Manage compression settings
        - Display compression results
        - Provide basic application status information
    """

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(
        self,
        root=None
    ):
        """
        Initialize the ImageCompressor application.
        """

        self.root = root or tk.Tk()

        self.root.title(
            "ImageCompressor"
        )

        self.root.geometry(
            "1100x700"
        )

        self.root.minsize(
            900,
            600
        )

        self.file_manager = (
            FileManager()
        )

        self.selected_files = []

        self.compression_results = []

        self.output_directory = ""

        self.quality = tk.IntVar(
            value=80
        )

        self.output_format = tk.StringVar(
            value="Original"
        )

        self.resize_enabled = tk.BooleanVar(
            value=False
        )

        self.resize_width = tk.IntVar(
            value=1920
        )

        self.resize_height = tk.IntVar(
            value=1080
        )

        self.status_text = tk.StringVar(
            value="Ready"
        )

        self.file_count_text = tk.StringVar(
            value="0 files selected"
        )

        self.total_size_text = tk.StringVar(
            value="Total size: 0 B"
        )

        self.result_text = tk.StringVar(
            value="No compression performed yet."
        )

        self._configure_style()

        self._build_interface()

    # ==========================================================
    # STYLE
    # ==========================================================

    def _configure_style(
        self
    ):
        """
        Configure ttk styles.
        """

        style = ttk.Style(
            self.root
        )

        try:

            style.theme_use(
                "clam"
            )

        except tk.TclError:

            pass

        style.configure(
            "Title.TLabel",
            font=(
                "Segoe UI",
                22,
                "bold"
            )
        )

        style.configure(
            "Subtitle.TLabel",
            font=(
                "Segoe UI",
                10
            )
        )

        style.configure(
            "Section.TLabel",
            font=(
                "Segoe UI",
                12,
                "bold"
            )
        )

        style.configure(
            "Primary.TButton",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            padding=8
        )

        style.configure(
            "Status.TLabel",
            font=(
                "Segoe UI",
                9
            )
        )

    # ==========================================================
    # BUILD INTERFACE
    # ==========================================================

    def _build_interface(
        self
    ):
        """
        Build the complete GUI.
        """

        self._build_header()

        self._build_main_area()

        self._build_status_bar()

    # ==========================================================
    # HEADER
    # ==========================================================

    def _build_header(
        self
    ):
        """
        Create application header.
        """

        header = ttk.Frame(
            self.root,
            padding=20
        )

        header.pack(
            fill=tk.X
        )

        title = ttk.Label(
            header,
            text="ImageCompressor",
            style="Title.TLabel"
        )

        title.pack(
            anchor=tk.W
        )

        subtitle = ttk.Label(
            header,
            text=(
                "Compress, resize and convert "
                "your images easily."
            ),
            style="Subtitle.TLabel"
        )

        subtitle.pack(
            anchor=tk.W,
            pady=(4, 0)
        )

    # ==========================================================
    # MAIN AREA
    # ==========================================================

    def _build_main_area(
        self
    ):
        """
        Create the main application area.
        """

        container = ttk.Frame(
            self.root,
            padding=15
        )

        container.pack(
            fill=tk.BOTH,
            expand=True
        )

        container.columnconfigure(
            0,
            weight=3
        )

        container.columnconfigure(
            1,
            weight=2
        )

        container.rowconfigure(
            0,
            weight=1
        )

        self._build_file_panel(
            container
        )

        self._build_settings_panel(
            container
        )

    # ==========================================================
    # FILE PANEL
    # ==========================================================

    def _build_file_panel(
        self,
        parent
    ):
        """
        Build the file selection and result panel.
        """

        frame = ttk.LabelFrame(
            parent,
            text="Images",
            padding=12
        )

        frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 10)
        )

        frame.rowconfigure(
            1,
            weight=1
        )

        frame.columnconfigure(
            0,
            weight=1
        )

        # ------------------------------------------------------
        # Buttons
        # ------------------------------------------------------

        button_frame = ttk.Frame(
            frame
        )

        button_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 10)
        )

        ttk.Button(
            button_frame,
            text="Add Images",
            command=self.select_images,
            style="Primary.TButton"
        ).pack(
            side=tk.LEFT,
            padx=(0, 5)
        )

        ttk.Button(
            button_frame,
            text="Add Folder",
            command=self.select_folder
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_files
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # ------------------------------------------------------
        # File List
        # ------------------------------------------------------

        list_frame = ttk.Frame(
            frame
        )

        list_frame.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        list_frame.rowconfigure(
            0,
            weight=1
        )

        list_frame.columnconfigure(
            0,
            weight=1
        )

        self.file_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.EXTENDED,
            font=(
                "Segoe UI",
                10
            )
        )

        self.file_listbox.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.file_listbox.yview
        )

        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.file_listbox.configure(
            yscrollcommand=scrollbar.set
        )

        # ------------------------------------------------------
        # File Information
        # ------------------------------------------------------

        info_frame = ttk.Frame(
            frame
        )

        info_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(10, 0)
        )

        ttk.Label(
            info_frame,
            textvariable=self.file_count_text
        ).pack(
            side=tk.LEFT
        )

        ttk.Label(
            info_frame,
            textvariable=self.total_size_text
        ).pack(
            side=tk.RIGHT
        )

    # ==========================================================
    # SETTINGS PANEL
    # ==========================================================

    def _build_settings_panel(
        self,
        parent
    ):
        """
        Build compression settings panel.
        """

        frame = ttk.LabelFrame(
            parent,
            text="Compression Settings",
            padding=15
        )

        frame.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        # ------------------------------------------------------
        # Quality
        # ------------------------------------------------------

        ttk.Label(
            frame,
            text="Quality",
            style="Section.TLabel"
        ).pack(
            anchor=tk.W
        )

        quality_frame = ttk.Frame(
            frame
        )

        quality_frame.pack(
            fill=tk.X,
            pady=(8, 20)
        )

        self.quality_scale = ttk.Scale(
            quality_frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            command=self._on_quality_change
        )

        self.quality_scale.set(
            self.quality.get()
        )

        self.quality_scale.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True
        )

        self.quality_label = ttk.Label(
            quality_frame,
            text="80"
        )

        self.quality_label.pack(
            side=tk.RIGHT,
            padx=(10, 0)
        )

        # ------------------------------------------------------
        # Output Format
        # ------------------------------------------------------

        ttk.Label(
            frame,
            text="Output Format",
            style="Section.TLabel"
        ).pack(
            anchor=tk.W
        )

        format_combo = ttk.Combobox(
            frame,
            textvariable=self.output_format,
            values=[
                "Original",
                "JPG",
                "PNG",
                "WEBP"
            ],
            state="readonly"
        )

        format_combo.pack(
            fill=tk.X,
            pady=(8, 20)
        )

        # ------------------------------------------------------
        # Resize
        # ------------------------------------------------------

        ttk.Label(
            frame,
            text="Resize",
            style="Section.TLabel"
        ).pack(
            anchor=tk.W
        )

        resize_check = ttk.Checkbutton(
            frame,
            text="Enable resizing",
            variable=self.resize_enabled
        )

        resize_check.pack(
            anchor=tk.W,
            pady=(8, 10)
        )

        size_frame = ttk.Frame(
            frame
        )

        size_frame.pack(
            fill=tk.X,
            pady=(0, 20)
        )

        ttk.Label(
            size_frame,
            text="Width:"
        ).grid(
            row=0,
            column=0,
            sticky=tk.W
        )

        width_entry = ttk.Entry(
            size_frame,
            textvariable=self.resize_width,
            width=10
        )

        width_entry.grid(
            row=0,
            column=1,
            padx=(8, 15)
        )

        ttk.Label(
            size_frame,
            text="Height:"
        ).grid(
            row=0,
            column=2,
            sticky=tk.W
        )

        height_entry = ttk.Entry(
            size_frame,
            textvariable=self.resize_height,
            width=10
        )

        height_entry.grid(
            row=0,
            column=3,
            padx=(8, 0)
        )

        # ------------------------------------------------------
        # Output Directory
        # ------------------------------------------------------

        ttk.Label(
            frame,
            text="Output Directory",
            style="Section.TLabel"
        ).pack(
            anchor=tk.W
        )

        output_frame = ttk.Frame(
            frame
        )

        output_frame.pack(
            fill=tk.X,
            pady=(8, 20)
        )

        self.output_entry = ttk.Entry(
            output_frame
        )

        self.output_entry.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True
        )

        ttk.Button(
            output_frame,
            text="Browse",
            command=self.select_output_directory
        ).pack(
            side=tk.RIGHT,
            padx=(8, 0)
        )

        # ------------------------------------------------------
        # Compress Button
        # ------------------------------------------------------

        ttk.Button(
            frame,
            text="Compress Images",
            command=self.start_compression,
            style="Primary.TButton"
        ).pack(
            fill=tk.X,
            pady=(10, 15)
        )

        # ------------------------------------------------------
        # Result
        # ------------------------------------------------------

        result_frame = ttk.LabelFrame(
            frame,
            text="Result",
            padding=10
        )

        result_frame.pack(
            fill=tk.BOTH,
            expand=True
        )

        ttk.Label(
            result_frame,
            textvariable=self.result_text,
            wraplength=300,
            justify=tk.LEFT
        ).pack(
            anchor=tk.W
        )

    # ==========================================================
    # STATUS BAR
    # ==========================================================

    def _build_status_bar(
        self
    ):
        """
        Create application status bar.
        """

        status_frame = ttk.Frame(
            self.root,
            padding=8
        )

        status_frame.pack(
            fill=tk.X
        )

        ttk.Label(
            status_frame,
            textvariable=self.status_text,
            style="Status.TLabel"
        ).pack(
            side=tk.LEFT
        )

        ttk.Label(
            status_frame,
            text="ImageCompressor"
        ).pack(
            side=tk.RIGHT
        )

    # ==========================================================
    # SELECT IMAGES
    # ==========================================================

    def select_images(
        self
    ):
        """
        Open file dialog and select multiple images.
        """

        file_paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[
                (
                    "Image Files",
                    "*.jpg *.jpeg *.png "
                    "*.webp *.bmp *.tiff *.tif"
                ),
                (
                    "All Files",
                    "*.*"
                )
            ]
        )

        if not file_paths:

            return

        added_count = 0

        for file_path in file_paths:

            if file_path in self.selected_files:

                continue

            if not self.file_manager.is_image(
                file_path
            ):

                continue

            self.selected_files.append(
                file_path
            )

            added_count += 1

        self._refresh_file_list()

        self.status_text.set(
            f"{added_count} image(s) added."
        )

    # ==========================================================
    # SELECT FOLDER
    # ==========================================================

    def select_folder(
        self
    ):
        """
        Select a folder and add all supported images.
        """

        directory = filedialog.askdirectory(
            title="Select Image Folder"
        )

        if not directory:

            return

        try:

            image_files = (
                self.file_manager.find_images(
                    directory,
                    recursive=False
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Error",
                str(error)
            )

            return

        added_count = 0

        for file_path in image_files:

            if file_path in self.selected_files:

                continue

            self.selected_files.append(
                file_path
            )

            added_count += 1

        self._refresh_file_list()

        self.status_text.set(
            f"{added_count} image(s) added from folder."
        )

    # ==========================================================
    # SELECT OUTPUT DIRECTORY
    # ==========================================================

    def select_output_directory(
        self
    ):
        """
        Select the output directory.
        """

        directory = filedialog.askdirectory(
            title="Select Output Directory"
        )

        if not directory:

            return

        self.output_directory = (
            os.path.abspath(
                directory
            )
        )

        self.output_entry.delete(
            0,
            tk.END
        )

        self.output_entry.insert(
            0,
            self.output_directory
        )

        self.status_text.set(
            "Output directory selected."
        )

    # ==========================================================
    # CLEAR FILES
    # ==========================================================

    def clear_files(
        self
    ):
        """
        Remove all selected files.
        """

        self.selected_files.clear()

        self.compression_results.clear()

        self._refresh_file_list()

        self.result_text.set(
            "No compression performed yet."
        )

        self.status_text.set(
            "Selection cleared."
        )

    # ==========================================================
    # REFRESH FILE LIST
    # ==========================================================

    def _refresh_file_list(
        self
    ):
        """
        Refresh image list and statistics.
        """

        self.file_listbox.delete(
            0,
            tk.END
        )

        total_size = 0

        for file_path in self.selected_files:

            filename = (
                self.file_manager.get_filename(
                    file_path
                )
            )

            size = (
                self.file_manager.get_file_size(
                    file_path
                )
            )

            total_size += size

            display_text = (
                f"{filename}    "
                f"({format_bytes(size)})"
            )

            self.file_listbox.insert(
                tk.END,
                display_text
            )

        count = len(
            self.selected_files
        )

        self.file_count_text.set(
            f"{count} file(s) selected"
        )

        self.total_size_text.set(
            f"Total size: {format_bytes(total_size)}"
        )

    # ==========================================================
    # QUALITY CHANGE
    # ==========================================================

    def _on_quality_change(
        self,
        value
    ):
        """
        Update quality value when slider changes.
        """

        try:

            quality = int(
                float(
                    value
                )
            )

        except (
            ValueError,
            TypeError
        ):

            quality = 80

        self.quality.set(
            quality
        )

        self.quality_label.configure(
            text=str(
                quality
            )
        )

    # ==========================================================
    # START COMPRESSION
    # ==========================================================

    def start_compression(
        self
    ):
        """
        Start compression process.

        The actual compression engine will be connected
        to this method after all core modules are completed.
        """

        if not self.selected_files:

            messagebox.showwarning(
                "No Images",
                "Please select at least one image."
            )

            return

        output_directory = (
            self.output_entry.get().strip()
        )

        if not output_directory:

            output_directory = (
                os.path.join(
                    os.path.dirname(
                        self.selected_files[0]
                    ),
                    "compressed"
                )
            )

            self.output_directory = (
                output_directory
            )

            self.output_entry.delete(
                0,
                tk.END
            )

            self.output_entry.insert(
                0,
                output_directory
            )

        try:

            self.file_manager.create_directory(
                output_directory
            )

        except Exception as error:

            messagebox.showerror(
                "Output Directory Error",
                str(error)
            )

            return

        self.status_text.set(
            "Compression engine is preparing..."
        )

        self.result_text.set(
            "Compression will be connected "
            "to the core engine."
        )

        messagebox.showinfo(
            "Ready",
            (
                f"{len(self.selected_files)} "
                "image(s) selected.\n\n"
                "The GUI is ready. "
                "The compression engine will "
                "be connected in the next stage."
            )
        )

    # ==========================================================
    # GET SETTINGS
    # ==========================================================

    def get_settings(
        self
    ):
        """
        Return current GUI settings.
        """

        return {
            "quality": self.quality.get(),

            "output_format": (
                self.output_format.get()
            ),

            "resize_enabled": (
                self.resize_enabled.get()
            ),

            "resize_width": (
                self.resize_width.get()
            ),

            "resize_height": (
                self.resize_height.get()
            ),

            "output_directory": (
                self.output_entry.get().strip()
            )
        }

    # ==========================================================
    # SHOW RESULT
    # ==========================================================

    def show_result(
        self,
        result
    ):
        """
        Display a compression result.
        """

        if not isinstance(
            result,
            dict
        ):

            return

        original_size = result.get(
            "original_size",
            0
        )

        new_size = result.get(
            "new_size",
            0
        )

        saving = (
            calculate_saving_percentage(
                original_size,
                new_size
            )
        )

        filename = result.get(
            "filename",
            "Image"
        )

        self.result_text.set(
            (
                f"File: {filename}\n"
                f"Original: "
                f"{format_bytes(original_size)}\n"
                f"Compressed: "
                f"{format_bytes(new_size)}\n"
                f"Saved: {saving:.2f}%\n"
                f"Time: "
                f"{result.get('processing_time', 0):.2f}s"
            )
        )

    # ==========================================================
    # SHOW SUMMARY
    # ==========================================================

    def show_summary(
        self,
        results
    ):
        """
        Display summary of compression results.
        """

        if not results:

            self.result_text.set(
                "No results available."
            )

            return

        total_original = 0

        total_new = 0

        successful = 0

        for result in results:

            if not isinstance(
                result,
                dict
            ):

                continue

            if result.get(
                "success",
                True
            ) is False:

                continue

            successful += 1

            total_original += int(
                result.get(
                    "original_size",
                    0
                )
            )

            total_new += int(
                result.get(
                    "new_size",
                    0
                )
            )

        saved_percentage = (
            calculate_saving_percentage(
                total_original,
                total_new
            )
        )

        self.result_text.set(
            (
                f"Processed: {successful}\n"
                f"Original: "
                f"{format_bytes(total_original)}\n"
                f"Compressed: "
                f"{format_bytes(total_new)}\n"
                f"Saved: "
                f"{saved_percentage:.2f}%"
            )
        )

    # ==========================================================
    # RUN
    # ==========================================================

    def run(
        self
    ):
        """
        Start the Tkinter event loop.
        """

        self.root.mainloop()


# ==============================================================
# DIRECT EXECUTION
# ==============================================================

if __name__ == "__main__":

    app = ImageCompressorApp()

    app.run()