import os
import re
import json
import requests
import shutil
import pdfplumber
import random
import numpy as np
import nltk
import pymorphy3
import pandas as pd
from PyPDF2 import PdfReader
from typing import Optional, List
from requests import ConnectionError, HTTPError
from pdfminer.high_level import extract_pages, extract_text
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from string import punctuation
from nltk.corpus import stopwords
from kiberleninka_parser import ArticleSearcher 


class FileSaver:

    def __init__(self, article: dict, base_path: str):
        self.article = article
        self.base_path = base_path
        title = re.sub(r'[\W_]+', ' ', self.article['title']).strip() 
        self.title = '_'.join([n for n in title.split()[:5]]).strip()

    def get_pdf(self) -> bytes:

        '''Getting pdf bytes from the link.
        '''
        article_bytes = requests.get(self.article['link'] + '/pdf', stream=True)
        return article_bytes.content


    def get_text(self, article_bytes: bytes) -> Optional[str]:

        '''Getting text from bytes.
        '''
        try:
            with open('test_1.pdf', 'wb') as file:
                file.write(article_bytes)
                file.close()

            reader = PdfReader('test_1.pdf', strict=False)
            text = ' '.join([page.extract_text() for page in reader.pages])

        except Exception as e:
            print(f'The problem with the article {self.article['title']} - {e}')
            return None

        return text


    def get_text_dict(self):

        '''
        Getting the text from article
        and its metadata.
        '''
        article_bytes = self.get_pdf()
        text = self.get_text(article_bytes)
        if not text:
            return None

        result = {'title': 
                  self.article['title'].replace('<b>', '').replace('</b>', ''), 
                  'year': self.article['year'],
                  'author': self.article['authors'],
                  'text': text}

        print(f'Article {self.article['title']} is loaded')

        return result


class SimilarityCalculator:

    def __init__(self, articles: List[dict]):
        self.articles = articles
        self.articles_df = self.create_table()


    def create_table(self) -> pd.DataFrame:

        articles_df = pd.DataFrame.from_dict(self.articles)
        return articles_df


    def clean_text(self, text: str) -> list:

        '''
        Text tokenization: from unstractured .txt file to 
        lemmatized tokens.

        '''
        text = re.sub(r'([а-яА-ЯёЁ]+)-\n([а-яА-ЯёЁ]+)', r'\1\2', text)
        text = re.sub(r'-\n', '', text)
        text = re.sub(r'[\r\n\t]+', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        tokens = nltk.word_tokenize(text)
        punc = list(punctuation)
        punc.extend(['...', '""', "''", '``', '«', '»', '—', '№'])
        stop_words = stopwords.words('russian') + stopwords.words('english')
        morph = pymorphy3.MorphAnalyzer()
        final_tokens = []

        for token in tokens:
            token = token.lower()
            if token not in punc and token not in stop_words:
                lemma = morph.parse(token.replace('-', ''))[0].normal_form
                final_tokens.append(lemma)

        return final_tokens


    def calculate_similarity(self) -> pd.DataFrame:

        '''Creation of tokens vocabulary.
        Tf-Idf approach: making a vocabulary that include all article's
        tokens and calculate the importance of each token, based on
        term-frequency and inverse document frequency.

        Calculation of similarity of vocabulary betweeen atricles.
        Cosine similarity: calculate the cosine distance between vectors of 
        each article in a sample.
        '''

        vec = TfidfVectorizer(tokenizer=self.clean_text)
        words_vectorized = vec.fit_transform(
            self.articles_df['text'])

        df_vocab = pd.DataFrame(
            words_vectorized.toarray(),
            columns = vec.get_feature_names_out(),
            index = self.articles_df['title']
           )

        df_vocab['year'] = self.articles_df['year'].values
        df_vocab['author'] = self.articles_df['author'].values

        article_ids = df_vocab.index.values
        article_years = df_vocab['year'].values
        article_author = df_vocab['author'].values
        vectors = df_vocab.drop(columns=['year', 'author']).values
        cosine_sim = cosine_similarity(vectors)

        scores = []
        for i in range(len(df_vocab)):
            for j in range(i + 1, len(df_vocab)):
                scores.append({
                    'article_1': article_ids[i],
                    'article_2': article_ids[j],
                    'article_1_year': article_years[i],
                    'article_2_year': article_years[j],
                    'article_1_author': article_author[i],
                    'article_2_author': article_author[j],
                    'similarity_score': cosine_sim[i][j]
                })

        similarity_scores = pd.DataFrame(scores)
        return similarity_scores 




if __name__ == '__main__':

    parser = ArticleSearcher("'протесты болотная площадь'", 2000, 2025, [2])
    articles = parser.get_articles()

    articles_data = []
    for article in articles:
        saver = FileSaver(article, os.getcwd())
        article_dict = saver.get_text_dict()
        if article_dict:
            articles_data.append(article_dict)

    calculator = SimilarityCalculator(articles_data)
    scores_df = calculator.calculate_similarity()

