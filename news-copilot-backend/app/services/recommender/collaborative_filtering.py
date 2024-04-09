import numpy as np
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

        if user_id not in self.user_item_matrix.index:
            return []

        if np.sum(self.user_item_matrix.loc[user_id]) == 0:
            return []

        user_views = self.user_item_matrix.loc[user_id].values.reshape(1, -1)
        similarity_scores = cosine_similarity(user_views, self.user_item_matrix)
        sim_scores_sorted = sorted(
            enumerate(similarity_scores[0]), key=lambda x: x[1], reverse=True
        )

        user_articles = self.user_item_matrix.columns
        recommended_articles = []

        for similar_user_id, similarity_score in sim_scores_sorted:
            print(similar_user_id, similarity_score)
            if len(recommended_articles) >= num_recommendations:
                break

            if similar_user_id == user_id:
                continue

            similar_user_views = self.user_item_matrix.loc[similar_user_id]

            for article_id, view_count in similar_user_views.iteritems():
                if (
                    view_count > 0
                    and article_id not in user_articles
                    and article_id not in recommended_articles
                ):
                    recommended_articles.append(article_id)

        return recommended_articles[:num_recommendations]
