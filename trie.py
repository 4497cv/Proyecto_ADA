import nltk
from nltk.corpus import words
from nltk.tokenize import sent_tokenize
import time
import spacy
from wordfreq import top_n_list
from word_forms.word_forms import get_word_forms

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.frequency = 0  # contador de uso

class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.all_words = []  # lista para recorrer fácilmente
        self.all_words_set = set()
        # Descargar lista de palabras en inglés y agregarlas al Trie
       # nltk.download('words')

        # english_words = set(words.words())
        # for word in english_words:
        #     self.insert(word)
        
        # nlp = spacy.load("en_core_web_lg")

        # new_w = 0
        # for word in nlp.vocab:
        #     if(word.is_alpha):
        #         self.insert(word.text)
        #         new_w +=1
        
        # self.number_of_words = len(self.all_words)
        # descargar lista de la palabras mas usadas
        words = top_n_list("en", 50000)  # 50k best English words
        
        for w in words:
            # verificar que la palabra no este en la lista de todas las palabras
            if(w not in self.all_words_set):
                # insertar palabra
                self.insert(w)
                # obtener conjugaciones de la palabra w
                forms = get_word_forms(w)
                for n in forms:
                    # verificar si existen conjugaciones de la palbra
                    if(len(forms[n]) > 0):
                        for conjugation in forms[n]:
                            # verificar que elemento no se encuentre en la lista de todas las palabras
                            if(conjugation not in self.all_words_set):
                                self.insert(conjugation)

        print("\nSe han agregado un total de %s palabras a Trie\n" % self.number_of_words)

    def insert(self, word):
        """
        Operacion para insertar una palabra en la estructura Trie.

        Parametros:
            self: Instancia de la clase Trie
            word: palabra o frase a insertar
        """
        # empezamos desde la raiz del arbol
        node = self.root
        word = word.lower()
        
        # iteramos en cada caracter de la palabra
        for char in word:
            if(char not in node.children):
                # insertamos un nodo en el hijo si no encontramos hijos
                node.children[char] = TrieNode()
            
            node = node.children[char]

        # indicamos que es el final del nodo
        node.is_end_of_word = True
        # incrementamos la frecuencia de uso de la palabra
        node.frequency += 1
        # agregamos la palabra a la lista de nuestras palabras usadas
        self.all_words.append(word)
        #actualizamos el numero de palabras
        self.number_of_words = len(self.all_words)
        self.all_words_set.add(word)

    def search(self, word):
        """
        Operacion para buscar una palabra en la estructura Trie.

        Parametros:
            self: Instancia de la clase Trie
            word: palabra o frase a insertar
        """
        ret_val = True
        # empezamos desde la raiz del arbol        
        node = self.root

        # buscamos el caracter en la estructura trie
        for ch in word:
            if(ch not in node.children):
                # nos detenemos si la palabra buscada ya no coincide
                ret_val = False
                break
            # asignamos el nodo como el hijo del anterior
            node = node.children[ch]
        
        # verificamos que sea el final de la palabra y que si lo hayamos encontrado
        if(node.is_end_of_word and ret_val):
            ret_val = True
        else:
            ret_val = False

        return ret_val
        
    def levenshtein_distance(self, word_a, word_b):
        """
        Calcula la distancia de levenshtein entre dos palabras.
        Utiliza programacion dinamica para obtener el edit distance.

        Parametros:
            self:   Instancia de la clase Trie
            word_a: palabra 'A'
            word_b: palabra 'B'
        """
        size_word_a = len(word_a)
        size_word_b = len(word_b)
        dp_filas = size_word_a + 1
        dp_columnas = size_word_b + 1

        # creamos matriz dp llena de ceros (dp_filas x dp_columnas) 
        dp = [[0] * (dp_columnas) for _ in range(dp_filas)]

        # inicializamos primera columna
        for i in range(dp_filas):
            dp[i][0] = i

        # inicializamos primera fila
        for i in range(dp_columnas):
            dp[0][i] = i

        for i in range(1, dp_filas):
            for j in range(1, dp_columnas):
                # calculamos el costo de quitar un caracter
                delete_cost = dp[i-1][j] + 1
                # calculamos el costo de insertar un caracter
                insert_cost = dp[i][j-1] + 1

                # calculamos el corto de sustitucion
                if(word_a[i-1] == word_b[j-1]):
                    subst_cost = dp[i-1][j-1] + 0
                else:
                    subst_cost = dp[i-1][j-1] + 1

                # evaluamos el de menor costo
                min_cost = delete_cost
                
                # validamos si el costo de insertarlo es menor
                if(min_cost > insert_cost):
                    min_cost = insert_cost

                # validamos si el costo de sustituirlo es menor
                if(min_cost > subst_cost):
                    min_cost = subst_cost

                # guardamos la solucion de menor costo
                dp[i][j] = min_cost

        return dp[size_word_a][size_word_b]

    def get_similar_words(self, word, max_distance=2):
        """
        Funcion para obtener las palabras encontradas en la estructura que tengan mayor similitud 
        con la palabra de entrada. 
            
        Se calcula la distancia de Levenshtein (edit distance) entre la palabra
        de entrada y cada palabra almacenada en la estructura, y se devuelven
        aquellas cuyo valor de distancia sea menor a la distancia maxima.

        Parametros:
        self : objeto tipo Trie
            Instancia de la clase Trie que llama a este método.
        word : str
            Palabra de entrada con la que se compararán las demás palabras.
        max_distance : int, opcional (por defecto=2)
            Distancia máxima de edición permitida para considerar palabras similares
        """
        # arreglo para ala
        similar_words = []
        results = []
        word = word.lower()

        frequent_words = self.get_most_frequent_words()

        for w, freq in frequent_words:
            if((w in word) and (len(w)>1)):
                results.append(w)

        if(len(results) > 0):
            return results
        else:
            # arreglo para ala
            similar_words = []
            results = []
            
            # iteramos entre las palabras almacenadas 
            for w in self.all_words:
                # calculamos el edit distance entre la palabra de entrada y la encontrada en la estructura trie
                dist = self.levenshtein_distance(word, w)

                if(dist <= max_distance):
                    similar_words.append((w, dist))

            # ordenamos por menor distancia
            similar_words.sort(key=lambda x: x[1])
            
            for w, _ in similar_words:
                results.append(w)
                
        return results

    def insert_paragraph(self, text):
        """
        Funcion para insertar un texto entero a la estructura de trie. Separa las frases en tokens y las inserta
        a la estructura de trie.

        Parametros:
        self : objeto tipo Trie
            Instancia de la clase Trie que llama a este método.
        text : str
        """
        # Get the list of English words
        tokens_frases = sent_tokenize(text, language="spanish")

        for element in tokens_frases:
            self.insert(element)

    def get_similar_phrases(self, phrase, max_ratio=0.1):
        similar_phrases = []
        for w in self.all_words:
            dist = self.levenshtein_distance(phrase, w)

            if((dist / max(len(phrase), len(w))) <= max_ratio):
                similar_phrases.append(w)

        return similar_phrases

    def get_node_frequency(self, word):
        ret_val = 0
        node = self.root
        for ch in word:
            if(ch not in node.children):
                return 0
            node = node.children[ch]

        if node.is_end_of_word:
            ret_val = node.frequency
        else:
            ret_val = 0
        
        return ret_val

    def get_most_frequent_words(self, top_n=10):
        word_freq = {}
        for word in set(self.all_words):
            freq = self.get_node_frequency(word)
            word_freq[word] = freq
        
        # Ordenar por frecuencia descendente
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_words[:top_n]

