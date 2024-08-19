import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import subprocess
import os
import platform
import webbrowser


# Define default parameters
DEFAULT_RESOLUTION = 150
DEFAULT_SCALE_TO = 0  # 0 indicates no scaling


def check_pdftocairo():
    try:
        # Attempt to get the version of pdftocairo
        subprocess.run(["pdftocairo", "-v"], check=True, stdout=subprocess.PIPE)
        status_label.config(text="pdftocairo is already installed.")
    except subprocess.CalledProcessError:
        # Determine the installation command based on the operating system
        system = platform.system()
        if system == 'Linux':
            # For Debian-based Linux distributions
            install_command = ["sudo", "apt-get", "install", "-y", "poppler-utils"]
        elif system == 'Darwin':  # macOS
            # Install poppler using Homebrew
            install_command = ["brew", "install", "poppler"]
        elif system == 'Windows':
            # Windows does not support direct installation, provide a download link
            messagebox.showinfo("Installation Required", 
                                "Please download and install Poppler for Windows from the link below.\n"
                                "https://github.com/oschwartz10612/poppler-windows")
            webbrowser.open("https://github.com/oschwartz10612/poppler-windows")
            return
        else:
            status_label.config(text="Unsupported operating system.")
            return

        # Run the installation command with sudo
        try:
            subprocess.run(install_command, check=True)
            status_label.config(text="Poppler (including pdftocairo) has been installed successfully.")
        except subprocess.CalledProcessError as e:
            status_label.config(text=f"Installation failed: {e}")



def browse_pdf():
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    pdf_entry.delete(0, tk.END)
    pdf_entry.insert(0, pdf_path)

def browse_output():
    # Get the selected format
    output_format = format_var.get()
    print(output_format)
    # Set the default extension
    default_extension = "." + output_format
    print(default_extension)

    # Get the base name of the PDF file
    default_name = os.path.splitext(os.path.basename(pdf_entry.get()))[0]
    print(default_name)

    # Open the save file dialog
    output_path = filedialog.asksaveasfilename(
        initialfile=default_name + default_extension,
    )

    # Update the output file path
    output_entry.delete(0, tk.END)
    output_entry.insert(0, output_path)

def convert_pdf():
    pdf_file = pdf_entry.get()
    output_prefix = output_entry.get()
    output_format = format_var.get()
    scale_to = scale_to_var.get()
    resolution = resolution_var.get()
    crop_x = crop_x_var.get()
    crop_y = crop_y_var.get()
    crop_w = crop_w_var.get()
    crop_h = crop_h_var.get()
    single_file = single_file_var.get()
    nocenter = nocenter_var.get()

    if not pdf_file or not output_prefix:
        status_label.config(text="Please select a PDF file and provide an output prefix.")
        return

    # Build the pdftocairo command
    command = ["pdftocairo", f"-{output_format}"]
    if scale_to:
        command.extend(["-scale-to", str(scale_to)])
    if resolution:
        command.extend(["-r", str(resolution)])
    if crop_x or crop_y or crop_w or crop_h:
        command.extend(["-x", str(crop_x), "-y", str(crop_y), "-W", str(crop_w), "-H", str(crop_h)])
    if single_file:
        command.append("-singlefile")
    if nocenter:
        command.append("-nocenter")
    command.extend([pdf_file, output_prefix])

    try:
        subprocess.run(command, check=True)
        status_label.config(text="Conversion successful.")
    except subprocess.CalledProcessError as e:
        status_label.config(text=f"Conversion failed: {e}")

