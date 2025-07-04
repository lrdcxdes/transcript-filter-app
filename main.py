import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import re
import platform

class WordFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Transcript Filter")
        self.root.geometry("600x550")
        self.root.resizable(False, False)

        self.input_file_path = None
        self.modifier = "Command" if platform.system() == "Darwin" else "Control"

        # --- Элементы GUI ---
        import_frame = tk.Frame(root, padx=10, pady=10)
        import_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(import_frame, text="1. Select Transcript File (.txt or .srt)", font=("Helvetica", 14, "bold")).pack(anchor="w")
        self.import_button = tk.Button(import_frame, text="Choose File...", command=self.select_file)
        self.import_button.pack(side="left", pady=5)
        self.file_label = tk.Label(import_frame, text="No file selected", fg="gray", wraplength=450)
        self.file_label.pack(side="left", padx=10)

        filter_frame = tk.Frame(root, padx=10, pady=10)
        filter_frame.pack(fill="both", expand=True, padx=10, pady=5)
        tk.Label(filter_frame, text="2. Configure Filter List (format: word_to_find -> replacement)", font=("Helvetica", 14, "bold")).pack(anchor="w")
        
        self.filter_text = scrolledtext.ScrolledText(filter_frame, height=10, width=70, wrap=tk.WORD, undo=True)
        self.filter_text.pack(pady=5, fill="both", expand=True)
        self.filter_text.insert(tk.INSERT, self.get_default_filters())

        # *** ФИНАЛЬНЫЙ, ИСПРАВЛЕННЫЙ БЛОК НАСТРОЙКИ ВИДЖЕТА ***
        self._setup_text_widget(self.filter_text)
        
        export_frame = tk.Frame(root, padx=10, pady=10)
        export_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(export_frame, text="3. Process and Export", font=("Helvetica", 14, "bold")).pack(anchor="w")
        self.export_button = tk.Button(export_frame, text="Export Cleaned File...", font=("Helvetica", 12, "bold"), command=self.process_and_export)
        self.export_button.pack(pady=5)
        self.status_label = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor="w", padx=10)
        self.status_label.pack(side="bottom", fill="x")

    def _setup_text_widget(self, widget):
        """Настраивает контекстное меню и ГОРЯЧИЕ КЛАВИШИ, которые теперь РАБОТАЮТ."""
        
        # Функция-обработчик, которая вызывает действие и останавливает событие
        def handle_event(event, virtual_event):
            widget.event_generate(virtual_event)
            return "break"

        # Привязка горячих клавиш
        widget.bind(f"<{self.modifier}-a>", lambda e: handle_event(e, "<<SelectAll>>"))
        widget.bind(f"<{self.modifier}-c>", lambda e: handle_event(e, "<<Copy>>"))
        widget.bind(f"<{self.modifier}-x>", lambda e: handle_event(e, "<<Cut>>"))
        widget.bind(f"<{self.modifier}-v>", lambda e: handle_event(e, "<<Paste>>"))
        widget.bind(f"<{self.modifier}-z>", lambda e: handle_event(e, "<<Undo>>"))
        widget.bind(f"<{self.modifier}-Shift-z>", lambda e: handle_event(e, "<<Redo>>"))
        if platform.system() != "Darwin":
             widget.bind("<Control-y>", lambda e: handle_event(e, "<<Redo>>"))

        # Создание и настройка контекстного меню
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="Undo", command=lambda: widget.event_generate("<<Undo>>"))
        menu.add_command(label="Redo", command=lambda: widget.event_generate("<<Redo>>"))
        menu.add_separator()
        menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: widget.event_generate("<<SelectAll>>"))

        def show_menu(event):
            try:
                has_selection = bool(widget.tag_ranges("sel"))
                can_paste = bool(widget.clipboard_get())
            except tk.TclError:
                can_paste = False
            
            menu.entryconfigure("Cut", state=tk.NORMAL if has_selection else tk.DISABLED)
            menu.entryconfigure("Copy", state=tk.NORMAL if has_selection else tk.DISABLED)
            menu.entryconfigure("Paste", state=tk.NORMAL if can_paste else tk.DISABLED)
            
            menu.tk_popup(event.x_root, event.y_root)

        right_click = "<Button-2>" if platform.system() == "Darwin" else "<Button-3>"
        widget.bind(right_click, show_menu)
        widget.bind("<Control-Button-1>", show_menu)

    def get_default_filters(self):
        return ("# Lines starting with # are ignored. Format is: word -> replacement\n"
                "fuck -> f**k\n"
                "shit -> s**t\n"
                "bitch -> b***h\n"
                "asshole -> a**hole\n"
                "cunt -> c**t\n")

    def select_file(self):
        self.input_file_path = filedialog.askopenfilename(
            title="Select a transcript file",
            filetypes=(("Text files", "*.txt"), ("SubRip files", "*.srt"), ("All files", "*.*")))
        if self.input_file_path:
            self.file_label.config(text=os.path.basename(self.input_file_path), fg="black")
            self.status_label.config(text=f"Selected: {os.path.basename(self.input_file_path)}")
        else:
            self.file_label.config(text="No file selected", fg="gray")
            self.status_label.config(text="Ready")

    def parse_filters(self):
        filter_map = {}
        filter_data = self.filter_text.get("1.0", tk.END)
        for i, line in enumerate(filter_data.split("\n")):
            line = line.strip()
            if not line or line.startswith("#"): continue
            if "->" not in line:
                messagebox.showerror("Filter Error", f"Invalid format on line {i+1}: Missing '->'.\n\nCorrect format: word_to_find -> replacement")
                return None
            parts = line.split("->", 1)
            word_to_find, replacement = parts[0].strip(), parts[1].strip()
            if not word_to_find:
                messagebox.showerror("Filter Error", f"Invalid format on line {i+1}: Word to find cannot be empty.")
                return None
            filter_map[word_to_find] = replacement
        return filter_map

    def process_and_export(self):
        if not self.input_file_path:
            messagebox.showwarning("Warning", "Please select an input file first.")
            return
        filter_map = self.parse_filters()
        if filter_map is None: return
        try:
            with open(self.input_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("File Read Error", f"Could not read the input file:\n{e}")
            return
        cleaned_content = content
        for word, replacement in filter_map.items():
            pattern = r'\b' + re.escape(word) + r'\b'
            cleaned_content = re.sub(pattern, replacement, cleaned_content, flags=re.IGNORECASE)
        input_dir, input_filename = os.path.split(self.input_file_path)
        name, ext = os.path.splitext(input_filename)
        default_output_filename = f"{name}_cleaned{ext}"
        output_path = filedialog.asksaveasfilename(
            initialdir=input_dir, initialfile=default_output_filename,
            defaultextension=ext or ".txt",
            filetypes=(("Text files", "*.txt"), ("SubRip files", "*.srt"), ("All files", "*.*")))
        if not output_path:
            self.status_label.config(text="Export cancelled by user.")
            return
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            messagebox.showinfo("Success", f"File successfully cleaned and saved to:\n{output_path}")
            self.status_label.config(text=f"Successfully exported to {os.path.basename(output_path)}")
        except Exception as e:
            messagebox.showerror("File Write Error", f"Could not save the file:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WordFilterApp(root)
    root.mainloop()
