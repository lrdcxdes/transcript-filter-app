import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import re

class WordFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Transcript Filter")
        self.root.geometry("600x550") # Adjusted size for better layout
        self.root.resizable(False, False)

        self.input_file_path = None

        # --- GUI Elements ---

        # Frame for file import
        import_frame = tk.Frame(root, padx=10, pady=10)
        import_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(import_frame, text="1. Select Transcript File (.txt or .srt)", font=("Helvetica", 14, "bold")).pack(anchor="w")
        
        self.import_button = tk.Button(import_frame, text="Choose File...", command=self.select_file)
        self.import_button.pack(side="left", pady=5)
        
        self.file_label = tk.Label(import_frame, text="No file selected", fg="gray", wraplength=450)
        self.file_label.pack(side="left", padx=10)

        # Frame for filter configuration
        filter_frame = tk.Frame(root, padx=10, pady=10)
        filter_frame.pack(fill="both", expand=True, padx=10, pady=5)

        tk.Label(filter_frame, text="2. Configure Filter List (format: word_to_find -> replacement)", font=("Helvetica", 14, "bold")).pack(anchor="w")
        
        self.filter_text = scrolledtext.ScrolledText(filter_frame, height=10, width=70, wrap=tk.WORD, undo=True)
        self.filter_text.pack(pady=5, fill="both", expand=True)
        self.filter_text.insert(tk.INSERT, self.get_default_filters())
        
        # Frame for processing and exporting
        export_frame = tk.Frame(root, padx=10, pady=10)
        export_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(export_frame, text="3. Process and Export", font=("Helvetica", 14, "bold")).pack(anchor="w")

        self.export_button = tk.Button(export_frame, text="Export Cleaned File...", font=("Helvetica", 12, "bold"), command=self.process_and_export)
        self.export_button.pack(pady=5)

        # Status bar
        self.status_label = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor="w", padx=10)
        self.status_label.pack(side="bottom", fill="x")

    def get_default_filters(self):
        """Returns a string of default filters to pre-populate the text box."""
        return (
            "# Lines starting with # are ignored. Format is: word -> replacement\n"
            "fuck -> f**k\n"
            "shit -> s**t\n"
            "bitch -> b***h\n"
            "asshole -> a**hole\n"
            "cunt -> c**t\n"
        )

    def select_file(self):
        """Opens a file dialog to select a .txt or .srt file."""
        self.input_file_path = filedialog.askopenfilename(
            title="Select a transcript file",
            filetypes=(("Text files", "*.txt"), ("SubRip files", "*.srt"), ("All files", "*.*"))
        )
        if self.input_file_path:
            self.file_label.config(text=os.path.basename(self.input_file_path), fg="black")
            self.status_label.config(text=f"Selected: {os.path.basename(self.input_file_path)}")
        else:
            self.file_label.config(text="No file selected", fg="gray")
            self.status_label.config(text="Ready")

    def parse_filters(self):
        """Parses the filter text box into a dictionary."""
        filter_map = {}
        filter_data = self.filter_text.get("1.0", tk.END)
        lines = filter_data.split("\n")
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if "->" not in line:
                messagebox.showerror("Filter Error", f"Invalid format on line {i+1}: Missing '->'.\n\nCorrect format: word_to_find -> replacement")
                return None
            
            parts = line.split("->", 1)
            word_to_find = parts[0].strip()
            replacement = parts[1].strip()

            if not word_to_find:
                messagebox.showerror("Filter Error", f"Invalid format on line {i+1}: Word to find cannot be empty.")
                return None
            
            filter_map[word_to_find] = replacement
        
        return filter_map

    def process_and_export(self):
        """Main function to process the file and trigger the save dialog."""
        if not self.input_file_path:
            messagebox.showwarning("Warning", "Please select an input file first.")
            self.status_label.config(text="Error: No input file selected.")
            return

        filter_map = self.parse_filters()
        if filter_map is None:
            self.status_label.config(text="Error: Please fix filter list format.")
            return

        try:
            with open(self.input_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("File Read Error", f"Could not read the input file:\n{e}")
            self.status_label.config(text=f"Error reading file: {e}")
            return

        # Perform case-insensitive replacement using regex for whole words
        cleaned_content = content
        for word, replacement in filter_map.items():
            # Use \b for word boundaries to avoid replacing 'ass' in 'class'
            # re.escape handles special characters in the word to be found
            pattern = r'\b' + re.escape(word) + r'\b'
            cleaned_content = re.sub(pattern, replacement, cleaned_content, flags=re.IGNORECASE)

        # Suggest a default output filename
        input_dir, input_filename = os.path.split(self.input_file_path)
        name, ext = os.path.splitext(input_filename)
        default_output_filename = f"{name}_cleaned{ext}"

        output_path = filedialog.asksaveasfilename(
            initialdir=input_dir,
            initialfile=default_output_filename,
            defaultextension=".txt",
            filetypes=(("Text files", "*.txt"), ("SubRip files", "*.srt"), ("All files", "*.*"))
        )

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
            self.status_label.config(text=f"Error saving file: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = WordFilterApp(root)
    root.mainloop()
