import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from app.models.article import Article
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedRecommender:
    def __init__(self):
        self.content_matrix = None
        self.tfidf_vectorizer = TfidfVectorizer(stop_words="english")

    def load_content_matrix(self, articles_df):
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(articles_df["summary"])
        self.content_matrix = pd.DataFrame(
            tfidf_matrix.toarray(), index=articles_df["id"]  # type: ignore
        )

    def train(self, articles_df):
        self.load_content_matrix(articles_df)

    def recommend_articles(self, article_id, num_recommendations=5):
        if self.content_matrix is None:
            raise Exception(
                "The train method must be called before recommend_articles."
            )
        query_vector = self.content_matrix.loc[article_id].values.reshape(1, -1)
        similarity_scores = cosine_similarity(query_vector, self.content_matrix)
        sim_scores_sorted = sorted(
            enumerate(similarity_scores[0]), key=lambda x: x[1], reverse=True
        )
        recommended_articles = []
        for i in range(1, len(sim_scores_sorted)):
            recommended_articles.append(sim_scores_sorted[i][0])
            if len(recommended_articles) >= num_recommendations:
                return recommended_articles
