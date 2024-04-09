import pandas as pd
from app.models.article import Article
from app.models.view import View


def load_articles():
    articles = Article.query.all()

    articles_df = pd.DataFrame(
        {
            "id": [article.id for article in articles],
            "title": [article.title for article in articles],
            "summary": [article.summary for article in articles],
        },
    )

    return articles_df


def load_views():
    views = View.query.all()

    views_df = pd.DataFrame(
        {
            "user_id": [view.user_id for view in views],
            "article_id": [view.article_id for view in views],
            "viewed_at": [view.viewed_at for view in views],
        }
    )
    return views_df
