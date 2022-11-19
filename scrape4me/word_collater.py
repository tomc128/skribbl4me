from os import path
import json

RAW_WORD_ENCOUNTERS_FILE = 'word_encounters.txt'
COLLATED_WORD_ENCOUNTERS_FILE = 'word_data.json'

raw_word_encounters_path = path.join(path.dirname(path.abspath(__file__)), RAW_WORD_ENCOUNTERS_FILE)
collated_word_encounters_path = path.join(path.dirname(path.abspath(__file__)), COLLATED_WORD_ENCOUNTERS_FILE)

word_encounters: dict[str, int] = {}
total_word_encounters = 0

with open(raw_word_encounters_path, 'r', encoding='utf-8') as file:
    for line in file:
        word = line.strip()
        if word not in word_encounters:
            word_encounters[word] = 0
        
        word_encounters[word] += 1
        total_word_encounters += 1

avg_frequency = total_word_encounters / len(word_encounters)

print(f'Loaded {len(word_encounters)} unique words out of {total_word_encounters} total word encounters')
print(f'Each word has been seen on average {avg_frequency:.2f} times')

# sort alphabetically
word_encounters = dict(sorted(word_encounters.items(), key=lambda item: item[0]))

json_data = {
    'total_word_encounters': total_word_encounters,
    'unique_words': len(word_encounters),
    'words': [
        {'word': word, 'frequency': encounters} for word, encounters in word_encounters.items()
    ]
}

with open(collated_word_encounters_path, 'w', encoding='utf-8') as file:
    json.dump(json_data, file, indent=4)

print(f'Saved word encounters to {COLLATED_WORD_ENCOUNTERS_FILE}')