def example():
    nltk.download('words')
    english_words = set(words.words())
    trie = Trie()

    for word in english_words:
        trie.insert(word)

    # Buscar palabra exacta
    print(trie.search("Hola amigo"))
    # Buscar palabras similares
    print(trie.get_similar_words("Hola mam"))

    texto = "Procesar un documento para determinar el uso de palabras en relación con otras; es decir, entender el estilo de redacción del autor y, al escribir más texto, recomendar palabras que se asocien con las frases escritas. Debe considerar las palabras utilizadas, el orden en que se emplean, su frecuencia, errores comunes, etc. \
             Además, la aplicación deberá ofrecer un sistema de búsqueda en tiempo real: conforme el usuario escribe cada letra de la frase que desea buscar, se le deben sugerir las n frases más frecuentemente utilizadas que comiencen con esas letras, o con letras similares si se considera que el usuario ha cometido un error de escritura. La cantidad de palabras y frases debe superar las 20,000.\
             Se deben considerar casos en los que el usuario intercambia letras, comete errores ortográficos o une palabras sin espacios. Para las frases, el sistema irá dando sugerencias y registrando las palabras empleadas, de modo que si se vuelve a escribir una frase, se sugiera primero aquella que ya fue utilizada anteriormente."
    
    trie.insert_paragraph(texto)


    print(trie.get_similar_phrases("Procesar un documento"))
    
#example()