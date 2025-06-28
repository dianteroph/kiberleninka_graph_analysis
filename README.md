# Graph analysis of articles:
### Kiberleninka website case.
This project provides a sufficient way to visualize articles based on their content similarity, using techniques such as website parsing and NLP analysis.
The base of the method is graph theory.

```kiberleninka_parser.py``` - have one class ArticleSearcher, which helps to parse articles from the website, based on your query and other params such as year and journal.
```article_processing.py``` - have two classes FileSaver and SimilarityCalculator which provides the main nlp-analysis of article texts.
```graph_creation.py``` - have one class GraphCreator, which build the graph save it in HTML-file
