import nltk
from nltk.tokenize import word_tokenize

# Generate two general sentences.
# Perform tokenization on them.
# Clean the tokens (lowercase , remove punctuation).
# Counts how many words two sentence have in common.
# Calculate the percentage overlap.

nltk.download('punkt', quiet=True)

def tokenize(text):
    return [t.lower() for t in word_tokenize(text) if t.isalpha()]

def common_word_count(s1, s2):
    return len(set(tokenize(s1)) & set(tokenize(s2)))

def percentage_overlap(s1, s2):
    t1 = set(tokenize(s1))
    t2 = set(tokenize(s2))
    if not (t1 | t2):
        return 0.0
    return len(t1 & t2) / len(t1 | t2) * 100.0

# Example
a = "Natural language processing is fun!"
b = "I find processing natural language quite enjoyable."

print("Tokens A:", tokenize(a))
print("Tokens B:", tokenize(b))
print("Shared count:", common_word_count(a, b))
print(f"Overlap %: {percentage_overlap(a, b):.1f}%")