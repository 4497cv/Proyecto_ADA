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
        node = self.root
        # iteramos en cada caracter de la palabra
        for char in word:
            # si no encontramos el caracter en el hijo del nodo, insertamos nuevo nodo
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.frequency += 1
        self.all_words.append(word)  # guardamos la palabra/frase

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

    def starts_with(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True


def main():
    nltk.download('words')
    english_words = set(words.words())

    trie = Trie()

    for word in english_words:
        trie.insert(word)

    trie.insert("Hola mundo")

    # Buscar palabra exacta
    print(trie.search("Hola mundo")) 

main()