import os
import tkinter as tk
from tkinter import filedialog, messagebox


# ==========================================================
# FILE DIALOGS
# ==========================================================

def select_images(
    parent=None
):
    """
    Open a file dialog and return selected image files.

    Returns:
        tuple[str, ...]
    """

    return filedialog.askopenfilenames(
        parent=parent,
        title="Select Images",
        filetypes=[
            (
                "Image Files",
                "*.jpg *.jpeg *.png "
                "*.webp *.bmp *.tiff *.tif"
            ),
            (
                "JPEG Images",
                "*.jpg *.jpeg"
            ),
            (
                "PNG Images",
                "*.png"
            ),
            (
                "WebP Images",
                "*.webp"
            ),
            (
                "All Files",
                "*.*"
            )
        ]
    )


def select_single_image(
    parent=None
):
    """
    Select a single image file.

    Returns:
        str
    """

    return filedialog.askopenfilename(
        parent=parent,
        title="Select Image",
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


def select_folder(
    parent=None
):
    """
    Open a directory selection dialog.

    Returns:
        str
    """

    return filedialog.askdirectory(
        parent=parent,
        title="Select Folder"
    )


def select_output_directory(
    parent=None
):
    """
    Select output directory for compressed images.

    Returns:
        str
    """

    return filedialog.askdirectory(
        parent=parent,
        title="Select Output Directory"
    )


def select_save_location(
    parent=None,
    initial_file="compressed_image.jpg"
):
    """
    Select a location for saving a single image.

    Returns:
        str
    """

    return filedialog.asksaveasfilename(
        parent=parent,
        title="Save Image",
        initialfile=initial_file,
        defaultextension=".jpg",
        filetypes=[
            (
                "JPEG Image",
                "*.jpg"
            ),
            (
                "PNG Image",
                "*.png"
            ),
            (
                "WebP Image",
                "*.webp"
            ),
            (
                "All Files",
                "*.*"
            )
        ]
    )


# ==========================================================
# MESSAGE BOXES
# ==========================================================

def show_info(
    title,
    message,
    parent=None
):
    """
    Show an information message.
    """

    return messagebox.showinfo(
        title,
        message,
        parent=parent
    )


def show_warning(
    title,
    message,
    parent=None
):
    """
    Show a warning message.
    """

    return messagebox.showwarning(
        title,
        message,
        parent=parent
    )


def show_error(
    title,
    message,
    parent=None
):
    """
    Show an error message.
    """

    return messagebox.showerror(
        title,
        message,
        parent=parent
    )


def show_question(
    title,
    message,
    parent=None
):
    """
    Show a yes/no confirmation dialog.

    Returns:
        bool
    """

    return messagebox.askyesno(
        title,
        message,
        parent=parent
    )


def show_retry_cancel(
    title,
    message,
    parent=None
):
    """
    Ask the user whether to retry an operation.

    Returns:
        bool
    """

    return messagebox.askretrycancel(
        title,
        message,
        parent=parent
    )


# ==========================================================
# APPLICATION-SPECIFIC DIALOGS
# ==========================================================

def confirm_clear_files(
    parent=None
):
    """
    Ask the user before clearing selected images.
    """

    return show_question(
        "Clear Images",
        (
            "Are you sure you want to remove "
            "all selected images?"
        ),
        parent
    )


def confirm_compression(
    file_count,
    parent=None
):
    """
    Ask the user to confirm compression.

    Args:
        file_count: Number of images to process.
    """

    return show_question(
        "Start Compression",
        (
            f"{file_count} image(s) will be compressed.\n\n"
            "Do you want to continue?"
        ),
        parent
    )


def confirm_exit(
    parent=None
):
    """
    Ask the user before closing the application.
    """

    return show_question(
        "Exit",
        "Are you sure you want to exit ImageCompressor?",
        parent
    )


# ==========================================================
# VALIDATION DIALOGS
# ==========================================================

def show_no_images_selected(
    parent=None
):
    """
    Display a warning when no images are selected.
    """

    return show_warning(
        "No Images",
        (
            "Please select at least one image "
            "before continuing."
        ),
        parent
    )


def show_invalid_image(
    file_path=None,
    parent=None
):
    """
    Display invalid image warning.
    """

    if file_path:

        filename = os.path.basename(
            file_path
        )

        message = (
            f"The selected file is not a valid "
            f"image:\n\n{filename}"
        )

    else:

        message = (
            "The selected file is not a valid image."
        )

    return show_warning(
        "Invalid Image",
        message,
        parent
    )


def show_invalid_directory(
    directory=None,
    parent=None
):
    """
    Display invalid directory warning.
    """

    if directory:

        message = (
            "The selected directory does not exist:\n\n"
            f"{directory}"
        )

    else:

        message = (
            "The selected directory is invalid."
        )

    return show_warning(
        "Invalid Directory",
        message,
        parent
    )


def show_invalid_quality(
    quality,
    parent=None
):
    """
    Display invalid quality warning.
    """

    return show_warning(
        "Invalid Quality",
        (
            f"'{quality}' is not a valid quality value.\n\n"
            "Quality must be between 1 and 100."
        ),
        parent
    )


def show_invalid_dimensions(
    width,
    height,
    parent=None
):
    """
    Display invalid resize dimensions warning.
    """

    return show_warning(
        "Invalid Dimensions",
        (
            f"Width: {width}\n"
            f"Height: {height}\n\n"
            "Width and height must be positive numbers."
        ),
        parent
    )


# ==========================================================
# COMPRESSION RESULT DIALOGS
# ==========================================================

def show_compression_success(
    processed_count,
    original_size,
    new_size,
    saving_percentage,
    parent=None
):
    """
    Display successful compression summary.
    """

    message = (
        "Compression completed successfully.\n\n"
        f"Processed images: {processed_count}\n"
        f"Original size: {original_size}\n"
        f"Compressed size: {new_size}\n"
        f"Storage saved: {saving_percentage:.2f}%"
    )

    return show_info(
        "Compression Complete",
        message,
        parent
    )


def show_compression_error(
    error,
    parent=None
):
    """
    Display compression error.
    """

    return show_error(
        "Compression Error",
        (
            "An error occurred during compression:\n\n"
            f"{error}"
        ),
        parent
    )


def show_partial_compression_error(
    successful_count,
    failed_count,
    parent=None
):
    """
    Display partial compression result.
    """

    return show_warning(
        "Compression Completed with Errors",
        (
            f"Successful: {successful_count}\n"
            f"Failed: {failed_count}\n\n"
            "Some images could not be processed."
        ),
        parent
    )


# ==========================================================
# DIRECTORY DIALOGS
# ==========================================================

def show_output_directory_required(
    parent=None
):
    """
    Display output directory warning.
    """

    return show_warning(
        "Output Directory",
        (
            "Please select an output directory "
            "before starting compression."
        ),
        parent
    )


def show_directory_created(
    directory,
    parent=None
):
    """
    Inform the user that a directory was created.
    """

    return show_info(
        "Directory Created",
        (
            "Output directory was created successfully:\n\n"
            f"{directory}"
        ),
        parent
    )


# ==========================================================
# FILE OVERWRITE
# ==========================================================

def confirm_overwrite(
    file_path,
    parent=None
):
    """
    Ask the user whether an existing file can be overwritten.
    """

    filename = os.path.basename(
        file_path
    )

    return show_question(
        "File Already Exists",
        (
            f"The file already exists:\n\n"
            f"{filename}\n\n"
            "Do you want to overwrite it?"
        ),
        parent
    )


# ==========================================================
# GENERIC ERROR HANDLER
# ==========================================================

def show_unexpected_error(
    error,
    parent=None
):
    """
    Display an unexpected application error.
    """

    return show_error(
        "Unexpected Error",
        (
            "An unexpected error occurred.\n\n"
            f"Error:\n{error}"
        ),
        parent
    )


# ==========================================================
# INFORMATION DIALOGS
# ==========================================================

def show_about(
    parent=None
):
    """
    Display application information.
    """

    message = (
        "ImageCompressor\n\n"
        "A Python desktop application for "
        "image compression, resizing and conversion.\n\n"
        "Built with Python and Tkinter."
    )

    return show_info(
        "About ImageCompressor",
        message,
        parent
    )


def show_help(
    parent=None
):
    """
    Display basic application instructions.
    """

    message = (
        "How to use ImageCompressor\n\n"
        "1. Add one or more images.\n"
        "2. Select the desired compression quality.\n"
        "3. Choose an output format if needed.\n"
        "4. Optionally enable resizing.\n"
        "5. Select an output directory.\n"
        "6. Click 'Compress Images'.\n\n"
        "The application will display the compression "
        "results after processing."
    )

    return show_info(
        "Help",
        message,
        parent
    )


# ==========================================================
# CUSTOM SIMPLE DIALOG
# ==========================================================

def show_text_dialog(
    parent,
    title,
    message,
    width=420,
    height=220
):
    """
    Display a simple custom text dialog.

    Returns:
        None
    """

    dialog = tk.Toplevel(
        parent
    )

    dialog.title(
        title
    )

    dialog.geometry(
        f"{width}x{height}"
    )

    dialog.transient(
        parent
    )

    dialog.grab_set()

    # ------------------------------------------------------
    # Content
    # ------------------------------------------------------

    container = tk.Frame(
        dialog,
        padx=20,
        pady=20
    )

    container.pack(
        fill=tk.BOTH,
        expand=True
    )

    label = tk.Label(
        container,
        text=message,
        justify=tk.LEFT,
        wraplength=width - 50,
        font=(
            "Segoe UI",
            10
        )
    )

    label.pack(
        fill=tk.BOTH,
        expand=True
    )

    # ------------------------------------------------------
    # Close button
    # ------------------------------------------------------

    close_button = tk.Button(
        container,
        text="Close",
        command=dialog.destroy,
        width=12
    )

    close_button.pack(
        pady=(10, 0)
    )

    dialog.wait_window()


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    root = tk.Tk()

    root.withdraw()

    show_about(
        root
    )

    root.destroy()