from wordfreq import top_n_list
from word_forms.word_forms import get_word_forms
import re 

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_eow = False
        self.freq = 0  # contador de uso

class Trie:
    def __init__(self, language = "en", dict_size = 50000):
        self.root = TrieNode()
        self.all_words = []  # lista para recorrer fácilmente
        self.all_words_set = set()
        self.next_words = {}
        self.language = language

        # descargar lista de la palabras mas usadas
        words = top_n_list(language, dict_size)  # 50k best English words
        
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
        node.is_eow = True

        if(node.freq == 0):
            # agregamos la palabra a la lista de nuestras palabras usadas
            self.all_words.append(word)
            self.all_words_set.add(word)

        # incrementamos la frecuencia de uso de la palabra
        node.freq += 1
        #actualizamos el numero de palabras
        self.number_of_words = len(self.all_words)

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
        if(node.is_eow and ret_val):
            ret_val = True
        else:
            ret_val = False

        return ret_val
        
    def levenshtein_distance(self, word_a, word_b, max_distance=2):
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
        diff_word_size = abs(size_word_a - size_word_b) 
        
        # evitar procesamiento si la longitud de ambas palabras es mayor a 2 caracteres
        if(diff_word_size > 2):
            return 99
        
        dp_filas = size_word_a + 1
        dp_columnas = size_word_b + 1

        # creamos matriz dp llena de ceros (dp_filas x dp_columnas) 
        dp = [[0] * (dp_columnas) for _ in range(dp_filas)]

        # inicializamos primera columna
        for i in range(dp_filas):
            dp[i][0] = i

        # inicializamos primera filar
        for i in range(dp_columnas):
            dp[0][i] = i

        for i in range(1, dp_filas):
            fila_min = 999999
            for j in range(1, dp_columnas):
                # calculamos el costo de quitar un caracter
                delete_cost = dp[i-1][j] + 1
                # calculamos el costo de insertar un caracter
                insert_cost = dp[i][j-1] + 1

                if(word_a[i-1] == word_b[j-1]):
                    subst_cost = dp[i-1][j-1]
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
                
                # se guarda la distancia mas pequeña encontraada en la fila
                if min_cost < fila_min:
                    fila_min = min_cost

            if(fila_min > max_distance):
                return 99

        return dp[size_word_a][size_word_b]


    def get_similar_words(self, word, max_distance=2, result_size=5):
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
        similar_words = []
        results = []
        word = word.lower()
        
        # iteramos entre las palabras almacenadas 
        for w in self.all_words:
            if((abs(len(w) - len(word))) > max_distance):
                continue
            
            # calculamos el edit distance entre la palabra de entrada y la encontrada en la estructura trie
            dist = self.levenshtein_distance(word, w, max_distance)

            if(dist <= max_distance):
                similar_words.append((w, dist))

        # ordenamos por menor distancia
        similar_words.sort(key=lambda x: x[1])
        
        for w, _ in similar_words:
            results.append(w)
            
        return results[:result_size]

    def insert_paragraph(self, text):
        """
        Funcion para insertar un texto entero a la estructura de trie. Separa las frases en tokens y las inserta
        a la estructura de trie.

        Parametros:
        self : objeto tipo Trie
            Instancia de la clase Trie que llama a este método.
        text : cadena de texto que contiene un parrafo que se desea insertar a la estructura trie
        """
        # separar las palabras del texto en diferentes tokens
        tokens_frases = sent_tokenize(text, language="spanish")

        for element in tokens_frases:
            self.insert(element)

    def get_node_freq(self, word):
        """
        Funcion para obtener la frecuencia de uso de la palabra. La frecuencia de uso de la palabra se encuentra almacenada
        en el ultimo nodo de la secuencia de la palabra y se lee el valor de esta.

        Parametros:
        self : objeto tipo Trie
            Instancia de la clase Trie que llama a este método.
        word : str
            Palabra de entrada con la que se compararán las demás palabras.
        """
        ret_val = 0
        node = self.root
        for ch in word:
            if(ch not in node.children):
                return 0
            node = node.children[ch]

        if node.is_eow:
            ret_val = node.freq
        else:
            ret_val = 0
        
        return ret_val

    def get_most_frequent_words(self, top_n=10):
        """
        Funcion para obtener las palabras utilizadas con mayor frecuencia.

        Parametros:
        self : objeto tipo Trie
            Instancia de la clase Trie que llama a este método.
        word : str
            palabra a buscar
        len : int
            longitud de palabras iniciales a buscar
        """
        word_freq = {}

        #iteramos entre todas las palabras agregadas a la trie
        for word in self.all_words:
            #obtenemos su frecuencia
            freq = self.get_node_freq(word)
            word_freq[word] = freq
        
        # Ordenar por frecuencia de forma descendente
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        # limitamos el numero de palabras
        sorted_words = sorted_words[:top_n]
        
        return sorted_words
    
    def starts_with(self, word, len=4):
        """
        Funcion para verificar si existe una palabra que comience con las primeras letras, que coincidan
        con el tamaño de la longitud dada a la entrada.

        Parametros:
        self : objeto tipo Trie
            Instancia de la clase Trie que llama a este método.
        word : str
            palabra a buscar
        len : int
            longitud de palabras iniciales a buscar
        """
        # empezamos desde la raiz del arbol        
        node = self.root
        counter = 0
        prefix = word[:len]

        # buscamos el caracter en la estructura trie
        for ch in prefix:
            if(ch not in node.children):
                # nos detenemos si la palabra buscada ya no coincide
                return False
            # asignamos el nodo como el hijo del anterior
            node = node.children[ch]

        return True
    
    def __dfs(self, node, prefix, results, max_lim=3):
        """
        Funcion para realizar busqueda por profundidad DFS para 

        Parametros:
        self : objeto tipo Trie
            Instancia de la clase Trie que llama a este método.
        node : TrieNode
            Nodo de la clase Trie
        prefix : str
            conjunto de letras al inicio de la palabra
        results: list
            resultados encontrados que incluyan el prefijo
        """
        # agregar el prefijo a los resultados si estamos al final de la palabra
        if node.is_eow:
            results.append(prefix)

        for ch, child_node in node.children.items():
            # limitamos la cantidad de resultados a max_lim
            if(len(results) >= max_lim):
                return
            # empleamos recursion y vamos recorriendo los nodos subsecuentes hasta encontrar el final de la palabra
            self.__dfs(child_node, prefix + ch, results)
    
    def autocomplete_prefix(self, prefix):
        """
        Funcion para obtener sugerencias que mas se aproximen a una palabra de un prefijo dado. 

        Parametros:
        self : objeto tipo Trie
            Instancia de la clase Trie que llama a este método.
        prefix : str
            lista de palabras a procesar.
        len : int
            longitud de palabras iniciales a buscar
        """
        if(len(prefix) == 0):
            return []
        
        results = []
        # empezamos desde la raiz del arbol        
        node = self.root

        # buscamos el caracter en la estructura trie
        for ch in prefix:
            if(ch not in node.children):
                # nos detenemos si la palabra buscada ya no coincide
                return []
            # asignamos el nodo como el hijo del anterior
            node = node.children[ch]

        # busqueda por profundidad (DFS)
        self.__dfs(node, prefix, results)
        return results

    def save_next_words(self, words):
        """
        Funcion para guardar el orden de la secuencia de palabras a almacenar en la Trie.

        Parametros:
        self : objeto tipo Trie
            Instancia de la clase Trie que llama a este método.
        words : str
            palabra a procesar
        """       
        word_size = len(words) - 1

        for i in range(word_size):
            # convertir las palabras a minusculas para poder procesarlas
            word_1 = words[i].lower()
            word_2 = words[i + 1].lower()

            # inicializamos si no esta en las palabras siguiente 
            if(word_1 not in self.next_words):
                self.next_words[word_1] = {}

            # inicializamos si no esta en las palabras siguiente de word 1
            if(word_2 not in self.next_words[word_1]):
                self.next_words[word_1][word_2] = 0

            self.next_words[word_1][word_2] += 1
    
    def get_next_words(self, word, n_suggestions=5):
        """
        Funcion para obtener las palabras siguientes de una frase dada.

        Parametros:
        self : objeto tipo Trie
            Instancia de la clase Trie que llama a este método.
        word : str
            palabra a procesar
        len : int
            longitud de palabras iniciales a buscar
        """
        # pasamos la palabra a minusculas para procesarla
        word = word.lower()
        results = []

        # verificamos que la palabra se encuentre en las siguientes palabras
        if word not in self.next_words:
            return []

        # obtenemos las posibles siguientes palabras 
        next_words = self.next_words[word].items()

        # ordenamos de forma acendente 
        next_word_freq = sorted(next_words, key=lambda x: x[1], reverse=True)
        next_word_freq = next_word_freq[:n_suggestions]

        for w, _ in next_word_freq:
            results.append(w)

        return results

    def process_text_optimized(self, words_list, suggestion_size = 3):
        """
        Funcion para realizar el procesamiento de un texto completo. 
        Esta toma todas las palabras del texto y verifica que se encuentren 
        definidas en la estructura Trie y las clasifica de manera que determina
        si existe la palabra, si hay una palabra parecida o no existe y necesita 
        ser agregada.

        Parametros:
        self : objeto tipo Trie
            Instancia de la clase Trie que llama a este método.
        words_list : list
            lista de palabras a procesar.
        len : int
            longitud de palabras iniciales a buscar
        """
        found_words = []
        similar_words = []
        unfound_words = []

        for word in words_list:
            # convertimos la palabra a minusculas
            word = word.lower()
            # primero buscamos si la palabra existe con busqueda rapida
            if(self.search(word)):
                # insertamos la palabra en nuestra estructura para aumentar su frecuencia de uso
                self.insert(word)
                # agregar a lista de palabras encontradas
                found_words.append(word)
            elif(self.starts_with(word, 2)):
                autocomplete = self.autocomplete_prefix(word)
                if(len(autocomplete) > 0):
                    similar_words.append((word, autocomplete))
                    print(similar_words)      
                else:
                    # asumimos que la palabra esta mal escrita y buscamos la que mas se aproxime
                    # obtenemos palabras similares
                    sim_word = self.get_similar_words(word, max_distance=2)
                    # reducir el nuemero de sugerencias
                    sim_word = sim_word[:suggestion_size]

                    # verficar que por lo menos haya una sugerencia
                    if(len(sim_word) > 0):
                        # agregar a palabras similares
                        similar_words.append((word, sim_word))
                    else:
                        # agregar a palabras no encontradas si sim_word esta vacio
                        unfound_words.append(word)
            else:
                # agregar a lista de palabras no encontradas
                unfound_words.append(word)   

        # almacenamos la secuencia de palabras
        self.save_next_words(words_list)

        return found_words, similar_words, unfound_words

