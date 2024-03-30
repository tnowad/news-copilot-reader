from flask import Blueprint

from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.articles import articles_bp
from app.routes.categories import categories_bp
from app.routes.user import user_bp
from app.routes.comments import comments_bp

routes_bp = Blueprint("api", __name__)

routes_bp.register_blueprint(auth_bp)
routes_bp.register_blueprint(main_bp)
routes_bp.register_blueprint(articles_bp)
routes_bp.register_blueprint(categories_bp)
routes_bp.register_blueprint(user_bp)
routes_bp.register_blueprint(comments_bp)
