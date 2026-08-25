import tkinter as tk
from tkinter import ttk


# ==========================================================
# TITLE COMPONENT
# ==========================================================

def create_title(
    parent,
    text,
    font=("Segoe UI", 22, "bold")
):
    """
    Create a reusable title label.
    """

    label = ttk.Label(
        parent,
        text=text,
        font=font
    )

    return label


# ==========================================================
# SUBTITLE COMPONENT
# ==========================================================

def create_subtitle(
    parent,
    text,
    font=("Segoe UI", 10)
):
    """
    Create a reusable subtitle label.
    """

    label = ttk.Label(
        parent,
        text=text,
        font=font
    )

    return label


# ==========================================================
# SECTION TITLE
# ==========================================================

def create_section_title(
    parent,
    text
):
    """
    Create a section title.
    """

    label = ttk.Label(
        parent,
        text=text,
        font=(
            "Segoe UI",
            12,
            "bold"
        )
    )

    return label


# ==========================================================
# PRIMARY BUTTON
# ==========================================================

def create_primary_button(
    parent,
    text,
    command,
    **kwargs
):
    """
    Create a primary application button.
    """

    button = ttk.Button(
        parent,
        text=text,
        command=command,
        **kwargs
    )

    return button


# ==========================================================
# SECONDARY BUTTON
# ==========================================================

def create_secondary_button(
    parent,
    text,
    command,
    **kwargs
):
    """
    Create a secondary application button.
    """

    button = ttk.Button(
        parent,
        text=text,
        command=command,
        **kwargs
    )

    return button


# ==========================================================
# ENTRY
# ==========================================================

def create_entry(
    parent,
    textvariable=None,
    width=30,
    **kwargs
):
    """
    Create a reusable text entry.
    """

    entry = ttk.Entry(
        parent,
        textvariable=textvariable,
        width=width,
        **kwargs
    )

    return entry


# ==========================================================
# COMBOBOX
# ==========================================================

def create_combobox(
    parent,
    values,
    textvariable=None,
    state="readonly",
    **kwargs
):
    """
    Create a reusable combobox.
    """

    combo = ttk.Combobox(
        parent,
        values=values,
        textvariable=textvariable,
        state=state,
        **kwargs
    )

    return combo


# ==========================================================
# CHECKBUTTON
# ==========================================================

def create_checkbutton(
    parent,
    text,
    variable,
    command=None,
    **kwargs
):
    """
    Create a reusable checkbutton.
    """

    checkbutton = ttk.Checkbutton(
        parent,
        text=text,
        variable=variable,
        command=command,
        **kwargs
    )

    return checkbutton


# ==========================================================
# SCALE
# ==========================================================

def create_scale(
    parent,
    variable,
    from_=1,
    to=100,
    command=None,
    orient=tk.HORIZONTAL,
    **kwargs
):
    """
    Create a reusable scale widget.
    """

    scale = ttk.Scale(
        parent,
        variable=variable,
        from_=from_,
        to=to,
        command=command,
        orient=orient,
        **kwargs
    )

    return scale


# ==========================================================
# LISTBOX
# ==========================================================

def create_listbox(
    parent,
    selectmode=tk.EXTENDED,
    height=15,
    **kwargs
):
    """
    Create a reusable listbox.
    """

    listbox = tk.Listbox(
        parent,
        selectmode=selectmode,
        height=height,
        font=(
            "Segoe UI",
            10
        ),
        **kwargs
    )

    return listbox


# ==========================================================
# SCROLLBAR
# ==========================================================

def create_scrollbar(
    parent,
    command=None,
    orient=tk.VERTICAL,
    **kwargs
):
    """
    Create a reusable scrollbar.
    """

    scrollbar = ttk.Scrollbar(
        parent,
        orient=orient,
        command=command,
        **kwargs
    )

    return scrollbar


# ==========================================================
# LABELED FRAME
# ==========================================================

def create_labeled_frame(
    parent,
    text,
    padding=10,
    **kwargs
):
    """
    Create a reusable labeled frame.
    """

    frame = ttk.LabelFrame(
        parent,
        text=text,
        padding=padding,
        **kwargs
    )

    return frame


# ==========================================================
# STANDARD FRAME
# ==========================================================

def create_frame(
    parent,
    padding=0,
    **kwargs
):
    """
    Create a reusable ttk frame.
    """

    frame = ttk.Frame(
        parent,
        padding=padding,
        **kwargs
    )

    return frame


# ==========================================================
# INFO CARD
# ==========================================================

def create_info_card(
    parent,
    title,
    value,
    width=180
):
    """
    Create a simple statistics/info card.

    This will be useful later for the dashboard.

    Example:

        Total Images
        25
    """

    card = ttk.Frame(
        parent,
        padding=12,
        width=width
    )

    title_label = ttk.Label(
        card,
        text=title,
        font=(
            "Segoe UI",
            9
        )
    )

    title_label.pack(
        anchor=tk.W
    )

    value_label = ttk.Label(
        card,
        text=value,
        font=(
            "Segoe UI",
            18,
            "bold"
        )
    )

    value_label.pack(
        anchor=tk.W,
        pady=(5, 0)
    )

    return card, value_label


# ==========================================================
# PROGRESS BAR
# ==========================================================

def create_progress_bar(
    parent,
    variable=None,
    maximum=100,
    mode="determinate",
    **kwargs
):
    """
    Create a reusable progress bar.
    """

    progress = ttk.Progressbar(
        parent,
        variable=variable,
        maximum=maximum,
        mode=mode,
        **kwargs
    )

    return progress


# ==========================================================
# STATUS LABEL
# ==========================================================

