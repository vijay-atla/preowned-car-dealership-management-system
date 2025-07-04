import customtkinter as ctk
from admin_dashboard import open_admin_dashboard
from customer_dashboard import open_customer_dashboard
from staff_dashboard import open_staff_dashboard
import customtkinter as ctk
from home import show_home_screen
from login import open_login_screen
import threading
import time
from utils import show_gif_loader, hide_loader
import pygame

# Initialize main window
ctk.set_appearance_mode("light")

global root
root = ctk.CTk()
root.geometry("900x650")
root.title("Pre-Owned Car Dealership System")
root.resizable(False, False)

main_frame = None

# Load and play engine sound using pygame
def play_engine_sound():
    pygame.mixer.init()
    pygame.mixer.music.load("fonts/engine_start.wav")  # 🔁 Update the path as needed
    pygame.mixer.music.play()

# Display loader first
def startup_sequence():
    show_gif_loader(root, message="🚗 Jump Starting Your Car...")
    
    threading.Thread(target=play_engine_sound).start()
    time.sleep(4)  # duration of the loader
    hide_loader()
    show_home_screen(root)

threading.Thread(target=startup_sequence).start()

root.mainloop()
