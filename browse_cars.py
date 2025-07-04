import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from utils import load_background, load_iconctk, hide_loader, show_gif_loader
from database_utils import get_all_car_listings
import tkinter.font as tkFont
from database_utils import search_cars, get_available_makes, get_available_models, get_available_options, get_range_bounds, get_make_model_pairs
from view_car_details import open_view_car_details
from session import current_user


# At the top of browse_cars.py
active_filters = {}



def open_browse_cars(root, main_frame):
    role = current_user["role"]

    def view_car(car):
        car_id = car["car_id"]
        show_gif_loader(main_frame)
        main_frame.after(300, lambda: [open_view_car_details(root, main_frame, car_id=car_id), hide_loader()])

    global active_filters
    active_filters = {}  # Global filter state
    search_timer = None  # declare at the top of open_browse_cars()

    def render_cars(car_list):
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        if not car_list:
            ctk.CTkLabel(scrollable_frame, text="😢 No cars found matching your filters.",
                        font=("Lato", 16, "bold"), text_color="red").pack(pady=20)
            return

        for i, car in enumerate(car_list):
            create_car_card(scrollable_frame, car, i // 2, i % 2)

    def show_sort_popup(anchor_widget):
        global active_filters

        popup = ctk.CTkToplevel()
        popup.title("Sort Options")
        popup.geometry("370x430")
        popup.transient(anchor_widget)
        popup.grab_set()
        popup.attributes("-topmost", True)

        # === Positioning (slightly left)
        x = anchor_widget.winfo_rootx()
        y = anchor_widget.winfo_rooty()
        popup.geometry(f"+{x - 250}+{y - 50}")

        # === Title
        ctk.CTkLabel(popup, text="Sort Options", font=("Lato", 16, "bold")).pack(pady=(10, 5))

        # === Top Button Frame
        button_frame = ctk.CTkFrame(popup, fg_color="#ebebeb")
        button_frame.pack(pady=10)

        sort_vars = {}

        def apply_sort():
            global active_filters
            selected = []
            for field, var in sort_vars.items():
                val = var.get()
                if val != "none":
                    selected.append((field, val))

            if selected:
                active_filters["sort_by"] = selected
                sort_summary = ", ".join([f"{field.title()} ({'↑' if direction == 'asc' else '↓'})" for field, direction in selected])
                sort_entry.configure(placeholder_text=f"Sorted: {sort_summary}")
            else:
                active_filters.pop("sort_by", None)
                sort_entry.configure(placeholder_text="Sort by")

            popup.destroy()
            show_gif_loader(main_frame)
            main_frame.after(300, lambda: [apply_search(), hide_loader()])

        def reset_sort():
            for var in sort_vars.values():
                var.set("none")

        ctk.CTkButton(button_frame, text="Back", fg_color="#d9534f", text_color="white",
                    command=popup.destroy, width=90).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="Reset", fg_color="#cccccc", text_color="black",
                    command=reset_sort, width=90).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="Apply", fg_color="#30b8a9", text_color="black",
                    command=apply_sort, width=90).pack(side="left", padx=10)
        
        # === Scrollable Frame
        scroll_frame = ctk.CTkScrollableFrame(popup, fg_color="white", width=380, height=300)
        scroll_frame.pack(padx=10, pady=5, fill="both", expand=True)

        # === Sort Fields
        sort_options = {
            "price": ["Low → High", "High → Low"],
            "mileage": ["Low → High", "High → Low"],
            "year": ["New → Old", "Old → New"],
            "economy": ["Best → Worst", "Worst → Best"]
        }

        def get_direction(label):
            return "asc" if "Low → High" in label or "Worst → Best" in label or "Old → New" in label else "desc"

        selected_sorts = dict(active_filters.get("sort_by", []))
        for i, (field, labels) in enumerate(sort_options.items()):
            group_frame = ctk.CTkFrame(scroll_frame, fg_color="white")
            group_frame.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="n")

            default_val = selected_sorts.get(field, "none")
            var = tk.StringVar(value=default_val)
            sort_vars[field] = var

            ctk.CTkLabel(group_frame, text=f"Sort by {field.title()}", font=("Lato", 13, "bold")).pack(anchor="w", pady=(0, 5))
            ctk.CTkRadioButton(group_frame, text="None", variable=var, value="none").pack(anchor="w", padx=20)

            for label in labels:
                ctk.CTkRadioButton(group_frame, text=label, variable=var, value=get_direction(label)).pack(anchor="w", padx=20)




    def show_filter_popup(anchor_widget):
        popup = ctk.CTkToplevel()
        popup.title("Filter Cars")
        popup.geometry("600x600")
        popup.transient(anchor_widget)
        popup.grab_set()
        popup.attributes("-topmost", True)

        # # Position below the clicked entry
        # x = anchor_widget.winfo_rootx()
        # y = anchor_widget.winfo_rooty()
        # popup.geometry(f"+{x}+{y + 40}")


        popup.update_idletasks()
        popup_width = 600
        popup_height = 560

        root_x = anchor_widget.winfo_rootx()
        root_y = anchor_widget.winfo_rooty()
        root_width = anchor_widget.winfo_width()
        root_height = anchor_widget.winfo_height()

        x = root_x + root_width // 2 - popup_width // 2 - 50  # shift a bit left
        y = root_y + root_height // 2 - popup_height // 2 + 40  # shift a bit upward

        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")


        def clear_filters():
            global active_filters
            active_filters = {}
            popup.destroy()
            filter_entry.configure(placeholder_text="Filter by")
            apply_search()


        # ===== Apply Logic =====
        def apply_filters():
            global active_filters
            active_filters = {}

            # -- Process multi-filters
            for key, var in filter_vars.items():
                if var.get():
                    col, val = key.split(":", 1)
                    active_filters.setdefault(col, []).append(val)

            # -- Process Make/Model
            for m, v in make_vars.items():
                if v.get():
                    active_filters.setdefault("make", []).append(m)
            for (make, model), v in model_vars.items():
                if v.get():
                    active_filters.setdefault("make", []).append(make)
                    active_filters.setdefault("model", []).append(model)

            # -- Process Ranges
            for key, (min_slider, max_slider) in range_entries.items():
                min_val = int(min_slider.get())
                max_val = int(max_slider.get())
                if min_val <= max_val:
                    active_filters[key] = (min_val, max_val)

            # Count active filters (handle both list and range types)
            # Define default ranges for each slider
            defaults = {
                "price_range": get_range_bounds("price"),
                "mileage_range": get_range_bounds("mileage"),
                "year_range": get_range_bounds("year"),
                "economy_range": get_range_bounds("economy")
            }
            # Count only filters that are actively used
            filter_count = 0
            for key, val in active_filters.items():
                if isinstance(val, list) and val:
                    filter_count += 1
                elif isinstance(val, tuple) and len(val) == 2:
                    min_def, max_def = defaults.get(key, (None, None))
                    if (min_def is not None and max_def is not None) and (val[0] > min_def or val[1] < max_def):
                        filter_count += 1


            filter_entry.configure(placeholder_text=f"Filtered ({filter_count})")
            popup.destroy()
            apply_search()

        # === Button row first
        button_frame = ctk.CTkFrame(popup, fg_color="#ebebeb")
        button_frame.pack(pady=(10, 0))

        ctk.CTkButton(button_frame, text="Back", fg_color="#d9534f", text_color="white",
                    command=popup.destroy, width=90).pack(side="left", padx=10)   
        ctk.CTkButton(button_frame, text="Clear", fg_color="#cccccc", text_color="black",
              command= clear_filters, width=90).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Apply", fg_color="#30b8a9", text_color="black",
                    command=apply_filters, width=90).pack(side="left", padx=10)

        # === Scrollable container
        scroll_frame = ctk.CTkScrollableFrame(popup, width=550, height=550, fg_color="white")
        scroll_frame.pack(pady=5)


        left_pane = ctk.CTkFrame(scroll_frame, fg_color="white")
        left_pane.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        right_pane = ctk.CTkFrame(scroll_frame, fg_color="white")
        right_pane.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        # === Fetch DB values
        fuel_types = get_available_options("fuel_type")
        transmissions = get_available_options("transmission")
        conditions = get_available_options("car_condition")

        filter_vars = {}

        row = 0
        row_right = 0
        


        # ===== MULTI-FILTERS (fuel, transmission, condition, color) =====
        def build_multi_field(title, column_name):
            nonlocal row
            options = get_available_options(column_name)
            if not options:
                return
            ctk.CTkLabel(left_pane, text=title, font=("Lato", 12, "bold")).grid(row=row, column=0, sticky="w", padx=10)
            row += 1
            col_count = 2
            for i, val in enumerate(options):
                var = tk.BooleanVar(value=(val in active_filters.get(column_name, [])))
                cb = ctk.CTkCheckBox(left_pane, text=val, variable=var, height=15, width=15)
                cb.grid(row=row + i // col_count, column=i % col_count, padx=20, sticky="w")
                filter_vars[f"{column_name}:{val}"] = var
            row += (len(options) + 1) // col_count


        build_multi_field("Fuel Type", "fuel_type")
        build_multi_field("Transmission", "transmission")
        build_multi_field("Condition", "car_condition")
        build_multi_field("Color", "car_color")

        # ===== MAKE =====
        ctk.CTkLabel(left_pane, text="Make", font=("Lato", 12, "bold")).grid(row=row, column=0, sticky="w", padx=10)
        row += 1
        makes = get_available_makes()
        selected_makes = []
        make_vars = {}
        col_count=2
        for i, make in enumerate(makes):
            var = tk.BooleanVar(value=(make in active_filters.get("make", [])))
            cb = ctk.CTkCheckBox(left_pane, text=make, variable=var)
            cb.grid(row=row + i // col_count, column=i % col_count, padx=20, sticky="w")
            make_vars[make] = var
        row += (len(makes) + 1) // col_count

        # ===== MODEL (dependent on MAKE) =====
        def update_models():
            nonlocal row
            selected = [m for m, v in make_vars.items() if v.get()]

            # Clear only model checkboxes
            for widget in left_pane.grid_slaves():
                try:
                    widget_text = widget.cget("text")
                    if (
                        widget.grid_info()["row"] >= model_row_start
                        and (isinstance(widget, ctk.CTkCheckBox) or (isinstance(widget, ctk.CTkLabel) and widget_text == "Model"))
                    ):
                        widget.grid_forget()
                except:
                    continue

            model_vars.clear()

            if selected:
                make_model_pairs = get_make_model_pairs(selected_makes)
                if not make_model_pairs:
                    return  # 👈 This prevents extra empty "Model" labels or checkboxes
                row = model_row_start
                ctk.CTkLabel(left_pane, text="Model", font=("Lato", 12, "bold")).grid(row=row, column=0, sticky="w", padx=10)
                row += 1
                col_count = 2
                for i, (make, model) in enumerate(make_model_pairs):
                    display_name = f"{make} {model}"    # 👈 What user sees
                    internal_value = (make, model)      # 👈 What you track internally

                    var = tk.BooleanVar(value=(model in active_filters.get("model", [])))
                    cb = ctk.CTkCheckBox(left_pane, text=display_name, variable=var)
                    cb.grid(row=row + i // col_count, column=i % col_count, padx=20, sticky="w")
                    model_vars[internal_value] = var
                row += (len(make_model_pairs) + 1) // col_count

        model_vars = {}
        model_row_start = row
        for cb in make_vars.values():
            cb.trace_add('write', lambda *_: update_models())

        update_models()



        # ===== RANGE FIELDS =====
        range_entries = {}

        def create_range_slider(parent, label, key, db_column, fallback_min=0, fallback_max=100):
            nonlocal row_right  # assuming you're using global row variable in layout
            min_val, max_val = get_range_bounds(db_column)
            min_val = float(min_val) if min_val is not None else fallback_min
            max_val = float(max_val) if max_val is not None else fallback_max

            # Title label
            ctk.CTkLabel(parent, text=label, font=("Lato", 12, "bold")).grid(row=row_right, column=0, columnspan=2, padx=10, sticky="w")
            row_right += 1


            min_slider = ctk.CTkSlider(parent, from_=min_val, to=max_val, number_of_steps=100, progress_color="#0aa0b3")
            min_slider.set(min_val)
            min_slider.grid(row=row_right, column=0, columnspan=2, padx=20, sticky="ew")
            row_right += 1


            max_slider = ctk.CTkSlider(parent, from_=min_val, to=max_val, number_of_steps=100, progress_color="#d9534f")
            max_slider.set(max_val)
            max_slider.grid(row=row_right, column=0, columnspan=2, padx=20, sticky="ew")
            row_right += 1

            if key in active_filters:
                min_slider.set(active_filters[key][0])
                max_slider.set(active_filters[key][1])


            # Value label
            value_label = ctk.CTkLabel(parent, text=f"{int(min_slider.get())} - {int(max_slider.get())}", font=("Lato", 11, "italic"))
            value_label.grid(row=row_right, column=0, columnspan=2, padx=20, sticky="w")
            row_right += 1


            # Sync sliders
            def update_range_label(*_):
                low = min_slider.get()
                high = max_slider.get()
                if low > high:
                    if _[0] == min_slider:
                        min_slider.set(high)
                    else:
                        max_slider.set(low)
                value_label.configure(text=f"{int(min_slider.get())} - {int(max_slider.get())}")

            min_slider.configure(command=lambda _: update_range_label(min_slider))
            max_slider.configure(command=lambda _: update_range_label(max_slider))

            range_entries[key] = (min_slider, max_slider)





        create_range_slider(right_pane, "Price ($)", "price_range", "price", 1000, 100000)
        create_range_slider(right_pane, "Year", "year_range", "year", 2000, 2025)
        create_range_slider(right_pane, "Mileage (mi)", "mileage_range", "mileage", 0, 150000)
        create_range_slider(right_pane, "Economy (mpg)", "economy_range", "economy", 5, 50)


    def show_filter_with_loader():
        show_gif_loader(root)
        root.after(500, lambda: [show_filter_popup(filter_entry), hide_loader()])


        


    # Illustration
    illustration_image = load_background("icons/default_bg.png", (750, 525), 0.3)
    ctk.CTkLabel(main_frame, image=illustration_image, text="").place(x=0, y=65)    

    # Welcome & Heading
    ctk.CTkLabel(main_frame, image=load_iconctk("icons/browse_car_icon.png", (75, 75)), text=" Browse Cars",
                 font=("Lato", 30, "bold"), text_color="#008080", fg_color="#ffffff", compound="left").place(x=27, y=30)


    if role in ["admin", "staff"]:
        welcome_msg = f"Welcome, {role.title()}, {current_user["full_name"]}!"
    elif role == "customer":
        welcome_msg = f"Welcome, {current_user["full_name"]}!"
    else:
        welcome_msg = "Welcome!"

    ctk.CTkLabel(main_frame, text=welcome_msg.title(), font=("Lato", 20), fg_color="#ffffff").place(x=420, y=62)

    

    # Main Table Frame
    table_frame = ctk.CTkFrame(main_frame, width=715, height=500, fg_color="#ffffff", corner_radius=10, border_color="#808080", border_width=5)
    table_frame.place(x=15, y=130)

    # ctk.CTkFrame(main_frame, fg_color="#808080", width=718, height=5, corner_radius=0).place(x=15, y=187)

    # Top Filters
    search_icon = load_iconctk("icons/search_icon.png", (25, 25))
    filter_icon = load_iconctk("icons/filter_icon.png", (25, 25))
    sort_icon = load_iconctk("icons/sort_icon.png", (25, 25))

    # Search Frame
    search_frame = ctk.CTkFrame(table_frame, width=685, height=43, fg_color="#bababa",
                                corner_radius=10, border_color="#808080", border_width=1)
    search_frame.place(x=14, y=10)


    ctk.CTkLabel(search_frame, image=search_icon, text="").place(x=10, y=7)

    

    search_var = tk.StringVar()
    def apply_search(event=None):
        global active_filters
        show_gif_loader(main_frame)  # ⏳ Show the loader
        main_frame.after(100, lambda: _run_search())  # Delay for smoothness

    def _run_search():
        global active_filters
        query = search_var.get().strip()
        if query.lower() == "search cars...":
            query = ""

        if query == "":
            search_box.delete(0, "end")  # Reset entry
            search_box.configure(placeholder_text="Search Cars...")

        cars = search_cars(search_text=query, filters=active_filters)
        render_cars(cars)
        hide_loader()  # ✅ Hide the loader

    def debounced_search(event=None):
        nonlocal search_timer
        if search_timer:
            search_frame.after_cancel(search_timer)
        search_timer = search_frame.after(600, apply_search)  # 600ms debounce

    # Search, Filter & Add Staff
    search_box = ctk.CTkEntry(search_frame, placeholder_text="Search Cars...", corner_radius=20, width=225, font=("Lato",15))
    search_box.place(x=40, y=7)
    search_box.configure(textvariable=search_var)
    search_box.bind("<FocusIn>", lambda e: search_box.configure(placeholder_text=""))
    search_box.bind("<FocusOut>", lambda e: search_box.configure(placeholder_text="Search Cars..." if not search_var.get().strip() else ""))
    search_box.bind("<KeyRelease>", debounced_search)
    search_box.bind("<Return>", debounced_search)  # Enter key binding
    
    go_btn = ctk.CTkButton(search_frame, text="Go", width=37, height=23, fg_color="#30b8a9", text_color="black", border_width=1, cursor="hand2",
                           border_color="#b4b4b4", font=("Lato", 14), hover_color="#30b8a9", command=apply_search)
    go_btn.place(x=271, y=10)

    filter_icon_label = ctk.CTkLabel(search_frame, image=load_iconctk("icons/filter_icon.png", (20, 20)), text="", compound="left",
                                     font=("Lato", 14), cursor="hand2")
    filter_icon_label.place(x=325, y=9)
    filter_icon_label.bind("<Button-1>", lambda e: show_filter_with_loader())

    filter_entry = ctk.CTkEntry(search_frame, placeholder_text="Filter by", width=100, height=28,
                             border_color="#a7a7a7", corner_radius=5, border_width=1, 
                             text_color="#808080", font=("Lato", 16))
    filter_entry.place(x=350, y=9)
    filter_entry.bind("<Button-1>", lambda e: show_filter_with_loader())
    # ✅ Apply cursor style after creation
    filter_entry._entry.configure(cursor="hand2")

    
    sort_icon_label = ctk.CTkLabel(search_frame, image=sort_icon, text="", cursor = "hand2")
    sort_icon_label.place(x=510, y=9)
    sort_icon_label.bind("<Button-1>", lambda e: show_sort_popup(sort_entry))

    
    sort_entry = ctk.CTkEntry(search_frame, placeholder_text="Sort by", width=100, height=28, border_color="#a7a7a7", corner_radius=5,
                 border_width=1, text_color="#808080", font=("Lato", 16))
    sort_entry.place(x=550, y=9)
    sort_entry._entry.configure(cursor="hand2")
    sort_entry.bind("<Button-1>", lambda e: show_sort_popup(sort_entry))





    # === Scroll Frame Container (inside table_frame, below search_frame) ===
    scroll_container = ctk.CTkFrame(table_frame, width=700, height=430, fg_color="white")
    scroll_container.place(x=5, y=60)


    # Scrollable Car Cards
    scrollable_frame = ctk.CTkScrollableFrame(scroll_container, width=675, height=420, fg_color="white", corner_radius=10,
                                            scrollbar_button_color="#d9d9d9", scrollbar_button_hover_color="#666666")
    scrollable_frame.place(x=0, y=0)



    def create_car_card(parent, car, row, col):

        card = ctk.CTkFrame(parent, width=330, height=100, fg_color="#F0F0F0", corner_radius=10, border_width=2, border_color="#b1b1b1",
                            cursor="hand2")
        card.bind("<Button-1>", lambda e: view_car(car))
        card.grid(row=row, column=col, padx=3, pady=5)

        car_img = load_iconctk(car["img"], (100, 90))
        ctk.CTkLabel(card, image=car_img, text="").place(x=5, y=5)

        # Format and split price
        full_price = f"{car['price']:.2f}"
        main_part, decimal_part = full_price.split(".")

        # Create a font object to measure width
        font_main = tkFont.Font(family="Lato", size=18)
        main_width = font_main.measure(f"${main_part}.")

        ctk.CTkLabel(card, text=car["name"], font=("Lato", 18)).place(x=110, y=5)
        ctk.CTkLabel(card, text=f"$ {main_part}.", font=("Lato", 18)).place(x=110, y=35)
        ctk.CTkLabel(card, text=decimal_part, font=("Lato", 12)).place(x=95 + main_width, y=37.5)
        ctk.CTkLabel(card, text=f"{car['mileage']} mi.", font=("Lato", 12)).place(x=110, y=65)

        icon_color = load_iconctk("icons/color_icon.png", (12, 12))
        icon_trans = load_iconctk("icons/transmission_icon.png", (12, 12))
        icon_fuel = load_iconctk("icons/fuel_icon.png", (12, 12))

        ctk.CTkLabel(card, image=icon_color, text=f"  {car['car_color']}", font=("Lato", 10), height=12, compound="left").place(x=210, y=35)
        ctk.CTkLabel(card, image=icon_trans, text=f"  {car['transmission']}", font=("Lato", 10), height=12, compound="left").place(x=210, y=55)
        ctk.CTkLabel(card, image=icon_fuel, text=f"  {car['fuel_type']}", font=("Lato", 10), height=12, compound="left").place(x=210, y=75)

        for widget in card.winfo_children():
                widget.configure(cursor = "hand2")
                widget.bind("<Button-1>", lambda e, c=car: view_car(c))

    show_gif_loader(main_frame)
    main_frame.after(300, lambda: [apply_search(), hide_loader()]) # Will respect active_filters
  
