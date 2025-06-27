#!/usr/bin/env python
# coding: utf-8

# In[134]:


get_ipython().system('uv add dotenv')


# In[158]:


import os
import webbrowser
import pandas as pd
from pyvis.network import Network
from kiberleninka_parser import ArticleSearcher 
from article_preprocessing import FileSaver, SimilarityCalculator


# In[129]:


class GraphCreator:

    def __init__(self, 
                 similarity_df: pd.DataFrame, 
                 json_options: str):

        self.similarity_df = similarity_df
        self.json_options = json_options

    def mean_similarity(self):

        '''Calculation of mean score of similarity 
        for each article. 
        '''
        self.similarity_df['mean_similarity_1'] = self.similarity_df.groupby('article_1') \
            ['similarity_score'].transform('mean')

        self.similarity_df['mean_similarity_2'] = self.similarity_df.groupby('article_2') \
            ['similarity_score'].transform('mean')

        return self.similarity_df


    def get_label(self, label: str) -> str:
        label = label.split()
        new_label = f'{' '.join(label[:4])}\n {' '.join(label[4:])}'
        return new_label


    def full_title(self, 
                   title: str, 
                   year: str, 
                   author: str) -> str:
        if author:
            author = ' '.join([x for x in author if author is not None])
            return f'{title}, \n[{author}, {year}]'

        return f'{title}, \n[{year}]'


    def create_graph(self):

        self.mean_similarity()
        self.similarity_df = self.similarity_df[ \
           self.similarity_df['similarity_score'] > 0.2]

        got_net = Network(notebook=False,
                         cdn_resources='remote', 
                         height="1000px",
                         width="100%",
                         bgcolor="#222222", 
                         font_color="white",
                         select_menu=True)
                          #filter_menu=True)

        edge_data = zip(self.similarity_df['article_1'], 
                       self.similarity_df['mean_similarity_1'],
                       self.similarity_df['article_1_year'],
                       self.similarity_df['article_1_author'],
                       self.similarity_df['article_2'],
                       self.similarity_df['mean_similarity_2'],
                       self.similarity_df['article_2_year'],
                       self.similarity_df['article_2_author'],
                       self.similarity_df['similarity_score'],
                       )


        for feature in edge_data:

            got_net.add_node(self.full_title(feature[0], feature[2], feature[3]), label=self.get_label(feature[0]), \
                             title=self.full_title(feature[0], feature[2], feature[3]), size=feature[1]*100, color='#77baff')

            got_net.add_node(self.full_title(feature[4], feature[6], feature[7]), label=self.get_label(feature[4]), \
                             title=self.full_title(feature[4], feature[6], feature[7]), size=feature[5]*100, color='#77baff')

            got_net.add_edge(self.full_title(feature[0], feature[2], feature[3]), \
                             self.full_title(feature[4], feature[6], feature[7]), value=feature[8])

        neighbor_map = got_net.get_adj_list()
        got_net.set_options(self.json_options)

        got_net.save_graph("article_protest_graph.html")
        file_path = os.path.abspath('article_protest_graph.html')


        return webbrowser.open_new_tab(f'file://{file_path}')





# In[ ]:


options_json = '''
             {"nodes": {
                "borderWidth": 0,
                "borderWidthSelected": 0,
                "opacity": 0.9,
                "font": {
                  "size": 18,
                  "face": "verdana"
                },
                "shadow": {
                  "enabled": true,
                  "color": "rgba(196, 228, 255, 0.51)",
                  "size": 12
                },
                "size": null
              },
              "edges": {
                "endPointOffset": {
                  "from": 4
                },
                "color": {
                  "inherit": true
                },
                "selfReferenceSize": null,
                "selfReference": {
                  "size": 54,
                  "angle": 0.7853981633974483
                },
                "smooth": false
              },
              "physics": {
                "barnesHut": {
                  "theta": 0.2,
                  "gravitationalConstant": -28860,
                  "centralGravity": 0.25,
                  "springLength": 405,
                  "springConstant": 0.01,
                  "damping": 0.24,
                  "avoidOverlap": 0.55
                },
                "maxVelocity": 140,
                "minVelocity": 0.24,
                "timestep": 0.67
              }

            '''


# In[132]:


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

    creator = GraphCreator(scores_df, options_json)
    df = creator.create_graph()


