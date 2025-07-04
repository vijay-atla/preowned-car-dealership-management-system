import customtkinter as ctk
from utils import load_background, load_iconctk
from session import current_user
from database_utils import get_customer_reviewable_purchases

def open_customer_reviews_ratings(root, parent_frame):
    global nroot, main_frame
    nroot = root
    main_frame = parent_frame
    # Clear parent frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # 🎨 Background Illustration
    illustration_image = load_background("icons/default_bg.png", (750, 525), 0.3)
    ctk.CTkLabel(parent_frame, image=illustration_image, text="").place(x=0, y=65)

    # 🏷️ Header Title
    ctk.CTkLabel( parent_frame, image=load_iconctk("icons/reviews_icon.png", (60, 60)), text=" Reviews & Ratings", font=("Lato", 30, "bold"),
        text_color="#008080", fg_color="#ffffff", compound="left" ).place(x=61, y=40)

    # 🙋 Welcome Message
    ctk.CTkLabel( parent_frame, text=f"Welcome, {current_user['full_name'].title()}!", font=("Lato", 20), fg_color="#ffffff"
    ).place(x=450, y=80)

    # 📄 Reviews Label
    ctk.CTkLabel( parent_frame, text="Your Car Reviews", font=("Lato", 16), width=160, height=22
    ).place(x=60, y=153)

    # 📦 Table Frame
    table_frame = ctk.CTkFrame( parent_frame, width=619, height=316, fg_color="#ffffff", corner_radius=10, border_color="#808080",
        border_width=5 )
    table_frame.place(x=65, y=178)


    # 📜 Scrollable Content Placeholder (empty for now)
    scrollable_frame = ctk.CTkScrollableFrame( table_frame, width=580, height=290, fg_color="white", scrollbar_button_color="#D9D9D9" )
    scrollable_frame.place(x=5, y=5)


    # Fetch Purchases + Reviews
    review_data = get_customer_reviewable_purchases(current_user["user_id"])
    if not review_data:
        ctk.CTkLabel(scrollable_frame, text="📦 You haven't made any purchases yet.", font=("Lato", 18, "bold"),
                     text_color="gray").pack(pady=80)
        return


    for row in review_data:
        if row['status'] == "Removed":
            return
        create_review_card(scrollable_frame, row)
    


def create_review_card(parent, data):
    car_name = data["car_name"]
    sale_date = data["sale_date"]
    rating = data["rating"]
    car_id = data["car_id"]
    reviewed = rating is not None

    card = ctk.CTkFrame(parent, height=90, width=620, fg_color="#F5F5F5", corner_radius=10, border_color="#808080", border_width=1)
    card.pack(pady=10)

    # Car Info
    ctk.CTkLabel(card, text=car_name, font=("Lato", 14, "bold")).place(x=20, y=10)
    ctk.CTkLabel(card, text=f"Purchased on: {sale_date}", font=("Lato", 12), text_color="gray").place(x=20, y=35)

    # Star Row
    for i in range(5):
        star = "★" if reviewed and i < rating else "☆"
        lbl = ctk.CTkLabel(card, text=star, font=("Arial", 22), cursor="hand2")
        lbl.place(x=420 + i * 30, y=25)
        lbl.bind("<Button-1>", lambda e, r=i + 1: open_review_popup( car_id, r, parent, existing_rating=rating,
                existing_review=data.get("review_text"), review_id=data.get("review_id")))
    # 👉 Show response from admin/staff if available
    
    if data.get("response_text"):
        response_icon = load_iconctk("icons/response_icon.png", (20, 20))  # use your icon here
        def open_response_popup():
            popup = ctk.CTkToplevel()
            popup.title("Response to Your Review")
            popup.geometry("400x250")
            popup.grab_set()
            popup.focus_force()

            ctk.CTkLabel(popup, text="↪ Response", font=("Lato", 16, "bold")).pack(pady=15)

            msg_box = ctk.CTkTextbox(popup, width=320, height=120, fg_color="#f4f4f4", text_color="#000")
            msg_box.insert("1.0", data["response_text"])
            msg_box.configure(state="disabled")
            msg_box.pack(pady=10)

            ctk.CTkButton(popup, text="Close", command=popup.destroy, width=80).pack(pady=5)

        # Place icon
        icon_label = ctk.CTkLabel(card, image=response_icon, text="", cursor="hand2")
        icon_label.place(x=400, y=60)  # adjust position based on your layout
        icon_label.bind("<Button-1>", lambda e: open_response_popup())




def open_review_popup(car_id, selected_rating, parent_frame, existing_rating=None, existing_review="", review_id=None):
    from tkinter import simpledialog

    # Popup for review
    review_popup = ctk.CTkToplevel()
    review_popup.title("Submit Review")
    review_popup.grab_set()
    review_popup.focus_force()

    # Center on parent_frame
    parent_frame.update_idletasks()
    x = parent_frame.winfo_rootx()
    y = parent_frame.winfo_rooty()
    width = parent_frame.winfo_width()
    height = parent_frame.winfo_height()
    popup_width, popup_height = 400, 300
    center_x = x + (width // 2) - (popup_width // 2)
    center_y = y + (height // 2) - (popup_height // 2)
    review_popup.geometry(f"{popup_width}x{popup_height}+{center_x}+{center_y}")

    if existing_rating:
        selected_rating = existing_rating

    ctk.CTkLabel(review_popup, text="Rate this car", font=("Lato", 18, "bold")).pack(pady=10)

    # Stars
    star_row = ctk.CTkFrame(review_popup, fg_color="#ebebeb")
    star_row.pack(pady=5)
    star_vars = []

    def update_stars(index):
        nonlocal selected_rating
        selected_rating = index + 1
        for i, lbl in enumerate(star_vars):
            lbl.configure(text="★" if i <= index else "☆")

    for i in range(5):
        star = "★" if i < selected_rating else "☆"
        lbl = ctk.CTkLabel(star_row, text=star, font=("Arial", 22), cursor="hand2")
        lbl.pack(side="left", padx=5)
        lbl.bind("<Button-1>", lambda e, i=i: update_stars(i))
        star_vars.append(lbl)

    # Review Text
    ctk.CTkLabel(review_popup, text="Your Review (Optional)", font=("Lato", 14)).pack(pady=(10, 0))
    review_box = ctk.CTkTextbox(review_popup, height=80, width=300)
    review_box.pack(pady=5)

    if existing_review:
        review_box.insert("1.0", existing_review)


    # Submit Button
    def submit_review():
        review_text = review_box.get("1.0", "end").strip()
        
        from database_utils import insert_customer_review, update_customer_review
        if review_id:
            success, msg = update_customer_review(review_id, selected_rating, review_text)
        else:
            success, msg = insert_customer_review(car_id, current_user["user_id"], selected_rating, review_text)
        if success:
            review_popup.destroy()
            open_customer_reviews_ratings(nroot, main_frame)
        else:
            print("[ERROR]", msg)


    ctk.CTkButton(review_popup, text="Submit Review", command=submit_review,
                  fg_color="#008080", text_color="white", width=140).pack(pady=15)     