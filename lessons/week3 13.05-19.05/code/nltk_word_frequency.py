from nltk.tokenize import word_tokenize
from collections import Counter
import nltk
from nltk.corpus import stopwords

nltk.download('punkt', quiet=True)

text = "Python is great. Python is simple. NLP with Python is powerful!"
tokens = [t.lower() for t in word_tokenize(text)]
freq = Counter(tokens)

print("Tokens:", tokens)
print("Frequencies:", freq)



nltk.download('stopwords', quiet=True)

text = "This is an example showing how tokenization and stopword removal work."
tokens = [t.lower() for t in word_tokenize(text)]
filtered = [t for t in tokens if t.isalpha() and t not in stopwords.words('english')]

print("Original tokens:", tokens)
print("Filtered tokens:", filtered)