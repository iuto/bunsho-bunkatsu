from flask import Flask, request, render_template
from collections import Counter
from urllib.parse import urlsplit
import re

app = Flask(__name__)

def remove_urls(text):
    url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.sub(url_regex, '', text)

def extract_urls(text):
    url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_regex, text)

def split_by_character_limit(text, limit):
    split_text = [text[i:i+limit] for i in range(0, len(text), limit)]
    lengths = [len(part) for part in split_text]
    return split_text, lengths

def split_by_period_and_char_limit(text, limit):
    split_text = []
    lengths = []
    temp_text = ''
    for char in text:
        temp_text += char
        if len(temp_text) >= limit:
            if '。' in temp_text:
                temp_text_parts = temp_text.rsplit('。', 1)
                split_text.append(temp_text_parts[0] + '。')
                lengths.append(len(temp_text_parts[0] + '。'))
                temp_text = temp_text_parts[1] if len(temp_text_parts) > 1 else ''
            else:
                split_text.append(temp_text)
                lengths.append(len(temp_text))
                temp_text = ''
    if temp_text:
        split_text.append(temp_text)
        lengths.append(len(temp_text))
    return split_text, lengths

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form.get('text')
        character_limit = int(request.form.get('character_limit'))
        split_by_period = request.form.get('split_by') == 'period'
        url_option = request.form.get('url_option')
        text_length_dicts = []
        url_counts = None

        if url_option == 'remove':
            text = remove_urls(text)
        elif url_option == 'extract':
            urls = extract_urls(text)
            url_counts = Counter(urls)

        if url_option != 'extract':
            if split_by_period:
                split_text, lengths = split_by_period_and_char_limit(text, character_limit)
            else:
                split_text, lengths = split_by_character_limit(text, character_limit)
            
            for text_part, length in zip(split_text, lengths):
                text_length_dicts.append({'text': text_part, 'length': length})

            total_length = sum(lengths)
        else:
            total_length = None

        return render_template('index.html', text_length_dicts=text_length_dicts, total_length=total_length, url_counts=url_counts)
    else:
        return render_template('index.html')
    
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)