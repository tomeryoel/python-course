import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet

# Downloads (run once)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)

# Helpers to map NLTK POS tags to WordNet's format
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    if treebank_tag.startswith('V'):
        return wordnet.VERB
    if treebank_tag.startswith('N'):
        return wordnet.NOUN
    if treebank_tag.startswith('R'):
        return wordnet.ADV
    return wordnet.NOUN  # fallback

text = "The striped bats are hanging on their feet and they are better than before."

tokens = word_tokenize(text)
print("Tokens:", tokens)
pos_tags = pos_tag(tokens)
print("Pos Tags:", pos_tags)

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

print("Token | Stemmed | Lemmatized")
for token, pos in pos_tags:
    stem = stemmer.stem(token)
    lemma = lemmatizer.lemmatize(token, get_wordnet_pos(pos))
    print(f"{token:6} | {stem:7} | {lemma}")