import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json

class AnnotationViewerApp:
    def __init__(self, data):
        # Initialize the AnnotationViewerApp with the provided data
        self.data = data
        self.root = tk.Toplevel()
        self.root.title("Annotation Visualization")

        # Create a main frame to contain the Text widget and the statistics widget
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Create a Text widget to display the text
        self.text_widget = tk.Text(main_frame, wrap="word", width=80, height=20)
        self.text_widget.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        # Create a Text widget to display the statistics
        self.probability_text = tk.Text(main_frame, wrap="word", width=20, height=5)
        self.probability_text.pack(side="right", padx=10, pady=10)

        # Create a frame for the legend
        legend_frame = ttk.Frame(self.root)
        legend_frame.pack(side="right", padx=10, pady=10, fill="y")

        # Create a legend for colors and types
        legend_label = ttk.Label(legend_frame, text="Legend:")
        legend_label.grid(row=0, column=0, columnspan=2, padx=5, pady=(0, 5))

        # Define colors for each type of annotated element
        colors = {
            "cell_line": "blue",
            "cell_type": "forestgreen",
            "DNA": "firebrick3",
            "species": "darkturquoise",
            "drug": "darkorchid2",
            "gene": "darkorange2",
            "RNA": "gold2",
            "disease":"mistyrose3"
        }

        # Display the legend
        row = 1
        for obj_type, color in colors.items():
            legend_item_label = ttk.Label(legend_frame, text=obj_type)
            legend_item_label.grid(row=row, column=0, padx=5, sticky="w")
            legend_item_color = ttk.Label(legend_frame, text="      ", background=color)
            legend_item_color.grid(row=row, column=1, padx=5, sticky="w")
            row += 1

        # Insert the text into the Text widget
        self.text_widget.insert(tk.END, self.data["text"])
        self.text_widget.configure(font=("TkDefaultFont", 14))

        # Add annotations to the text with proper highlighting and boldening
        if "annotations" in self.data:
            for annotation in self.data["annotations"]:
                begin = annotation["span"]["begin"]
                end = annotation["span"]["end"]
                obj_type = annotation["obj"]
                mention = annotation["mention"]
                color = colors.get(obj_type, "black")

                # Apply color and bolden the annotation text
                self.text_widget.tag_add(mention, f"1.{begin}", f"1.{end}")
                self.text_widget.tag_config(mention, foreground=color, font=("TkDefaultFont", 14, "bold"))

                # Bind mouse hover to display probability
                self.text_widget.tag_bind(mention, "<Enter>", lambda event, mention=mention: self.show_probability(event, mention))
                self.text_widget.tag_bind(mention, "<Leave>", lambda event: self.probability_text.delete("1.0", "end"))

    def show_probability(self, event, mention):
        # Show probability when mouse hovers over annotation
        prob = self.get_probability(mention)
        self.probability_text.delete("1.0", "end")
        self.probability_text.insert("1.0", f"Probability: {prob}")

    def get_probability(self, mention):
        # Retrieve probability associated with the annotation
        if "annotations" in self.data:
            for annotation in self.data["annotations"]:
                if annotation["mention"] == mention:
                    return str(annotation.get("prob", "")) +" "+ annotation.get("id", "")[0]
        return ""

class MenuApp:
    def __init__(self, root):
        # Initialize the MenuApp
        self.root = root
        self.root.title("Menu App")

        self.file_path = None
        self.data = None

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Define main window dimensions
        window_width = int(screen_width * 0.8)  # 80% of screen width
        window_height = int(screen_height * 0.8)  # 80% of screen height

        # Calculate window coordinates to center it
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Set main window geometry
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Create buttons for file selection and display
        self.button_choose_file = tk.Button(root, text="Choose JSON File", command=self.choose_json_file)
        self.button_choose_file.pack()

        self.button_abstract = tk.Button(root, text="Abstract", command=self.display_abstract, state=tk.DISABLED)
        self.button_abstract.pack()

        self.button_data = tk.Button(root, text="Data", command=self.display_body, state=tk.DISABLED)
        self.button_data.pack()

        self.button_display = tk.Button(root, text="Display", command=self.display, state=tk.DISABLED)
        self.button_display.pack()

    def choose_json_file(self):
        # File selection callback
        self.button_abstract.config(state=tk.DISABLED)
        self.button_data.config(state=tk.DISABLED)
        self.button_display.config(state=tk.DISABLED)
        self.file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if self.file_path:
            with open(self.file_path, 'r') as file:
                self.data = json.load(file)
            if 'abstract' not in self.data and 'data' not in self.data:
                messagebox.showerror("Error", "Neither abstract nor body found in the JSON file.")
                return
            if 'abstract' in self.data:
                self.button_abstract.config(state=tk.NORMAL)
            if 'data' in self.data:
                self.button_data.config(state=tk.NORMAL)

    def display_abstract(self):
        # Display abstract callback
        if self.data and 'abstract' in self.data:
            self.button_display.config(state=tk.NORMAL)
            #self.display_annotations(self.data["abstract"])

    def display_body(self):
        # Display body callback
        if self.data and 'data' in self.data:
            self.button_display.config(state=tk.NORMAL)
            #self.display_annotations(self.data["data"])

    def display_annotations(self, text):
        # Display annotations callback
        annotation_viewer = AnnotationViewerApp({"abstract": text, "annotations": self.data.get("annotations", [])})

    def display(self):
        # Display callback
        annotation_viewer = AnnotationViewerApp(self.data["data"])

if __name__ == "__main__":
    root = tk.Tk()
    app = MenuApp(root)
    root.mainloop()
