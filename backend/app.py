from flask import Flask

from backend.routes.auth import auth_bp
from backend.routes.home_routes import home_bp
from backend.routes.category_routes import category_bp
from backend.routes.status_routes import status_bp
from backend.routes.history_routes import history_bp

from backend.routes.admin.category_routes import admin_category_bp
from backend.routes.admin.status_routes import admin_status_bp
from backend.routes.admin.job_routes import admin_job_bp
from backend.routes.admin.achievement_routes import admin_achievement_bp
from backend.routes.admin.rule_routes import admin_rule_bp

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "your-secret-key"

    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(history_bp)

    app.register_blueprint(admin_category_bp)
    app.register_blueprint(admin_status_bp)
    app.register_blueprint(admin_job_bp)
    app.register_blueprint(admin_achievement_bp)
    app.register_blueprint(admin_rule_bp)

    return app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)