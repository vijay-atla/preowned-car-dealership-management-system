import customtkinter as ctk
from utils import load_background, load_iconctk, show_custom_message
from session import current_user
from database_utils import get_all_reviews, update_review_status

search_debounce_timer = [None]  # use list so it’s mutable inside nested function

def open_manage_reviews(root, parent_frame):
    global nroot, main_frame
    nroot = root
    main_frame = parent_frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # === Background ===
    bg_img = load_background("icons/default_bg.png", (750, 525), 0.3)
    ctk.CTkLabel(parent_frame, image=bg_img, text="").place(x=0, y=65)

    # === Header ===
    ctk.CTkLabel(parent_frame, image=load_iconctk("icons/reviews_icon.png", (60, 60)), text="  Manage Reviews & Ratings", font=("Lato", 28, "bold"),
                 text_color="#008080", fg_color="#ffffff", compound="left").place(x=40, y=30)
    
    ctk.CTkLabel(parent_frame, text=f"Welcome {current_user['role'].title()}, {current_user['full_name'].title()}!",
                 font=("Lato", 20), fg_color="#ffffff").place(x=400, y=80)


    # === Outer Table Frame ===
    table_frame = ctk.CTkFrame(parent_frame, width=650, height=400, fg_color="#ffffff", corner_radius=10, border_width=5, border_color="#808080")
    table_frame.place(x=40, y=150)

    # === Search Frame ===
    search_frame = ctk.CTkFrame(table_frame, width=630, height=35, fg_color="#BABABA")
    search_frame.place(x=10, y=10)

    status_label = ctk.CTkLabel(search_frame, text="Status", width=90,height=25)
    status_label.place(x=5, y=5)

    ctk.CTkLabel(search_frame, text="", font=("Lato", 14)).place(x=10, y=17)
    status_filter_var = ctk.StringVar(value="All")
    filter_dropdown = ctk.CTkOptionMenu(search_frame, variable=status_filter_var, values=["All", "Active", "Removed"], width=120, height=25,
                                        fg_color="#ffffff", text_color="black")
    filter_dropdown.place(x=75, y=5)

    search_var = ctk.StringVar()
    search_entry = ctk.CTkEntry(search_frame, textvariable=search_var, placeholder_text="Search reviews...", width=250, height=25, corner_radius=15)
    search_entry.place(x=240, y=5)

    search_button = ctk.CTkButton(search_frame, text="Search", width=90,height=25, fg_color="#008080", text_color="black")
    search_button.place(x=510, y=5)
    
    def debounced_search(*args):
        if search_debounce_timer[0]:
            parent_frame.after_cancel(search_debounce_timer[0])

        search_debounce_timer[0] = parent_frame.after(400, refresh_reviews)

    search_var.trace_add("write", debounced_search)

    # === Scrollable Frame for Review Cards ===
    scrollable_frame = ctk.CTkScrollableFrame(table_frame, width=618, height=330, fg_color="#ffffff")
    scrollable_frame._scrollbar.configure(width = 15)
    scrollable_frame.place(x=5, y=50)



    def refresh_reviews():
        status = status_filter_var.get()
        search = search_var.get().strip()
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        reviews = get_all_reviews(search, status)
        if not reviews:
            ctk.CTkLabel(scrollable_frame, text="📝 No reviews found!", font=("Lato", 18, "bold"), text_color="gray").pack(pady=60)
            return

        for row in reviews:
            create_review_card(scrollable_frame, row)

    search_button.configure(command=refresh_reviews)  # ✅ Already defined inside search_frame

    refresh_reviews()


def create_review_card(parent, data):
    from PIL import Image
    card = ctk.CTkFrame(parent, height=90, width=580, fg_color="#F3F3F3", corner_radius=10, border_width=2)
    card.pack(pady=5,  padx=2, fill='x')

    stars = "★" * data["rating"] + "☆" * (5 - data["rating"])
    status_color = "#008000" if data["status"] == "Active" else "#B22222"

    ctk.CTkLabel(card, text=data["car_name"], font=("Lato", 14, "bold")).place(x=20, y=5)
    ctk.CTkLabel(card, text=f"By: {data['customer_name']}", font=("Lato", 12)).place(x=20, y=30)
    ctk.CTkLabel(card, text=f"Rating: {stars}", font=("Arial", 14)).place(x=20, y=55)
    ctk.CTkLabel(card, text=f"\"{data['review_text']}\"", font=("Lato", 11), text_color="gray").place(x=215, y=15)
    ctk.CTkLabel(card, text=f"Status: {data['status']}", font=("Lato", 12, "bold"),
                 text_color=status_color).place(x=480, y=50)

    icon_path = "icons/delete_inquiry_icon.png" if data["status"] == "Active" else "icons/confirm_icon.png"
    action_tooltip = "Remove" if data["status"] == "Active" else "Restore"
    action_icon = load_iconctk(icon_path, (30, 30))

    def handle_action():
        new_status = "Removed" if data["status"] == "Active" else "Active"
        update_review_status(data["review_id"], new_status)
        open_manage_reviews(nroot, main_frame)

    btn = ctk.CTkLabel(card, image=action_icon, text="", cursor="hand2")
    btn.image = action_icon
    btn.place(x=485, y=10)
    btn.bind("<Button-1>", lambda e: handle_action())

    respond_icon = load_iconctk("icons/response_icon.png", (30, 30))  # 📨 your custom icon

    def open_response_popup():
        from tkinter import simpledialog
        popup = ctk.CTkToplevel()
        popup.geometry("400x220")
        popup.title("Respond to Review")
        popup.grab_set()
        popup.focus_force()

        ctk.CTkLabel(popup, text="Write your response:", font=("Lato", 14)).pack(pady=10)
        box = ctk.CTkTextbox(popup, height=80, width=320)
        box.pack(pady=5)

        if data.get("response_text"):
            box.insert("1.0", data["response_text"])

        def submit_response():
            response = box.get("1.0", "end").strip()
            if not response:
                from tkinter import messagebox
                messagebox.showwarning("Validation Error", "Response cannot be empty!")
                return
            
            from database_utils import respond_to_review
            success, msg = respond_to_review(data["review_id"], box.get("1.0", "end").strip())
            popup.destroy()
            if success:
                show_custom_message("Success", "Responded successfully!")
                
                open_manage_reviews(nroot, main_frame)
            else:
                show_custom_message("Error", f"Failed to respond: {msg}", type="error")
            


        ctk.CTkButton(popup, text="Submit", command=submit_response,
                    fg_color="#008080", text_color="white", width=100).pack(pady=10)

    # Place icon
    resp_btn = ctk.CTkLabel(card, image=respond_icon, text="", cursor="hand2")
    resp_btn.image = respond_icon
    resp_btn.place(x=535, y=10)
    resp_btn.bind("<Button-1>", lambda e: open_response_popup())
    # respond_icon = load_iconctk("icons/response_icon.png", (30, 30))

    
