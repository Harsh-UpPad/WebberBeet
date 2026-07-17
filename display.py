import os
import tkinter as tk
from tkinter import ttk, font
import engine  # Imports your standalone parsing engine module

class TkinterBrowserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("webberBeet Separate Engine Browser")
        self.root.geometry("1024x768")

        self.history = []
        self.forward_stack = []

        self.root.rowconfigure(1, weight=3)
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)

        # 1. Navigation Panel Controls
        toolbar = ttk.Frame(self.root, padding="5")
        toolbar.grid(row=0, column=0, sticky="ew")

        self.btn_back = ttk.Button(toolbar, text="◀ Back", width=8, command=self.ui_event_back)
        self.btn_forward = ttk.Button(toolbar, text="Forward ▶", width=10, command=self.ui_event_forward)
        self.btn_refresh = ttk.Button(toolbar, text="⟳ Refresh", width=9, command=self.ui_event_refresh)
        self.btn_home = ttk.Button(toolbar, text="🏠 Home", width=8, command=self.ui_event_home)

        self.btn_back.pack(side=tk.LEFT, padx=2)
        self.btn_forward.pack(side=tk.LEFT, padx=2)
        self.btn_refresh.pack(side=tk.LEFT, padx=2)
        self.btn_home.pack(side=tk.LEFT, padx=2)

        self.btn_back.state(["disabled"])
        self.btn_forward.state(["disabled"])

        self.address_bar = ttk.Entry(toolbar)
        self.address_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.address_bar.bind("<Return>", lambda event: self.ui_event_navigate())

        # 2. Main Viewport Document Canvas
        self.viewport_label = ttk.Label(self.root, text="◤ Web Viewport Content Canvas", anchor="w", font=("Helvetica", 10, "bold"))
        self.viewport_label.grid(row=1, column=0, sticky="nw", padx=5)
        
        self.web_viewport = tk.Text(self.root, font=("Helvetica", 12), wrap="word", bg="#ffffff", fg="#000000", padx=15, pady=15)
        self.web_viewport.grid(row=1, column=0, sticky="nsew", padx=5, pady=(20, 5))
        
        # Define the typographic sizing map
        sizes = {
            "hge": 32,
            "bg": 22,
            "med": 16,
            "sma": 12,
            "ser": 10,
            "tet": 8,
            "normal": 12
        }

        # Dynamically loop and register base, bold, italic, and bold-italic tag configurations
        for tag, size in sizes.items():
            self.web_viewport.tag_configure(tag, font=font.Font(family="Helvetica", size=size))
            self.web_viewport.tag_configure(f"{tag}_bold", font=font.Font(family="Helvetica", size=size, weight="bold"))
            self.web_viewport.tag_configure(f"{tag}_italic", font=font.Font(family="Helvetica", size=size, slant="italic"))
            self.web_viewport.tag_configure(f"{tag}_bi", font=font.Font(family="Helvetica", size=size, weight="bold", slant="italic"))

        # 4. Separate Developer Logs Frame
        self.console_label = ttk.Label(self.root, text="◤ Developer Console Output Log", anchor="w", font=("Helvetica", 10, "bold"))
        self.console_label.grid(row=2, column=0, sticky="nw", padx=5)

        self.console_log = tk.Text(self.root, font=("Courier", 10), wrap="word", bg="#1e1e1e", fg="#d4d4d4", padx=10, pady=10)
        self.console_log.grid(row=2, column=0, sticky="nsew", padx=5, pady=(20, 25))
        self.console_log.insert(tk.END, "[System Initialization]: Modular view engine separated from decoder stack.")
        self.console_log.config(state="disabled")

        self.status_footer = ttk.Label(self.root, text="Status: Ready", anchor="w", padding="3")
        self.status_footer.grid(row=3, column=0, sticky="ew")

        self.load_initial_view()

    def load_initial_view(self):
        self.web_viewport.config(state="normal")
        self.web_viewport.delete("1.0", tk.END)
        self.web_viewport.insert(tk.END, "Enter an absolute path to a (.wb) file above and press Enter.")
        self.web_viewport.config(state="disabled")

    def process_target_path(self, file_path):
        """Passes track data to engine, dynamically registers custom page hex tokens, and paints viewport layouts."""
        self.web_viewport.config(state="normal")
        self.web_viewport.delete("1.0", tk.END)

        if not file_path.lower().endswith('.wb'):
            self.web_viewport.insert(tk.END, "Format Error: Platform requires valid webberBeet (.wb) targets.")
            self.web_viewport.config(state="disabled")
            return

        try:
            if os.path.exists(file_path):
                tokenized_document = engine.parser(file_path)
                
                for line_tokens in tokenized_document:
                    for text_segment, style_tag in line_tokens:
                        
                        # DYNAMIC STYLE REGISTERING: Build hex colors cleanly if passed down by engine
                        if "_color_" in style_tag:
                            if style_tag not in self.web_viewport.tag_names():
                                parts = style_tag.split("_color_")
                                font_style_base = parts[0]  # e.g. "hge_bold" or "normal_formatted"
                                hex_value = f"#{parts[1]}"  # e.g. "#FF0000"
                                
                                # Fall back safely to standard mappings to resolve structural weight settings
                                # Change "normal" to "roman" for the slant fallback configuration
                                weight_setting = "bold" if "bold" in font_style_base or "bi" in font_style_base else "normal"
                                slant_setting = "italic" if "italic" in font_style_base or "bi" in font_style_base else "roman"

                                
                                # Resolve point configuration size steps
                                size_key = font_style_base.split("_")[0]
                                size_map = {"hge": 32, "bg": 22, "med": 16, "sma": 12, "ser": 10, "tet": 8, "normal": 12, "formatted": 12}
                                font_size = size_map.get(size_key, 12)
                                
                                # Bind the dynamic colored font tag configuration to your Tkinter session loop
                                self.web_viewport.tag_configure(
                                    style_tag, 
                                    font=font.Font(family="Helvetica", size=font_size, weight=weight_setting, slant=slant_setting),
                                    foreground=hex_value
                                )
                        
                        self.web_viewport.insert(tk.END, text_segment, style_tag)
                    self.web_viewport.insert(tk.END, "\n", "normal")
            else:
                self.web_viewport.insert(tk.END, f"File System Error 404: File Not Found at absolute track:\n'{file_path}'")
        except Exception as e:
            self.web_viewport.insert(tk.END, f"System Display Interface Read Error:\n\n{str(e)}")
        
        self.web_viewport.config(state="disabled")

    # Navigation Event Hooks
    def ui_event_navigate(self):
        target = self.address_bar.get().strip()
        if target:
            if not self.history or self.history[-1] != target:
                self.history.append(target)
            self.forward_stack.clear()
            self.process_target_path(target)
            self.update_ui_state(f"Navigating file pointer system to: {target}")

    def ui_event_back(self):
        if self.history:
            item = self.history.pop()
            self.forward_stack.append(item)
            self.address_bar.delete(0, tk.END)
            self.address_bar.insert(0, item)
            self.process_target_path(item)
            self.update_ui_state(f"UI Event: Back tracking -> {item}")

    def ui_event_forward(self):
        if self.forward_stack:
            item = self.forward_stack.pop()
            self.history.append(item)
            self.address_bar.delete(0, tk.END)
            self.address_bar.insert(0, item)
            self.process_target_path(item)
            self.update_ui_state(f"UI Event: Forward tracking -> {item}")

    def ui_event_refresh(self):
        current = self.address_bar.get().strip()
        self.process_target_path(current)
        self.update_ui_state(f"UI Event: Refreshing text cache buffer for: {current}")

    def ui_event_home(self):
        self.address_bar.delete(0, tk.END)
        self.load_initial_view()
        self.update_ui_state("UI Event: Core canvas view reset to main screen.")

    def update_ui_state(self, status_message):
        self.status_footer.config(text=f"Status: {status_message}")
        self.console_log.config(state="normal")
        self.console_log.insert(tk.END, f"\n[UI Interaction Logged]: {status_message}")
        self.console_log.see(tk.END)
        self.console_log.config(state="disabled")

        if len(self.history) > 1:
            self.btn_back.state(["!disabled"])
        else:
            self.btn_back.state(["disabled"])

        if len(self.forward_stack) > 0:
            self.btn_forward.state(["!disabled"])
        else:
            self.btn_forward.state(["disabled"])

if __name__ == "__main__":
    root_window = tk.Tk()
    app = TkinterBrowserGUI(root_window)
    root_window.mainloop()
