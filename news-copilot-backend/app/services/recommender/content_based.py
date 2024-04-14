import pandas as pd
from pyvi import ViTokenizer, ViPosTagger


class ContentBasedRecommender:
    def __init__(self):
        self.content_matrix = None

    def load_content_matrix(self, articles_df):
        summaries = articles_df["summary"]
        tokenized_summaries = [self.extract_nouns(summary) for summary in summaries]
        self.content_matrix = pd.DataFrame(tokenized_summaries, index=articles_df["id"])

    def extract_nouns(self, summary):
        tokens, pos_tags = ViPosTagger.postagging(ViTokenizer.tokenize(summary))
        nouns = [
            tokens[i]
            for i, tag in enumerate(pos_tags)
            if tag.startswith("N") or tag.startswith("V")
        ]
        nouns = [noun.lower() for noun in nouns]
        return nouns

    def train(self, articles_df):
        self.load_content_matrix(articles_df)

    def recommend_articles(self, article_id, num_recommendations=5):
        if self.content_matrix is None:
            raise Exception(
                "The train method must be called before recommend_articles."
            )

        query_keywords = set(self.content_matrix.loc[article_id])

        recommended_articles = []
        for index, keywords_list in self.content_matrix.iterrows():
            if index == article_id:
                continue

            similarity_score = self.calculate_similarity(
                query_keywords, set(keywords_list)
            )
            recommended_articles.append((index, similarity_score))

        recommended_articles.sort(key=lambda x: x[1], reverse=True)
        return [article[0] for article in recommended_articles[:num_recommendations]]

    def calculate_similarity(self, query_keywords, article_keywords):
        intersection = len(query_keywords.intersection(article_keywords))
        union = len(query_keywords.union(article_keywords))
        return intersection / union
