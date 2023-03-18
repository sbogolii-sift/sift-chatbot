import os

import numpy as np
from bs4 import BeautifulSoup
from datasets import load_dataset
from sentence_transformers import SentenceTransformer, util, InputExample, losses, evaluation
from transformers import pipeline
from random import sample, seed, shuffle
from torch.utils.data import DataLoader


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = 'api-reference.html'
paragraphs = []
with open(file_path, 'r') as f:
    contents = f.read()
    html_parse = BeautifulSoup(contents, 'html.parser')
    for div in html_parse.find_all("div"):
        paragraphs.append(div.get_text(strip=False))

documents = list(filter(lambda x: len(x) > 30, paragraphs))

print(len(paragraphs))
print(len(documents))

bi_encoder = SentenceTransformer('msmarco-distilbert-base-v4')
bi_encoder.max_seq_length = 512
document_embeddings = bi_encoder.encode(documents, convert_to_tensor=True, show_progress_bar=True)

print(document_embeddings.shape)

QUESTION = 'Is $entity_type required in event?'

question_embeddings = bi_encoder.encode(QUESTION, convert_to_tensor=True)

hits = util.semantic_search(question_embeddings, document_embeddings, top_k=3)[0]

print(hits)

print(f'Question: {QUESTION}\n')

for i, hit in enumerate(hits):
    print(f'Document {i+1} Cos_Sim {hit["score"]:.3f}:\n\n{documents[hit["corpus_id"]]}')
    print('\n')

nlp = pipeline('question-answering', model='deepset/roberta-base-squad2', tokenizer='deepset/roberta-base-squad2', max_length=10)

answer = nlp(QUESTION, documents[hits[0]['corpus_id']])

print(f'Answer: {answer}\n\n')



