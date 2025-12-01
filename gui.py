import tkinter as tk
from tkinter import font, filedialog, messagebox
import re
from trie import Trie

# --- Ventana principal ---
root = tk.Tk()
root.title("Editor estilo Word con sugerencias")
root.geometry("800x600")
root.configure(bg="#f8f8f8")

# --- Fuente ---
text_font = font.Font(family="Roboto", size=12)

# --- Variables de idioma ---
current_language = tk.StringVar(value="en")
trie = Trie(current_language.get(), 50000)

# --- Función para cambiar idioma ---
def change_language(lang):
    global trie
    current_language.set(lang)
    trie = Trie(lang, 50000)
    language_label.config(text="English" if lang == "en" else "Spanish")

# --- Funciones de menú ---
def new_file():
    if messagebox.askyesno("Nuevo archivo", "Se perderán los cambios no guardados."):
        text_widget.delete("1.0", tk.END)
        update_word_count()

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", f.read())
        update_word_count()

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_widget.get("1.0", tk.END))

def show_metrics():
    text = text_widget.get("1.0", tk.END)
    words = [w for w in re.split(r"[\s.,;:!?()\"'-]+", text) if w]
    messagebox.showinfo("Metrics", f"Número de palabras: {len(words)}")

def show_word_frequency():
    top_words = trie.get_most_frequent_words(10)
    if not top_words:
        messagebox.showinfo("Word Frequency", "No hay palabras frecuentes todavía.")
        return
    popup = tk.Toplevel(root)
    popup.title("Word Frequency")
    popup.geometry("300x400")
    popup.configure(bg="white")
    label = tk.Label(popup, text="Palabras más frecuentes:", font=("Roboto", 10, "bold"), bg="white")
    label.pack(pady=5)
    listbox = tk.Listbox(popup, font=("Roboto", 10), bg="white", fg="#333")
    listbox.pack(fill="both", expand=True, padx=10, pady=10)
    for w in top_words:
        listbox.insert(tk.END, w)

def process_text():
    """Procesa todo el texto, aplica tags y actualiza Trie"""
    text = text_widget.get("1.0", tk.END)
    words = [w for w in re.split(r"([\s.,;:!?()\"'-]+)", text) if w]  # Mantener separadores
    text_widget.tag_remove("similar", "1.0", tk.END)
    text_widget.tag_remove("unfound", "1.0", tk.END)

    index = "1.0"
    for w in words:
        if re.fullmatch(r"[\s.,;:!?()\"'-]+", w):  # separadores
            index = text_widget.index(f"{index} + {len(w)}c")
            continue

        w_lower = w.lower()
        start_index = index
        end_index = text_widget.index(f"{start_index} + {len(w)}c")

        if trie.search(w_lower):
            trie.insert(w_lower)
        else:
            similar_words = trie.get_similar_words(w_lower, max_distance=2)
            if similar_words:
                text_widget.tag_add("similar", start_index, end_index)
            else:
                text_widget.tag_add("unfound", start_index, end_index)

        index = end_index

    update_word_count()
    messagebox.showinfo("Process Text", "Procesamiento completo finalizado.")

# --- Menú superior ---
menu_bar = tk.Menu(root)

file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

metrics_menu = tk.Menu(menu_bar, tearoff=0)
metrics_menu.add_command(label="Show Metrics", command=show_metrics)
metrics_menu.add_command(label="Word Frequency", command=show_word_frequency)
menu_bar.add_cascade(label="Metrics", menu=metrics_menu)

process_menu = tk.Menu(menu_bar, tearoff=0)
process_menu.add_command(label="Process Text", command=process_text)
menu_bar.add_cascade(label="Process Text", menu=process_menu)

settings_menu = tk.Menu(menu_bar, tearoff=0)
language_menu = tk.Menu(settings_menu, tearoff=0)
language_menu.add_command(label="English", command=lambda: change_language("en"))
language_menu.add_command(label="Spanish", command=lambda: change_language("es"))
settings_menu.add_cascade(label="Change Language", menu=language_menu)
menu_bar.add_cascade(label="Settings", menu=settings_menu)

root.config(menu=menu_bar)

# --- Frame principal para texto ---
main_frame = tk.Frame(root, bg="#f8f8f8")
main_frame.pack(fill="both", expand=True, padx=20, pady=5)

text_widget = tk.Text(main_frame, wrap="word", font=text_font, undo=True,
                      relief="flat", bd=0, bg="white", fg="#333", insertbackground="#333")
