class HybridRecommender:
    def __init__(self, collaborative_filtering_recommender, content_based_recommender):
        self.collaborative_filtering_recommender = collaborative_filtering_recommender
        self.content_based_recommender = content_based_recommender

    def train(self, views_df, articles_df):
        self.collaborative_filtering_recommender.train(views_df)
        self.content_based_recommender.train(articles_df)

    def recommend_articles(self, user_id, article_id, num_recommendations=5):
        recommended_articles = []
        if user_id is not None:
            collaborative_recommendations = (
                self.collaborative_filtering_recommender.recommend_articles(user_id)
            )
            print(collaborative_recommendations)
            recommended_articles.extend(collaborative_recommendations)

        if article_id is not None:
            content_based_recommendations = (
                self.content_based_recommender.recommend_articles(article_id)
            )
            recommended_articles.extend(content_based_recommendations)

        return recommended_articles[:num_recommendations]
