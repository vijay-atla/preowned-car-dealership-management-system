from PIL import Image, ImageEnhance, ImageTk, ImageSequence
import customtkinter as ctk
import os
import tkinter.font as tkFont
import tkinter as tk

def load_background(image_path, size, opacity=1.0):
    """
    Loads and resizes an image with optional opacity adjustment.

    :param image_path: Path to the image file
    :param size: Tuple (width, height) for resizing
    :param opacity: Float (0.0 - 1.0) to adjust opacity (default is 1.0 for full visibility)
    :return: ctk.CTkImage object
    """
    pil_image = Image.open(image_path).convert("RGB")  # Use RGB to avoid darkening
    # Resize image
    pil_image = pil_image.resize(size)

    # Reduce opacity by blending with a white image
    if opacity < 1.0:
        white_overlay = Image.new("RGB", pil_image.size, (255, 255, 255))  # White background
        pil_image = Image.blend(pil_image, white_overlay, 1 - opacity)  # Blend for fade effect

    return ctk.CTkImage(light_image=pil_image, size=size)

def load_icon(image_url, size):
    """ Function to resize an image.
    Args:
    size (tuple): size of the image
    image_url (str): url of the image
    Returns:Resized image
    """
    # Load the original image
    original_image = Image.open(f'{image_url}')
    resized_image = original_image.resize((size[0], size[1]))   
    tk_image = ImageTk.PhotoImage(resized_image)
    return tk_image


def load_iconctk(image_url, size):
    """ Function to resize an image.
    Args:
    size (tuple): size of the image
    image_url (str): url of the image
    Returns:Resized image
    """
    # Load the original image
    # original_image = Image.open(f'{image_url}')
    # resized_image = original_image.resize((size[0], size[1]))   
    # tk_image = ImageTk.PhotoImage(resized_image)
    return ctk.CTkImage(light_image=Image.open(image_url), size=size)



def load_custom_fonts(root, font_folder="F:/PCDS/fonts"):
    """
    Automatically loads all .ttf font files from the specified folder into Tkinter.
    
    Parameters:
    - root: The Tkinter or CustomTkinter root window.
    - font_folder: The folder containing .ttf font files (default: "/mnt/data/").
    
    Returns:
    - A dictionary of loaded fonts with font names as keys.
    """
    loaded_fonts = []

    if not os.path.exists(font_folder):  # Ensure the folder exists
        print(f"Font folder '{font_folder}' not found!")
        return loaded_fonts

    for font_file in os.listdir(font_folder):
        if font_file.endswith(".ttf"):
            font_path = os.path.join(font_folder, font_file)
            font_name = os.path.splitext(font_file)[0]  # Remove .ttf extension
            
            # Load font properly
            root.tk.call("font", "create", font_name, "-family", font_name, "-size", 12)
            loaded_fonts.append(font_path)  # Store font paths (optional)
    
    return loaded_fonts  # Return dictionary of font names and paths



#-----------------------------------------------------------------------------------------------------------------------------


# Global variables for animation control
mini_loader = None
mini_frames = []
mini_animating = False

def show_gif_loader(parent_frame, message="Processing..."):
    global mini_loader, mini_frames, mini_animating

    if mini_loader:
        return

    mini_loader = tk.Toplevel(parent_frame)
    mini_loader.withdraw()
    mini_loader.geometry("500x350")  # Initial placeholder
    mini_loader.overrideredirect(True)
    mini_loader.configure(bg="black")
    mini_loader.attributes("-topmost", True)

    # Center the box using place
    container = tk.Frame(mini_loader, bg="white")
    container.pack(expand=True, fill="both")

    # Floating centered box
    floating_box = tk.Frame(container, bg="white")
    floating_box.place(relx=0.5, rely=0.5, anchor="center")

    # GIF first
    label_gif = tk.Label(floating_box, bg="white")
    label_gif.pack(pady=(0, 0))  # give bottom padding before text

    # Text below GIF
    label_text = tk.Label(floating_box, text=message, fg="black", bg="white", font=("Lato", 14))
    label_text.pack()

    try:
        gif = Image.open("icons/car-dealer-loader-gif.gif")
        mini_frames.clear()
        mini_frames.extend([ImageTk.PhotoImage(f.copy().convert("RGBA")) for f in ImageSequence.Iterator(gif)])
        mini_animating = True
        animate_mini_gif(label_gif, 0)
    except Exception as e:
        label_gif.config(text="(GIF failed)")
        print("GIF Load Error:", e)

    parent_frame.after(100, lambda: finish_loader_placement(parent_frame))

