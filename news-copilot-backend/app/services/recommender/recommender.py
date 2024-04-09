from app.services.recommender.data_loader import load_articles, load_views
from app.services.recommender.content_based import ContentBasedRecommender
from app.services.recommender.collaborative_filtering import (
    CollaborativeFilteringRecommender,
)
from app.services.recommender.hybrid import HybridRecommender

cf_recommender = CollaborativeFilteringRecommender()
cb_recommender = ContentBasedRecommender()

cf_recommender.train(load_views())
cb_recommender.train(load_articles())

hybrid_recommender = HybridRecommender(cf_recommender, cb_recommender)