def create_status_label(
    parent,
    textvariable=None,
    text="Ready"
):
    """
    Create a status label.
    """

    label = ttk.Label(
        parent,
        text=text,
        textvariable=textvariable,
        font=(
            "Segoe UI",
            9
        )
    )

    return label


# ==========================================================
# SEPARATOR
# ==========================================================

def create_separator(
    parent,
    orient=tk.HORIZONTAL
):
    """
    Create a reusable separator.
    """

    separator = ttk.Separator(
        parent,
        orient=orient
    )

    return separator


# ==========================================================
# CHECKBOX ROW
# ==========================================================

def create_checkbox_row(
    parent,
    text,
    variable,
    command=None
):
    """
    Create a checkbox row.
    """

    frame = ttk.Frame(
        parent
    )

    checkbox = ttk.Checkbutton(
        frame,
        text=text,
        variable=variable,
        command=command
    )

    checkbox.pack(
        side=tk.LEFT
    )

    return frame, checkbox


# ==========================================================
# LABEL + ENTRY ROW
# ==========================================================

def create_labeled_entry(
    parent,
    label_text,
    variable=None,
    width=15
):
    """
    Create a label and entry pair.

    Returns:
        frame, entry
    """

    frame = ttk.Frame(
        parent
    )

    label = ttk.Label(
        frame,
        text=label_text
    )

    label.pack(
        side=tk.LEFT
    )

    entry = ttk.Entry(
        frame,
        textvariable=variable,
        width=width
    )

    entry.pack(
        side=tk.LEFT,
        padx=(8, 0)
    )

    return frame, entry


# ==========================================================
# LABEL + COMBOBOX ROW
# ==========================================================

def create_labeled_combobox(
    parent,
    label_text,
    values,
    variable=None,
    width=15
):
    """
    Create a label and combobox pair.

    Returns:
        frame, combobox
    """

    frame = ttk.Frame(
        parent
    )

    label = ttk.Label(
        frame,
        text=label_text
    )

    label.pack(
        side=tk.LEFT
    )

    combo = ttk.Combobox(
        frame,
        values=values,
        textvariable=variable,
        state="readonly",
        width=width
    )

    combo.pack(
        side=tk.LEFT,
        padx=(8, 0)
    )

    return frame, combo


# ==========================================================
# BUTTON ROW
# ==========================================================

def create_button_row(
    parent,
    buttons,
    padding=5
):
    """
    Create a horizontal button row.

    Args:
        buttons:
            List of dictionaries.

            Example:

                [
                    {
                        "text": "Add",
                        "command": add_function
                    },
                    {
                        "text": "Clear",
                        "command": clear_function
                    }
                ]

    Returns:
        Frame and button list.
    """

    frame = ttk.Frame(
        parent
    )

    created_buttons = []

    for button_config in buttons:

        text = button_config.get(
            "text",
            "Button"
        )

        command = button_config.get(
            "command"
        )

        button = ttk.Button(
            frame,
            text=text,
            command=command
        )

        button.pack(
            side=tk.LEFT,
            padx=padding
        )

        created_buttons.append(
            button
        )

    return frame, created_buttons


# ==========================================================
# CENTER WINDOW
# ==========================================================

def center_window(
    window,
    width=None,
    height=None
):
    """
    Center a Tkinter window on the screen.
    """

    window.update_idletasks()

    if width is None:

        width = window.winfo_width()

    if height is None:

        height = window.winfo_height()

    screen_width = (
        window.winfo_screenwidth()
    )

    screen_height = (
        window.winfo_screenheight()
    )

    x = int(
        (
            screen_width
            - width
        ) / 2
    )

    y = int(
        (
            screen_height
            - height
        ) / 2
    )

    window.geometry(
        f"{width}x{height}"
        f"+{x}+{y}"
    )


# ==========================================================
# ENABLE / DISABLE WIDGET
# ==========================================================

def set_widget_state(
    widget,
    enabled=True
):
    """
    Enable or disable a ttk widget.
    """

    state = (
        "normal"
        if enabled
        else "disabled"
    )

    try:

        widget.configure(
            state=state
        )

    except tk.TclError:

        pass


# ==========================================================
# CLEAR ENTRY
# ==========================================================

def clear_entry(
    entry
):
    """
    Clear the content of an Entry widget.
    """

    try:

        entry.delete(
            0,
            tk.END
        )

    except tk.TclError:

        pass


# ==========================================================
# SET ENTRY VALUE
# ==========================================================

def set_entry_value(
    entry,
    value
):
    """
    Set the value of an Entry widget.
    """

    try:

        entry.delete(
            0,
            tk.END
        )

        entry.insert(
            0,
            str(value)
        )

    except tk.TclError:

        pass


# ==========================================================
# CLEAR LISTBOX
# ==========================================================

def clear_listbox(
    listbox
):
    """
    Remove all items from a Listbox.
    """

    try:

        listbox.delete(
            0,
            tk.END
        )

    except tk.TclError:

        pass


# ==========================================================
# ADD TO LISTBOX
# ==========================================================

def add_to_listbox(
    listbox,
    items
):
    """
    Add one or multiple items to a Listbox.
    """

    if isinstance(
        items,
        str
    ):

        items = [items]

    for item in items:

        try:

            listbox.insert(
                tk.END,
                str(item)
            )

        except tk.TclError:

            break


# ==========================================================
# UPDATE LABEL
# ==========================================================

def update_label(
    label,
    text
):
    """
    Update label text safely.
    """

    try:

        label.configure(
            text=str(text)
        )

    except tk.TclError:

        pass


# ==========================================================
# UPDATE PROGRESS
# ==========================================================

def update_progress(
    progress,
    value
):
    """
    Update progress bar value.
    """

    try:

        progress["value"] = value

    except (
        tk.TclError,
        TypeError
    ):

        pass