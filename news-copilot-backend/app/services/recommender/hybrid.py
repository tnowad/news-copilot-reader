from app.services.recommender.data_loader import load_articles, load_views
from app.services.recommender.content_based import ContentBasedRecommender
from app.services.recommender.collaborative_filtering import (
    CollaborativeFilteringRecommender,
)


class HybridRecommender:
    def __init__(self):
        self.collaborative_filtering_recommender = CollaborativeFilteringRecommender()
        self.content_based_recommender = ContentBasedRecommender()
        self.train(load_views(), load_articles())

    def train(self, views_df, articles_df):
        self.collaborative_filtering_recommender.train(views_df)
        self.content_based_recommender.train(articles_df)

    def recommend_articles(self, user_id, article_id, num_recommendations=12):
        recommended_articles = []
        if user_id is not None:
            collaborative_recommendations = (
                self.collaborative_filtering_recommender.recommend_articles(
                    user_id, num_recommendations
                )
            )
            print(collaborative_recommendations)
            recommended_articles.extend(collaborative_recommendations)

        if article_id is not None:
            content_based_recommendations = (
                self.content_based_recommender.recommend_articles(
                    article_id, num_recommendations
                )
            )
            recommended_articles.extend(content_based_recommendations)

        return recommended_articles[:num_recommendations]
