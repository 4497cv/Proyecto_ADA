import nltk
from nltk.corpus import words
import time

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.frequency = 0  # contador de uso

class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.all_words = []  # lista para recorrer fácilmente

    def insert(self, word):
        """
        Operacion para insertar una palabra en la estructura Trie.

        Parametros:
            self: Instancia de la clase Trie
            word: palabra o frase a insertar
        """
        # empezamos desde la raiz del arbol
        node = self.root
        
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
            Distancia máxima de edición permitida para considerar palabras similare

        Parametros:
            self:   Instancia de la clase Trie
            word_a: palabra 'A'
            word_b: palabra 'B'
        """
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

# -------------------------------
# Ejemplo de uso
# -------------------------------
def main():
    nltk.download('words')
    english_words = set(words.words())

    trie = Trie()

    for word in english_words:
        trie.insert(word)  # Output: True or False


    trie.insert("Hola mundo")
    trie.insert("Hola mamá")
    trie.insert("Hola mamon")
    trie.insert("Hola amigo")
    trie.insert("truth")
    trie.insert("casa")
    trie.insert("caza")
    trie.insert("cassa")

    # Buscar palabra exacta
    print(trie.search("Hola amigo"))
    # Buscar palabras similares
    print(trie.get_similar_words("Hola mam"))

main()