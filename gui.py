import tkinter as tk
from tkinter import font, filedialog, messagebox
import re
from trie import Trie  # tu clase Trie

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
    process_text()

# --- Funciones de menú ---
def new_file():
    if messagebox.askyesno("Nuevo archivo", "Se perderán los cambios no guardados."):
        text_widget.delete("1.0", tk.END)
        update_word_count()
        update_suggestion_bar("")

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", f.read())
        process_text()
        update_suggestion_bar("")

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_widget.get("1.0", tk.END))

def show_metrics():
    text = text_widget.get("1.0", tk.END)
    words = [w for w in re.findall(r"\b\w+\b", text)]
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
    for w, freq in top_words:
        listbox.insert(tk.END, f"{w} ({freq})")

# --- Función para procesar texto completo ---
def process_text():
    """Procesa todo el texto y aplica tags, ignorando signos de puntuación"""
    text = text_widget.get("1.0", tk.END)
    text_widget.tag_remove("similar", "1.0", tk.END)
    text_widget.tag_remove("unfound", "1.0", tk.END)

    words_list = [w for w in re.findall(r"\b\w+\b", text)]
    found_words, similar_words, unfound_words = trie.process_text_optimized(words_list)

    for match in re.finditer(r"\b\w+\b", text):
        word = match.group()
        start_index = f"1.0 + {match.start()}c"
        end_index = f"1.0 + {match.end()}c"
        word_lower = word.lower()
        if word_lower in found_words:
            continue
        elif any(word_lower == w for w, _ in similar_words):
            text_widget.tag_add("similar", start_index, end_index)
        elif word_lower in unfound_words:
            text_widget.tag_add("unfound", start_index, end_index)

    update_word_count()

# --- Función para pegar y procesar automáticamente ---
def on_paste(event=None):
    text_widget.event_generate("<<Paste>>")
    root.after(10, process_text)
    return "break"

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
text_widget.tag_configure("black", foreground="#333")

# --- Label inferior ---
status_frame = tk.Frame(root, bg="#f8f8f8")
status_frame.pack(fill="x", side="bottom", padx=20, pady=5)

word_count_label = tk.Label(status_frame, text="0 palabras", font=("Roboto", 8), fg="#555", bg="#f8f8f8")
word_count_label.pack(side="left")

language_label = tk.Label(status_frame, text="English", font=("Roboto", 8), fg="#555", bg="#f8f8f8")
language_label.pack(side="right")

suggestion_label = tk.Label(status_frame, text="Sugerencias: ", font=("Roboto", 8), fg="#000", bg="#f8f8f8")
suggestion_label.pack(side="bottom", fill="x", pady=2)

# --- Función para actualizar contador de palabras ---
def update_word_count(event=None):
    text = text_widget.get("1.0", tk.END)
    words = [w for w in re.findall(r"\b\w+\b", text)]
    word_count_label.config(text=f"{len(words)} palabra{'s' if len(words)!=1 else ''}")

# --- Función para actualizar barra de sugerencias ---
def update_suggestion_bar(word):
    """Actualiza la barra inferior con sugerencias de palabras siguientes"""
    if not word.strip():
        suggestion_label.config(text="Sugerencias: ")
        return
    next_words = trie.get_next_words(word.lower())  # obtenemos palabras que siguen
    if next_words:
        suggestion_label.config(text="Sugerencias: " + ", ".join(next_words))
    else:
        suggestion_label.config(text="Sugerencias: (ninguna)")

# --- Sugerencias popup ---
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

    suggestions = []
    if "similar" in tags:
        suggestions = trie.get_similar_words(word, max_distance=2)
    elif "unfound" in tags:
        suggestions = []

    suggestions.append("---")
    suggestions.append("Agregar al diccionario")

    if not suggestions:
        return

    suggestion_popup = tk.Toplevel(root)
    suggestion_popup.wm_overrideredirect(True)
    suggestion_popup.geometry(f"+{event.x_root+10}+{event.y_root+10}")
    suggestion_popup.configure(bg="#2c2c2c")

    def close_popup(event_inner):
        if suggestion_popup and suggestion_popup.winfo_exists():
            suggestion_popup.destroy()
        root.unbind("<Button-1>")

    root.bind("<Button-1>", close_popup)

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
            text_widget.tag_remove("similar", word_start, word_end)
            text_widget.tag_add("black", word_start, word_end)
        elif selection == "---":
            return
        else:
            text_widget.delete(word_start, word_end)
            text_widget.insert(word_start, selection)
            text_widget.tag_remove("unfound", word_start, word_end)
            text_widget.tag_remove("similar", word_start, word_end)
            text_widget.tag_add("black", word_start, word_start + f"+{len(selection)}c")
            trie.insert(selection.lower())

        if suggestion_popup and suggestion_popup.winfo_exists():
            suggestion_popup.destroy()
        root.unbind("<Button-1>")
        check_last_word()
        update_suggestion_bar(selection)

    listbox.bind("<Double-Button-1>", replace_word)

# --- Revisar última palabra ---
def check_last_word(event=None):
    if event and event.keysym not in ("space", "Return", "period", "comma", "exclam", "question"):
        return

    cursor_index = text_widget.index("insert")
    text_up_to_cursor = text_widget.get("1.0", cursor_index)
    words = [w for w in re.findall(r"\b\w+\b", text_up_to_cursor)]
    if not words:
        update_suggestion_bar("")
        return

    last_word = words[-1].lower()
    match_iter = list(re.finditer(r"\b\w+\b", text_up_to_cursor))
    last_match = match_iter[-1]
    start_index = f"1.0 + {last_match.start()}c"
    end_index = f"1.0 + {last_match.end()}c"

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

    # Guardar secuencia de palabras
    if len(words) > 1:
        trie.save_next_words([words[-2], words[-1]])

    # Actualizar barra de sugerencias
    update_suggestion_bar(last_word)

# --- Eventos ---
text_widget.bind("<KeyRelease>", lambda event: [check_last_word(event), update_word_count(event)])
text_widget.bind("<Double-Button-1>", show_suggestions)
text_widget.bind("<ButtonRelease-1>", lambda event: update_suggestion_bar(
    text_widget.get("insert wordstart", "insert wordend")))
text_widget.bind("<Control-v>", lambda e: on_paste())
text_widget.bind("<Shift-Insert>", lambda e: on_paste())

# --- Ejecutar aplicación ---
root.mainloop()
