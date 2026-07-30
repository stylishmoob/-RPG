from flask import Flask, send_from_directory
import os
from pathlib import Path

from backend.routes.auth import auth_bp
from backend.routes.home_routes import home_bp
from backend.routes.category_routes import category_bp
from backend.routes.status_routes import status_bp
from backend.routes.history_routes import history_bp

from backend.services.action_service import action_bp

from backend.routes.admin.category_routes import admin_category_bp
from backend.routes.admin.status_routes import admin_status_bp
from backend.routes.admin.job_routes import admin_job_bp
from backend.routes.admin.achievement_routes import admin_achievement_bp
from backend.routes.admin.rule_routes import admin_rule_bp
from backend.routes.admin.user_routes import admin_user_bp, reset_user_data_bp

PROJECT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_DIR / "frontend" / "dist"

def create_app():
    app = Flask(
        __name__,
        static_folder=str(DIST_DIR / "assets"),
        static_url_path="/assets",
    )

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "development-secret-key")

    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(history_bp)

    app.register_blueprint(action_bp)

    app.register_blueprint(admin_category_bp)
    app.register_blueprint(admin_status_bp)
    app.register_blueprint(admin_job_bp)
    app.register_blueprint(admin_achievement_bp)
    app.register_blueprint(admin_rule_bp)
    app.register_blueprint(admin_user_bp)
    app.register_blueprint(reset_user_data_bp)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_react(path):
        requested_file = DIST_DIR / path

        if path and requested_file.is_file():
            return send_from_directory(DIST_DIR, path)

        return send_from_directory(DIST_DIR, "index.html")

    return app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
