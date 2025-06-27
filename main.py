#!/usr/bin/env python
# coding: utf-8

# In[1]:


from kiberleninka_parser import ArticleSearcher 
from article_preprocessing import FileSaver, SimilarityCalculator
from graph_creation import GraphCreator


# In[ ]:


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
    creator.create_graph()