text_widget.pack(fill="both", expand=True, side="left")

scrollbar = tk.Scrollbar(main_frame, command=text_widget.yview)
scrollbar.pack(side="right", fill="y")
text_widget.config(yscrollcommand=scrollbar.set)

text_widget.tag_configure("similar", underline=True, foreground="#ff4d4f")
text_widget.tag_configure("unfound", underline=True, foreground="#1890ff")

# --- Label inferior (izquierda y derecha) ---
status_frame = tk.Frame(root, bg="#f8f8f8")
status_frame.pack(fill="x", side="bottom", padx=20, pady=5)

word_count_label = tk.Label(status_frame, text="0 palabras", font=("Roboto", 8), fg="#555", bg="#f8f8f8")
word_count_label.pack(side="left")

language_label = tk.Label(status_frame, text="English", font=("Roboto", 8), fg="#555", bg="#f8f8f8")
language_label.pack(side="right")

# --- Función para actualizar contador de palabras ---
def update_word_count(event=None):
    text = text_widget.get("1.0", tk.END)
    words = [w for w in re.split(r"[\s.,;:!?()\"'-]+", text) if w]
    word_count_label.config(text=f"{len(words)} palabra{'s' if len(words)!=1 else ''}")

# --- Función para mostrar sugerencias ---
suggestion_popup = None
def show_suggestions(event):
    global suggestion_popup
    if suggestion_popup and suggestion_popup.winfo_exists():
        suggestion_popup.destroy()
    index = text_widget.index(f"@{event.x},{event.y}")
    tags = text_widget.tag_names(index)
    word_start = text_widget.index(f"{index} wordstart")
    word_end = text_widget.index(f"{index} wordend")
    word = text_widget.get(word_start, word_end)
    if "similar" in tags:
        suggestions = trie.get_similar_words(word, max_distance=2)
    elif "unfound" in tags:
        suggestions = ["Agregar al diccionario"]
    else:
        return
    if not suggestions: return
    suggestion_popup = tk.Toplevel(root)
    suggestion_popup.wm_overrideredirect(True)
    suggestion_popup.geometry(f"+{event.x_root+10}+{event.y_root+10}")
    suggestion_popup.configure(bg="#2c2c2c")
    label = tk.Label(suggestion_popup, text=f"Sugerencias para '{word}':",
                     bg="#2c2c2c", fg="white", font=("Roboto", 10, "bold"), anchor="w")
    label.pack(fill="x", padx=5, pady=5)
    listbox = tk.Listbox(suggestion_popup, bg="#2c2c2c", fg="white",
                         selectbackground="#4a90e2", selectforeground="white",
                         highlightthickness=0, relief="flat", font=("Roboto", 10))
    listbox.pack(fill="both", padx=5, pady=5)
    for s in suggestions:
        listbox.insert(tk.END, s)
    def replace_word(e):
        selection = listbox.get(listbox.curselection())
        if selection == "Agregar al diccionario":
            trie.insert(word.lower())
            text_widget.tag_remove("unfound", word_start, word_end)
        else:
            text_widget.delete(word_start, word_end)
            text_widget.insert(word_start, selection)
        suggestion_popup.destroy()
    listbox.bind("<Double-Button-1>", replace_word)

# --- Revisar última palabra ---
def check_last_word(event=None):
    if event.keysym not in ("space", "Return"): return
    cursor_index = text_widget.index("insert")
    text_up_to_cursor = text_widget.get("1.0", cursor_index)
    words = [w for w in re.split(r"[\s.,;:!?()\"'-]+", text_up_to_cursor) if w]
    if not words: return
    last_word = words[-1].lower()
    start_index = f"{cursor_index} - {len(last_word)+1}c"
    end_index = f"{cursor_index} - 1c"
    text_widget.tag_remove("similar", start_index, end_index)
    text_widget.tag_remove("unfound", start_index, end_index)
    if trie.search(last_word):
        trie.insert(last_word)
    else:
        similar_words = trie.get_similar_words(last_word, max_distance=2)
        if similar_words:
            text_widget.tag_add("similar", start_index, end_index)
        else:
            text_widget.tag_add("unfound", start_index, end_index)

# --- Eventos ---
text_widget.bind("<KeyRelease>", lambda event: [check_last_word(event), update_word_count(event)])
text_widget.bind("<Double-Button-1>", show_suggestions)

# --- Ejecutar aplicación ---
root.mainloop()
