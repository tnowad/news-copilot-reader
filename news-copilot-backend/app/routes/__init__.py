from flask import Blueprint

from .main import main_bp
from .auth import auth_bp
from .articles import articles_bp
from .categories import categories_bp
from .user import user_bp

routes_bp = Blueprint("api", __name__)

routes_bp.register_blueprint(auth_bp)
routes_bp.register_blueprint(main_bp)
routes_bp.register_blueprint(articles_bp)
routes_bp.register_blueprint(categories_bp)
routes_bp.register_blueprint(user_bp)
