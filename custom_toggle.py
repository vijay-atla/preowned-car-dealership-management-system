import customtkinter as ctk

class ToggleSwitch(ctk.CTkFrame):
    def __init__(self, master, width=50, height=35, on_text="Registered", off_text="Walk-in",
                 on_color="#17b8a6", off_color="#e5e7eb", command=None, initial=False, **kwargs):
        super().__init__(master, width=width, height=height, fg_color=off_color, corner_radius=20, border_color="#b4b4b4", border_width=1 ,**kwargs)
        self.configure(border_width=0)
        self._on_text = on_text
        self._off_text = off_text
        self._on_color = on_color
        self._off_color = off_color
        self._command = command
        self._value = initial
        self._border_color ="#b4b4b4"
        self._border_width = 2

        self.label = ctk.CTkLabel(self, text="", font=("Lato", 12, "bold"), text_color="black")
        self.circle = ctk.CTkFrame(self, width=26, height=26, corner_radius=14, fg_color="#d9d9d9", border_width=2, border_color="#808080")

        self.bind("<Button-1>", self.toggle)
        self.label.bind("<Button-1>", self.toggle)
        self.circle.bind("<Button-1>", self.toggle)

        self._redraw_toggle()

    def _redraw_toggle(self):
        self.configure(fg_color="#17b8a6" if self._value else self._off_color)

        # Move the white knob
        self.circle.place(x=66 if self._value else 8, y=4)

        # Update the label text
        self.label.configure(text=self._on_text if self._value else self._off_text)

        # Move label away from the knob more clearly
        if self._value:  # Registered (ON)
            self.label.place(x=8, y=3)  # Text far left
        else:  # Walk-in (OFF)
            self.label.place(x=40, y=3)  # Text far right



    def toggle(self, event=None):
        self._value = not self._value
        self._redraw_toggle()
        if self._command:
            self._command()

    def get(self):
        return int(self._value)  # 1 for ON (Registered), 0 for OFF (Walk-in)

    def set(self, value: bool):
        self._value = value
        self._redraw_toggle()
