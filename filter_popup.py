import customtkinter as ctk
import tkinter as tk
from database_utils import get_available_options,  get_available_makes, get_available_models, get_range_bounds, get_make_model_pairs
from utils import show_gif_loader, hide_loader


def show_filter_popup(root, anchor_widget, target_entry, apply_search_callback, active_filters, refresh_delay=300):
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
        active_filters.clear()
        popup.destroy()
        target_entry.configure(placeholder_text="Filter by")
        apply_search_callback()


    # ===== Apply Logic =====
    def apply_filters():
        active_filters.clear()

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


        target_entry.configure(placeholder_text=f"Filtered ({filter_count})")
        popup.destroy()
        apply_search_callback()

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
            make_model_pairs = get_make_model_pairs(selected)
            if not make_model_pairs:
                return  # 👈 This prevents extra empty "Model" labels or checkboxes
            row = model_row_start
            ctk.CTkLabel(left_pane, text="Model", font=("Lato", 12, "bold")).grid(row=row, column=0, sticky="w", padx=10)
            row += 1
            col_count = 2
            for i, (make, model) in enumerate(make_model_pairs):

                display_name = f"{make} {model}"  # 👈 Show "Toyota Corolla"
                internal_value = (make, model)    # 👈 Save as tuple for filter


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

