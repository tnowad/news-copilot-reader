from sklearn.metrics.pairwise import cosine_similarity


class CollaborativeFilteringRecommender:
    def __init__(self):
        self.user_item_matrix = None

    def load_user_item_matrix(self, views_df):
        self.user_item_matrix = views_df.pivot_table(
            index="user_id", columns="article_id", aggfunc="size", fill_value=0
        )

    def train(self, views_df):
        self.load_user_item_matrix(views_df)

    def recommend_articles(self, user_id, num_recommendations=5):
        if self.user_item_matrix is None:
            raise Exception(
                "The train method must be called before recommend_articles."
            )

        user_views = self.user_item_matrix.loc[user_id].values.reshape(1, -1)
        similarity_matrix = cosine_similarity(user_views, self.user_item_matrix)
        sim_scores = list(enumerate(similarity_matrix[0]))
        sim_scores_sorted = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        user_articles = self.user_item_matrix.columns
        recommended_articles = []
        for i in range(1, len(sim_scores_sorted)):
            similar_user_id = sim_scores_sorted[i][0]
            similar_user_views = self.user_item_matrix.loc[similar_user_id]
            for article_id, view_count in similar_user_views.iteritems():
                if view_count > 0 and article_id not in user_articles:
                    recommended_articles.append(article_id)
                if len(recommended_articles) >= num_recommendations:
                    return recommended_articles
