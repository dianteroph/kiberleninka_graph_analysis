import os
import re
import json
import requests
import shutil
import pdfplumber
import pytesseract
import random
from typing import List
from pprint import pprint
from bs4 import BeautifulSoup
from typing import Optional, List
from requests import ConnectionError, HTTPError


'''
Main journal codes:

Scopus - [2]
AGRIS - [12]
BAK - [8]
RSCI - [22]
ESCI - [23]

'''


def get_user_agents(path: str ='user-agents.txt') -> Optional[List[dict]]:
    '''Get the list of user agents
    '''
    user_agents = []
    try:
        with open('user-agents.txt', 'r') as file:
            for line in file.readlines():
                user_agents.append(line.strip('\n'))
            return user_agents 

    except FileNotFoundError:
        print(f'The is no such a file {path}')
        return []

request_body = {
        'mode': 'articles',
        'size': 10}



class ArticleSearcher:

    def __init__(self,
                 keywords: str,
                 year_from: int,
                 year_to: int,
                 filter_val: Optional[List[int]] = None) -> None:

        self.article_data = []
        self.url = 'https://cyberleninka.ru'
        self.api =  f'{self.url}/api/search'
        self.keywords = keywords
        self.year_from = year_from
        self.year_to = year_to
        self.headers = {'User-Agent': random.choice(get_user_agents())}
        self.request_body = request_body | {'q': self.keywords} \
                                         | ({'catalogs': filter_val} if filter_val is not None else {})


    def get_json(self, year: int, from_val=0) -> Optional[dict]:

        '''Getting the response from the kiberleninka 
        hidden api, using post request.
        '''
        request_payload = {
             **self.request_body,
            'from': from_val, 
            'year_from': year,
            'year_to': year
        }
        try:
            response = requests.post(self.api, data=json.dumps(request_payload),
                                     headers=self.headers).text

            return json.loads(response)

        except Exception as e:
            print(f"Can't get a response, got an error - {e}")
            return None


    def article_metadata(self, article_data: List[dict]) -> None:
        '''Collecting the main information about articles.
        '''
        for article in article_data:
            self.article_data.append({
                'title': article['name'],
                'link': self.url + article['link'],
                'authors': article['authors'],
                'year': article['year'],
                'journal': article['journal']
            })


    def iterate_pages(self, year: int) -> None:
        data_json = self.get_json(year)
        articles_num = data_json.get('found', 0)
        print(f'Found {articles_num} articles for request{self.keywords}, published in {year}')

        for page in range(0, articles_num, 10):
            try:
                response_json = self.get_json(year, page)
                data = self.article_metadata(response_json['articles'])
                print(f'Data for the page {page} is loaded')
            except KeyError:
                break


    def get_articles(self) -> List[dict]:
        '''Main function to get all articles from the response.
        '''
        years = list(range(self.year_from, self.year_to + 1))

        for year in years:
            self.iterate_pages(year)

        return self.article_data




if __name__ == '__main__':
    searcher = ArticleSearcher("'протесты болотная площадь'", 2000, 2025, [2])
    seacher.get_articles()