def preview_first_page():
    pdf_file = pdf_entry.get()

    if not pdf_file:
        status_label.config(text="Please select a PDF file.")
        return

    # Use pdftocairo to convert the first page of the PDF to a temporary PNG file
    temp_png_file = "temp_preview"
    command = ["pdftocairo", "-singlefile", "-png", pdf_file, temp_png_file]

    try:
        subprocess.run(command, check=True)
        
        # Load the temporary PNG file and display it
        img = Image.open(temp_png_file + '.png')
        img.thumbnail((300, 300))  # Resize to fit the preview area
        img_tk = ImageTk.PhotoImage(img)

        # Display the preview in a new Toplevel window
        preview_window = tk.Toplevel(root)
        preview_window.title("PDF Preview")
        preview_label = ttk.Label(preview_window, image=img_tk)
        preview_label.pack()
        preview_label.image = img_tk  # Keep a reference to avoid garbage collection
        status_label.config(text="First page preview loaded.")
    except subprocess.CalledProcessError as e:
        status_label.config(text=f"Preview failed: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_png_file + '.png'):
            os.remove(temp_png_file + '.png')

def show_help():
    help_text = "PDF to Image Converter Usage:\n\n"
    help_text += "1. Select the PDF file you want to convert using the Browse button.\n"
    help_text += "2. Choose the output format from the dropdown menu.\n"
    help_text += "3. Provide a prefix for the output file(s) in the Output Prefix field.\n"
    help_text += "4. Optionally, set the resolution, scale, or cropping parameters.\n"
    help_text += "   - Resolution (DPI): Enter the desired DPI for the output image.\n"
    help_text += "   - Scale To (pixels): Scale the output to a specific pixel size.\n"
    help_text += "   - Crop (X Y W H): Define the area of the PDF page to be cropped.\n"
    help_text += "5. Check the -singlefile box to output only the first page.\n"
    help_text += "6. Check the -nocenter box to disable automatic centering of the output.\n"
    help_text += "7. Click the Convert button to start the conversion process.\n"
    help_text += "8. The status message will indicate whether the conversion was successful."
    messagebox.showinfo("Help", help_text)

# Create the main window
root = tk.Tk()
root.title("PDF to Image Converter")
try:
    root.iconbitmap('icon.ico')

# Use ttk styles
style = ttk.Style()
style.theme_use('clam')  # Change the theme for a more modern look

# Create and place widgets
main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

# PDF file selection
pdf_label = ttk.Label(main_frame, text="Select PDF:")
pdf_label.grid(row=0, column=0, sticky=tk.W)

pdf_entry = ttk.Entry(main_frame, width=50)
pdf_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

browse_pdf_button = ttk.Button(main_frame, text="Browse", command=browse_pdf)
browse_pdf_button.grid(row=0, column=2)

# Add a preview button
preview_button = ttk.Button(main_frame, text="Preview", command=preview_first_page)
preview_button.grid(row=0, column=3)

# Output format selection
format_label = ttk.Label(main_frame, text="Output Format:")
format_label.grid(row=1, column=0, sticky=tk.W)

format_var = tk.StringVar(root)
format_var.set("png")  # Default value
format_options = ["png", "jpeg", "tiff", "pdf", "ps", "eps", "svg"]
format_menu = ttk.OptionMenu(main_frame, format_var, *format_options)
format_menu.grid(row=1, column=1, sticky=(tk.W, tk.E))

# Output prefix
output_label = ttk.Label(main_frame, text="Output Prefix:")
output_label.grid(row=2, column=0, sticky=tk.W)

output_entry = ttk.Entry(main_frame, width=50)
output_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

browse_output_button = ttk.Button(main_frame, text="Browse", command=browse_output)
browse_output_button.grid(row=2, column=2)

# Resolution setting
resolution_label = ttk.Label(main_frame, text="Resolution (DPI):")
resolution_label.grid(row=3, column=0, sticky=tk.W)

resolution_var = tk.IntVar(root, value=DEFAULT_RESOLUTION)
resolution_entry = ttk.Entry(main_frame, width=5, textvariable=resolution_var)
resolution_entry.grid(row=3, column=1, sticky=tk.W)

# Scaling setting
scale_to_label = ttk.Label(main_frame, text="Scale To (pixels):")
scale_to_label.grid(row=4, column=0, sticky=tk.W)

scale_to_var = tk.IntVar(root, value=DEFAULT_SCALE_TO)
scale_to_entry = ttk.Entry(main_frame, width=5, textvariable=scale_to_var)
scale_to_entry.grid(row=4, column=1, sticky=tk.W)

# Cropping settings
crop_label = ttk.Label(main_frame, text="Crop X:")
crop_label.grid(row=5, column=0, sticky=tk.W)
crop_label = ttk.Label(main_frame, text="Crop Y:")
crop_label.grid(row=6, column=0, sticky=tk.W)
crop_label = ttk.Label(main_frame, text="Crop W:")
crop_label.grid(row=7, column=0, sticky=tk.W)
crop_label = ttk.Label(main_frame, text="Crop H:")
crop_label.grid(row=8, column=0, sticky=tk.W)

crop_x_var = tk.IntVar(root)
crop_y_var = tk.IntVar(root)
crop_w_var = tk.IntVar(root)
crop_h_var = tk.IntVar(root)

crop_x_entry = ttk.Entry(main_frame, width=5, textvariable=crop_x_var)
crop_x_entry.grid(row=5, column=1, sticky=tk.W)
crop_y_entry = ttk.Entry(main_frame, width=5, textvariable=crop_y_var)
crop_y_entry.grid(row=6, column=1, sticky=tk.W)
crop_w_entry = ttk.Entry(main_frame, width=5, textvariable=crop_w_var)
crop_w_entry.grid(row=7, column=1, sticky=tk.W)
crop_h_entry = ttk.Entry(main_frame, width=5, textvariable=crop_h_var)
crop_h_entry.grid(row=8, column=1, sticky=tk.W)

# Single file output
single_file_var = tk.BooleanVar(root)
single_file_check = ttk.Checkbutton(main_frame, text="-singlefile", variable=single_file_var)
single_file_check.grid(row=9, column=0, sticky=tk.W)

# Disable centering output
nocenter_var = tk.BooleanVar(root)
nocenter_check = ttk.Checkbutton(main_frame, text="-nocenter", variable=nocenter_var)
nocenter_check.grid(row=9, column=1, sticky=tk.W)

# Button layout
convert_button = ttk.Button(main_frame, text="Convert", command=convert_pdf)
convert_button.grid(row=10, column=0, sticky=tk.W)

# Add a button in the main window to check/install pdftocairo
check_pdftocairo_button = ttk.Button(main_frame, text="Check installation", command=check_pdftocairo)
check_pdftocairo_button.grid(row=10, column=2)


help_button = ttk.Button(main_frame, text="Help", command=show_help)
help_button.grid(row=10, column=3, sticky=tk.W)

# Preview label
preview_label = ttk.Label(main_frame)
preview_label.grid(row=11, column=0, columnspan=2, sticky=tk.W)

# Status label
status_label = ttk.Label(main_frame, text="", foreground="blue")
status_label.grid(row=12, column=0, columnspan=2, sticky=tk.W)

# Main loop
root.mainloop()
