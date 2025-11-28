import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import words

# Download the word list if not already done
nltk.download('words')
nltk.download('punkt')
nltk.download('punkt_tab')

# Get the list of English words
english_words = set(words.words())

texto = "Procesar un documento para determinar el uso de palabras en relación con otras; es decir, entender el estilo de redacción del autor y, al escribir más texto, recomendar palabras que se asocien con las frases escritas. Debe considerar las palabras utilizadas, el orden en que se emplean, su frecuencia, errores comunes, etc. \
         Además, la aplicación deberá ofrecer un sistema de búsqueda en tiempo real: conforme el usuario escribe cada letra de la frase que desea buscar, se le deben sugerir las n frases más frecuentemente utilizadas que comiencen con esas letras, o con letras similares si se considera que el usuario ha cometido un error de escritura. La cantidad de palabras y frases debe superar las 20,000.\
         Se deben considerar casos en los que el usuario intercambia letras, comete errores ortográficos o une palabras sin espacios. Para las frases, el sistema irá dando sugerencias y registrando las palabras empleadas, de modo que si se vuelve a escribir una frase, se sugiera primero aquella que ya fue utilizada anteriormente."

tokens_frases = sent_tokenize(texto, language="spanish")


print(tokens_frases)