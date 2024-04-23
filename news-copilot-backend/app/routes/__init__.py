from flask import Blueprint

from app.routes.articles import articles_bp
from app.routes.auth import auth_bp
from app.routes.bookmarks import bookmarks_bp
from app.routes.categories import categories_bp
from app.routes.comments import comments_bp
from app.routes.generation import generation_bp
from app.routes.main import main_bp
from app.routes.recommendations import recommendations_bp
from app.routes.roles import roles_bp
from app.routes.statistics import statistics_bp
from app.routes.uploads import uploads_bp
from app.routes.users import users_bp
from app.routes.views import views_bp
from app.routes.report import report_bp
from app.routes.chatbot import chatbot_bp

routes_bp = Blueprint("api", __name__)

routes_bp.register_blueprint(articles_bp)
routes_bp.register_blueprint(auth_bp)
routes_bp.register_blueprint(bookmarks_bp)
routes_bp.register_blueprint(categories_bp)
routes_bp.register_blueprint(comments_bp)
routes_bp.register_blueprint(generation_bp)
routes_bp.register_blueprint(main_bp)
routes_bp.register_blueprint(recommendations_bp)
routes_bp.register_blueprint(roles_bp)
routes_bp.register_blueprint(statistics_bp)
routes_bp.register_blueprint(users_bp)
routes_bp.register_blueprint(uploads_bp)
routes_bp.register_blueprint(views_bp)
routes_bp.register_blueprint(report_bp)
roles_bp.register_blueprint(chatbot_bp)