def example():
    trie = Trie()

    texto = "Procesar un documento para determinar el uso de palabras en relación con otras; es decir, entender el estilo de redacción del autor y, al escribir más texto, recomendar palabras que se asocien con las frases escritas. Debe considerar las palabras utilizadas, el orden en que se emplean, su frecuencia, errores comunes, etc. \
             Además, la aplicación deberá ofrecer un sistema de búsqueda en tiempo real: conforme el usuario escribe cada letra de la frase que desea buscar, se le deben sugerir las n frases más frecuentemente utilizadas que comiencen con esas letras, o con letras similares si se considera que el usuario ha cometido un error de escritura. La cantidad de palabras y frases debe superar las 20,000.\
             Se deben considerar casos en los que el usuario intercambia letras, comete errores ortográficos o une palabras sin espacios. Para las frases, el sistema irá dando sugerencias y registrando las palabras empleadas, de modo que si se vuelve a escribir una frase, se sugiera primero aquella que ya fue utilizada anteriormente."
    
    text_trial = "Climate change are getting worst every year, and many peoples don’t realize how serius the problem really is. The temperature of the planet rise more faster than scientists was expecting, causing storms and weather events that is totally unpredictable. If we don’t take actions soon, the future generations will have much more dificulties to live in a healthy asdaszxa world."
    words_list = re.split(r"[ .,]+", text_trial)

    trie.insert("structure")
    print(trie.search("structure"))
    test = trie.starts_with("struc")
    print(test)

    found_words, similar_words, unfound_words = trie.process_text_optimized(words_list)

    print("found words:")
    for word in found_words: 
        print(word)
    
    print("similar words:")
    for word, sim_word in similar_words: 
        print(word)
        for w in sim_word:
            print("- %s" % w)
    
    print("unfound_words words:")
    for word in unfound_words: 
        print(word)


    print(trie.autocomplete_prefix("struc"))
    
#example()