import tkinter as tk 
import time
from trie import Trie  # Importar tu clase Trie desde trie.py
import re

# Crear el Trie
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
text_widget.tag_configure("unfound", underline=True, foreground="blue")

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


# --- Procesar TODO el texto ---
def process_full_text():
    start_time = time.time()

    text = text_widget.get("1.0", "end-1c")
    words_list = re.split(r"[ .,]+", text)

    # quitar resaltados anteriores
    text_widget.tag_remove("similar", "1.0", tk.END)
    text_widget.tag_remove("unfound", "1.0", tk.END)

    # obtener resultados del Trie
    found_words, similar_words, unfound_words = trie.process_text_optimized(words_list)

    # sets para búsqueda rápida
    similar_set = {w.lower() for w, sug in similar_words}
    unfound_set = {w.lower() for w in unfound_words}

    # recorrer texto y marcar
    for word in words_list:
        w = word.lower()
        if not w:
            continue

        start_idx = "1.0"
        while True:
            pos = text_widget.search(w, start_idx, tk.END, nocase=1)
            if not pos:
                break

            end_pos = f"{pos}+{len(w)}c"

            if w in similar_set:
                text_widget.tag_add("similar", pos, end_pos)

            if w in unfound_set:
                text_widget.tag_add("unfound", pos, end_pos)

            start_idx = end_pos

    elapsed = time.time() - start_time
    update_stats(elapsed, len(words_list))


# --- Analizar última palabra escrita ---
def check_last_word(event=None):
    if event.keysym not in ("space", "Return"):
        return
    process_full_text()


# --- Mostrar sugerencias al hacer clic ---
def show_suggestions(event):
    index = text_widget.index(f"@{event.x},{event.y}")
    tags = text_widget.tag_names(index)

    # ============================
    #   CASO: PALABRA SIMILAR
    # ============================
    if "similar" in tags:
        word_start = text_widget.index(f"{index} wordstart")
        word_end = text_widget.index(f"{index} wordend")
        word = text_widget.get(word_start, word_end)

        # buscar sugerencias directamente del Trie
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

            def replace_word(e):
                selection = listbox.get(listbox.curselection())
                text_widget.delete(word_start, word_end)
                text_widget.insert(word_start, selection)
                popup.destroy()
                process_full_text()

            listbox.bind("<Double-Button-1>", replace_word)


    # ============================
    #   CASO: PALABRA NO ENCONTRADA
    # ============================
    if "unfound" in tags:
        word_start = text_widget.index(f"{index} wordstart")
        word_end = text_widget.index(f"{index} wordend")
        word = text_widget.get(word_start, word_end).lower()

        popup = tk.Toplevel(root)
        popup.title("Palabra desconocida")
        popup.geometry(f"+{event.x_root}+{event.y_root}")
        popup.transient(root)

        label = tk.Label(popup, text=f"'{word}' no está en el diccionario")
        label.pack(padx=5, pady=5)

        def add_word():
            trie.insert(word)

            # quitar azul SOLO a esta palabra antes de recalcular
            text_widget.tag_remove("unfound", word_start, word_end)

            popup.destroy()
            process_full_text()  # recolorear todo

        btn = tk.Button(popup, text="Agregar al diccionario", command=add_word)
        btn.pack(padx=5, pady=10)


# --- Mostrar palabras más frecuentes ---
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
