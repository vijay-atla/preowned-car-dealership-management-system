from session import current_user
from login import open_login_screen

def logout_user(root, parent_frame):
    # 1. Clear session data
    current_user.clear()

    # 2. Clear the frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # 3. Reload login screen
    open_login_screen(root)
