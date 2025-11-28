import tkinter as tk 
import time
from trie import Trie  # Importar tu clase Trie desde trie.py
import nltk
from nltk.corpus import words
import re

# Crear el Trie y agregar palabras de ejemplo
trie = Trie()

# --- Ventana principal ---
root = tk.Tk()
root.title("Editor estilo Word con sugerencias")

# ---- Frame principal con texto y panel lateral ----
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# ---- Widget de texto ----
text_widget = tk.Text(main_frame, wrap="word", width=60, height=20)
text_widget.grid(row=0, column=0, padx=10, pady=10)
text_widget.tag_configure("similar", underline=True, foreground="red")

# ---- Panel lateral para estadísticas ----
side_panel = tk.Frame(main_frame)
side_panel.grid(row=0, column=1, padx=10, pady=10, sticky="n")

label_title = tk.Label(side_panel, text="Estadísticas", font=("Arial", 12, "bold"))
label_title.pack(pady=5)

label_time = tk.Label(side_panel, text="Tiempo: 0.0 ms", font=("Arial", 10))
label_time.pack(pady=5)

label_wordcount = tk.Label(side_panel, text="Palabras: 0", font=("Arial", 10))
label_wordcount.pack(pady=5)

# --- Función para actualizar estadísticas ---
def update_stats(time_seconds, word_count):
    label_time.config(text=f"Tiempo: {time_seconds*1000:.2f} ms")
    label_wordcount.config(text=f"Palabras: {word_count}")

# --- Función NUEVA para analizar todo el texto completo ---
def process_full_text():
    start_time = time.time()

    text = text_widget.get("1.0", "end-1c")
    words_list = re.split(r"[ .,]+", text)
    text_widget.tag_remove("similar", "1.0", tk.END)

    idx = "1.0"

    for word in words_list:
        word = word.lower()
        pos = text_widget.search(word, idx, tk.END)
        if not pos:
            continue

        end_pos = f"{pos}+{len(word)}c"

        # Actualizar Trie si existe
        if trie.search(word):
            trie.insert(word)

        # Verificar palabras similares
        similar = trie.get_similar_words(word, max_distance=3)
        
        if similar and word not in similar:
            text_widget.tag_add("similar", pos, end_pos)

        idx = end_pos

    # Tiempo total
    end_time = time.time()
    elapsed = end_time - start_time

    # Actualizar panel
    update_stats(elapsed, len(words_list))

# --- Función para analizar la última palabra escrita ---
def check_last_word(event=None):
    if event.keysym not in ("space", "Return"):
        return
    process_full_text()

# --- Función para mostrar popup con coincidencias ---
def show_suggestions(event):
    index = text_widget.index(f"@{event.x},{event.y}")
    tags = text_widget.tag_names(index)
    
    if "similar" in tags:
        word_start = text_widget.index(f"{index} wordstart")
        word_end = text_widget.index(f"{index} wordend")
        word = text_widget.get(word_start, word_end)

        similar_words = trie.get_similar_words(word, max_distance=2)

        if similar_words:
            popup = tk.Toplevel(root)
            popup.title("Sugerencias")
            popup.geometry(f"+{event.x_root}+{event.y_root}")
            popup.transient(root)

            label = tk.Label(popup, text=f"Sugerencias para '{word}':")
            label.pack(padx=5, pady=5)

            listbox = tk.Listbox(popup)
            listbox.pack(padx=5, pady=5)
            for s in similar_words:
                listbox.insert(tk.END, s)

            def replace_word(event):
                selection = listbox.get(listbox.curselection())
                text_widget.delete(word_start, word_end)
                text_widget.insert(word_start, selection)
                popup.destroy()

            listbox.bind("<Double-Button-1>", replace_word)

# --- Función para mostrar palabras más frecuentes ---
def show_most_frequent():
    top_words = trie.get_most_frequent_words(trie, top_n=10)
    if not top_words:
        return

    popup = tk.Toplevel(root)
    popup.title("Palabras más frecuentes")
    popup.geometry("+200+200")
    popup.transient(root)

    label = tk.Label(popup, text="Palabras más frecuentes:")
    label.pack(padx=5, pady=5)

    listbox = tk.Listbox(popup, width=50)
    listbox.pack(padx=5, pady=5)

    for word, freq in top_words:
        listbox.insert(tk.END, f"{word} : {freq}")

# ---- Botón para mostrar palabras frecuentes -----
button = tk.Button(root, text="Mostrar palabras frecuentes", command=show_most_frequent)
button.pack(pady=5)

# ---- Botón para procesar texto completo -----
process_button = tk.Button(root, text="Procesar texto completo", command=process_full_text)
process_button.pack(pady=5)

# ------------------ Eventos ---------------------
text_widget.bind("<KeyRelease>", check_last_word)
text_widget.bind("<Button-1>", show_suggestions)

root.mainloop()
