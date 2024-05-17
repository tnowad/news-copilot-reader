import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize


class CollaborativeFilteringRecommender:
    def __init__(self):
        self.user_item_matrix = None
        self.user_similarity_matrix = None

    def load_user_item_matrix(self, views_df):
        self.user_item_matrix = views_df.pivot_table(
            index="user_id", columns="article_id", aggfunc="size", fill_value=0
        )
        self.user_similarity_matrix = self._compute_user_similarity_matrix()

    def _compute_user_similarity_matrix(self):
        user_views_normalized = normalize(self.user_item_matrix.values)  # type: ignore
        similarity_matrix = cosine_similarity(user_views_normalized)
        np.fill_diagonal(similarity_matrix, 0)  # Set self-similarity to 0
        return similarity_matrix

    def train(self, views_df):
        self.load_user_item_matrix(views_df)

    def recommend_articles(
        self, user_id, num_recommendations=5, similarity_threshold=0.5
    ):
        if self.user_item_matrix is None:
            raise Exception(
                "The train method must be called before recommend_articles."
            )

        if user_id not in self.user_item_matrix.index:
            return []

        user_index = self.user_item_matrix.index.get_loc(user_id)
        user_similarities = self.user_similarity_matrix[user_index]  # type: ignore
        similar_users = np.where(user_similarities > similarity_threshold)[0]

        # if len(similar_users) == 0:
        #     return []

        item_scores = np.sum(self.user_item_matrix.values[similar_users], axis=0)
        item_scores[user_index] = 0
        top_item_indices = np.argsort(item_scores)[::-1][:num_recommendations]

        return self.user_item_matrix.columns[top_item_indices].tolist()
