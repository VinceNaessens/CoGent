from typing import List
from nltk.corpus import wordnet
import nltk

nltk.download('wordnet')
nltk.download('omw-1.4')


def get_synonyms(basis_word: str) -> List[str]:
    synonyms = []
    for syn in wordnet.synsets(basis_word):
        for l in syn.lemmas():
            synonyms.append(l.name())
    synonyms.append(basis_word)

    return list(set(synonyms))
