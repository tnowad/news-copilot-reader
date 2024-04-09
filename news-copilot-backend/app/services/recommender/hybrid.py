class HybridRecommender:
    def __init__(self, collaborative_filtering_recommender, content_based_recommender):
        # self.collaborative_filtering_recommender = collaborative_filtering_recommender
        self.content_based_recommender = content_based_recommender

    def train(self, views_df, articles_df):
        # self.collaborative_filtering_recommender.train(views_df)
        self.content_based_recommender.train(articles_df)

    def recommend_articles(self, user_id, num_recommendations=5):
        # collaborative_recommendations = (
        #     self.collaborative_filtering_recommender.recommend_articles(user_id)
        # )
        content_based_recommendations = (
            self.content_based_recommender.recommend_articles(user_id)
        )
        # hybrid_recommendations = (
        #     collaborative_recommendations + content_based_recommendations
        # )
        # return hybrid_recommendations[:num_recommendations]
        return content_based_recommendations[:num_recommendations]
