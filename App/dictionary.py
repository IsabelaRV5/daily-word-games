from english_words import get_english_words_set 

valid_words = set()

# https://pypi.org/project/english-words
word_set = get_english_words_set(['web2'], lower=False)

for word in word_set:
    word = word.upper()
    # keep only alphabet characters
    if word.isalpha():
        valid_words.add(word)