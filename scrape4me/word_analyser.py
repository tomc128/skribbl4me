import json
from os import path

import matplotlib.pyplot as plt

COLLATED_WORD_ENCOUNTERS_FILE = 'word_data.json'
collated_word_encounters_path = path.join(path.dirname(path.abspath(__file__)), COLLATED_WORD_ENCOUNTERS_FILE)

with open(collated_word_encounters_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)

words = json_data['words']

# plot a bar chart of word against frequency

top_words = sorted(words, key=lambda word: word['frequency'], reverse=True)[:20]
top_words = [(word['word'], word['frequency']) for word in top_words]

# plot
plt.bar(*zip(*top_words))
plt.xticks(rotation=45)
plt.show()
