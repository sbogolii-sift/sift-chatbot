import os

from flask import Flask, request, render_template
from transformers import GPT2LMHeadModel, pipeline

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(ROOT_DIR, 'templates'),
            static_folder=os.path.join(ROOT_DIR, 'static'))
model = GPT2LMHeadModel.from_pretrained('./gpt2_sift_api')

generator = pipeline(
    'text-generation', model=model, tokenizer='gpt2')


@app.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'POST':
        text_input = request.form['text_input']
        text_output = process_text(text_input)
        print(text_output)
        return render_template('index.html', text_output=text_output.replace('\n', '<br/>'))
    return render_template('index.html')


def process_text(query):
    return generator(query, max_length=50, num_return_sequences=1)[0]['generated_text']


if __name__ == '__main__':
    app.run()
