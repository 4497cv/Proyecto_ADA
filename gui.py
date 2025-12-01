import tkinter as tk
from tkinter import font
import re
from trie import Trie  # Asegúrate de que tu clase Trie acepte idioma y número de palabras

# --- Ventana principal ---
root = tk.Tk()
root.title("Editor estilo Word con sugerencias")
root.geometry("800x600")
root.configure(bg="#f8f8f8")

# --- Fuente personalizada ---
text_font = font.Font(family="Roboto", size=12)

# --- Variables de idioma ---
current_language = tk.StringVar(value="en")  # idioma actual
trie = Trie(current_language.get(), 50000)  # Trie inicial en inglés

# --- Función para cambiar idioma ---
def change_language(lang):
    global trie
    trie = Trie(lang, 50000)  # recargar Trie con palabras del idioma seleccionado

# --- Frame principal ---
main_frame = tk.Frame(root, bg="#f8f8f8")
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# --- Widget de texto ---
text_widget = tk.Text(
    main_frame, wrap="word", font=text_font, undo=True, relief="flat", bd=0,
    bg="white", fg="#333333", insertbackground="#333333"
)
text_widget.pack(fill="both", expand=True, side="left", padx=(0,10), pady=10)

# --- Scrollbar ---
scrollbar = tk.Scrollbar(main_frame, command=text_widget.yview)
scrollbar.pack(side="right", fill="y")
text_widget.config(yscrollcommand=scrollbar.set)

# --- Configurar estilos de tags ---
text_widget.tag_configure("similar", underline=True, foreground="#ff4d4f")  # rojo
text_widget.tag_configure("unfound", underline=True, foreground="#1890ff")  # azul

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

    if not suggestions:
        return

    suggestion_popup = tk.Toplevel(root)
    suggestion_popup.wm_overrideredirect(True)
    suggestion_popup.geometry(f"+{event.x_root+10}+{event.y_root+10}")
    suggestion_popup.configure(bg="#2c2c2c")

    label = tk.Label(
        suggestion_popup,
        text=f"Sugerencias para '{word}':",
        bg="#2c2c2c",
        fg="white",
        font=("Roboto", 10, "bold"),
        anchor="w"
    )
    label.pack(fill="x", padx=5, pady=5)

    listbox = tk.Listbox(
        suggestion_popup,
        bg="#2c2c2c",
        fg="white",
        selectbackground="#4a90e2",
        selectforeground="white",
        highlightthickness=0,
        relief="flat",
        font=("Roboto", 10)
    )
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

def show_top_words():
    # Obtener, por ejemplo, las 20 palabras más frecuentes
    top_words = trie.get_most_frequent_words(10)  # tu Trie debe tener un método get_top_words()
    if not top_words:
        return

    popup = tk.Toplevel(root)
    popup.title("Palabras frecuentes")
    popup.geometry("300x400")
    popup.configure(bg="white")

    label = tk.Label(popup, text="Palabras más frecuentes:", font=("Roboto", 10, "bold"), bg="white")
    label.pack(pady=5)

    listbox = tk.Listbox(popup, font=("Roboto", 10), bg="white", fg="#333")
    listbox.pack(fill="both", expand=True, padx=10, pady=10)

    for w in top_words:
        listbox.insert(tk.END, w)

# --- Revisar la última palabra al presionar espacio o Enter ---
def check_last_word(event=None):
    if event.keysym not in ("space", "Return"):
        return

    cursor_index = text_widget.index("insert")
    text_up_to_cursor = text_widget.get("1.0", cursor_index)

    words = [w for w in re.split(r"[\s.,;:!?()\"'-]+", text_up_to_cursor) if w]
    if not words:
        return

    last_word = words[-1].lower()
    start_index = f"{cursor_index} - {len(last_word)+1}c"
    end_index = f"{cursor_index} - 1c"

    # Limpiar tags previos
    text_widget.tag_remove("similar", start_index, end_index)
    text_widget.tag_remove("unfound", start_index, end_index)

    # Verificar la palabra en el Trie
    if trie.search(last_word):
        trie.insert(last_word)
    else:
        similar_words = trie.get_similar_words(last_word, max_distance=2)
        if similar_words:
            text_widget.tag_add("similar", start_index, end_index)
        else:
            text_widget.tag_add("unfound", start_index, end_index)

# --- Botones flotantes y selección de idioma ---
button_frame = tk.Frame(root, bg="#f8f8f8")
button_frame.pack(fill="x", padx=20, pady=10)

tk.Button(button_frame, text="Procesar texto completo", bg="#4a90e2", fg="white", relief="flat", command=lambda: None).pack(side="left", padx=5)
tk.Button(button_frame, text="Mostrar palabras frecuentes", bg="#4a90e2", fg="white", relief="flat", command=show_top_words).pack(side="left", padx=5)
# Menú de idioma
lang_menu = tk.OptionMenu(button_frame, current_language, "en", "es", command=change_language)
lang_menu.config(bg="#4a90e2", fg="white", relief="flat")
lang_menu["menu"].config(bg="white", fg="black")
lang_menu.pack(side="right", padx=5)

# --- Eventos ---
text_widget.bind("<KeyRelease>", check_last_word)
text_widget.bind("<Double-Button-1>", show_suggestions)

# --- Iniciar aplicación ---
root.mainloop()