def finish_loader_placement(parent_frame):
    global mini_loader
    if not mini_loader:
        return

    parent_frame.update_idletasks()
    x = parent_frame.winfo_rootx() + parent_frame.winfo_width() // 2 - 250
    y = parent_frame.winfo_rooty() + parent_frame.winfo_height() // 2 - 150
    mini_loader.geometry(f"500x350+{x}+{y}")
    mini_loader.deiconify()



def center_loader_on_frame(parent_frame):
    """Centers the loader window on the parent_frame"""
    global mini_loader
    if not mini_loader:
        return

    parent_frame.update_idletasks()
    x = parent_frame.winfo_rootx() + parent_frame.winfo_width() // 2 - 150
    y = parent_frame.winfo_rooty() + parent_frame.winfo_height() // 2 - 150
    mini_loader.geometry(f"500x350{x}+{y}")

def animate_mini_gif(label, frame_index):
    """Animates the GIF by looping through its frames"""
    global mini_animating, mini_frames

    if not mini_animating or not mini_frames:
        return

    label.configure(image=mini_frames[frame_index])
    label.after(20, lambda: animate_mini_gif(label, (frame_index + 1) % len(mini_frames)))

def hide_loader():
    """Destroys the loader and stops the animation"""
    global mini_loader, mini_animating
    mini_animating = False

    if mini_loader:
        mini_loader.destroy()
        mini_loader = None




#-----------------------------------------------------------------------------------------------------------------------------


def show_custom_message(title, message, type="info", button_text="OK"):
    """
    Display a custom message box.

    Args:
        title (str): Title of the popup window.
        message (str): Message to display inside.
        type (str): "info", "warning", "error", "success"
        button_text (str): Button label (default = "OK")
    """
    popup = ctk.CTkToplevel()
    popup.title(title)
    popup.geometry("400x200")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)
    popup.grab_set()

    # Position popup at center
    popup.update_idletasks()
    w, h = 400, 200
    x = (popup.winfo_screenwidth() // 2) - (w // 2)
    y = (popup.winfo_screenheight() // 2) - (h // 2)
    popup.geometry(f"{w}x{h}+{x}+{y}")

    # Color and Emoji depending on type
    color_map = {
        "info": ("#3498db", "ℹ️"),
        "warning": ("#f39c12", "⚠️"),
        "error": ("#e74c3c", "❌"),
        "success": ("#2ecc71", "✅")
    }

    color, emoji = color_map.get(type, ("#3498db", "ℹ️"))

    # === Title
    title_label = ctk.CTkLabel(popup, text=f"{emoji} {title}", font=("Lato", 18, "bold"), text_color=color)
    title_label.pack(pady=(20, 10))

    # === Message
    message_label = ctk.CTkLabel(popup, text=message, font=("Lato", 14), wraplength=360, justify="center")
    message_label.pack(pady=(0, 20))

    # === OK Button
    ok_btn = ctk.CTkButton(popup, text=button_text, width=100, height=30, 
                           fg_color=color, hover_color=color, text_color="white", 
                           font=("Lato", 14, "bold"), command=popup.destroy)
    ok_btn.pack()

    # Focus on button
    popup.after(100, lambda: ok_btn.focus_force())



#-----------------------------------------------------------------------------------------------------------------------------

def show_custom_confirm(message, on_yes=None, on_no=None, title="Confirm Action", root=None):
    popup = ctk.CTkToplevel(root)
    popup.title(title)
    popup.geometry("360x160")
    popup.attributes("-topmost", True)
    popup.configure(fg_color="#fff9e5", border_color="#ffcc00", border_width=2)

    popup.update_idletasks()
    x = root.winfo_rootx() + 350
    y = root.winfo_rooty() + 220
    popup.geometry(f"+{x}+{y}")

    ctk.CTkLabel( popup,  text=message, font=("Lato", 14, "bold"), text_color="black",  wraplength=300, justify="center" ).place(x=30, y=30)

    def handle_yes():
        popup.destroy()
        if on_yes:
            on_yes()

    def handle_no():
        popup.destroy()
        if on_no:
            on_no()

    ctk.CTkButton(popup, text="Yes", width=100, fg_color="#30b8a9", text_color="black", command=handle_yes).place(x=50, y=100)
    ctk.CTkButton(popup, text="No", width=100, fg_color="#d9534f", text_color="white", command=handle_no).place(x=200, y=100)



#-----------------------------------------------------------------------------------------------------------------------------