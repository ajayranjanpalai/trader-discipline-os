from flask import Flask, send_from_directory
from flask_cors import CORS
from sqlalchemy import event, inspect, text
from dotenv import load_dotenv

load_dotenv()

from config import Config
from models import db
from routes.auth import auth_bp
from routes.trades import trades_bp
from routes.expenses import expenses_bp
from routes.tasks import tasks_bp
from routes.analytics import analytics_bp
from routes.capital import capital_bp
from routes.insights import insights_bp
from routes.extended_api import extended_api_bp
from routes.heatmap import heatmap_bp
from routes.gallery import gallery_bp
from routes.milestone import milestone_bp
from routes.reports import reports_bp
from services.noon_task_scheduler import start_noon_task_email_scheduler


def ensure_task_columns():
    try:
        inspector = inspect(db.engine)
        if "tasks" not in inspector.get_table_names():
            return
        columns = {col["name"] for col in inspector.get_columns("tasks")}
        with db.engine.begin() as connection:
            if "task_scope" not in columns:
                connection.execute(text("ALTER TABLE tasks ADD COLUMN task_scope VARCHAR(20) DEFAULT 'today'"))
            if "due_date" not in columns:
                connection.execute(text("ALTER TABLE tasks ADD COLUMN due_date DATE"))
    except Exception as e:
        print(f"Task migration notice: {e}")


def ensure_trade_columns():
    try:
        inspector = inspect(db.engine)
        if "trades" not in inspector.get_table_names():
            return
        columns = {col["name"] for col in inspector.get_columns("trades")}
        with db.engine.begin() as connection:
            if "brokerage" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN brokerage FLOAT DEFAULT 0"))
            if "closed_quantity" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN closed_quantity FLOAT DEFAULT 0"))
            if "remaining_quantity" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN remaining_quantity FLOAT DEFAULT 0"))
            if "remaining_exit" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN remaining_exit FLOAT DEFAULT 0"))
            if "tags" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN tags VARCHAR(255) DEFAULT ''"))
            if "is_bookmarked" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN is_bookmarked BOOLEAN DEFAULT FALSE"))
            if "bookmark_label" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN bookmark_label VARCHAR(100) DEFAULT ''"))
            if "is_best_trade" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN is_best_trade BOOLEAN DEFAULT FALSE"))
            if "is_worst_trade" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN is_worst_trade BOOLEAN DEFAULT FALSE"))
            if "screenshot_url" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN screenshot_url TEXT DEFAULT ''"))
            if "before_img" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN before_img TEXT DEFAULT ''"))
            if "during_img" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN during_img TEXT DEFAULT ''"))
            if "exit_img" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN exit_img TEXT DEFAULT ''"))
            if "is_favorite" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN is_favorite BOOLEAN DEFAULT FALSE"))
            if "strategy_version" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN strategy_version VARCHAR(100) DEFAULT ''"))
            if "duration_type" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN duration_type VARCHAR(40) DEFAULT 'Intraday'"))
            if "holding_time_minutes" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN holding_time_minutes FLOAT DEFAULT 0"))
            if "custom_fields_json" not in columns:
                connection.execute(text("ALTER TABLE trades ADD COLUMN custom_fields_json TEXT DEFAULT '{}'"))
    except Exception as e:
        print(f"Trade migration notice: {e}")



def create_app():
    app = Flask(__name__, static_folder="frontend", static_url_path="")
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(trades_bp, url_prefix="/api/trades")
    app.register_blueprint(expenses_bp, url_prefix="/api/expenses")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(capital_bp, url_prefix="/api/capital")
    app.register_blueprint(insights_bp, url_prefix="/api/insights")
    app.register_blueprint(extended_api_bp, url_prefix="/api/os")
    app.register_blueprint(heatmap_bp, url_prefix="/api/heatmap")
    app.register_blueprint(gallery_bp, url_prefix="/api/gallery")
    app.register_blueprint(milestone_bp, url_prefix="/api/milestones")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")



    @app.route("/")
    def index():
        return send_from_directory("frontend", "index.html")

    @app.errorhandler(404)
    def not_found(_error):
        return {"error": "Resource not found"}, 404

    @app.errorhandler(500)
    def server_error(error):
        app.logger.error("Unhandled server exception: %s", error, exc_info=True)
        return {"error": "Unexpected server error"}, 500

    with app.app_context():
        if db.engine.url.drivername == "sqlite":
            @event.listens_for(db.engine, "connect")
            def set_sqlite_pragmas(dbapi_connection, _connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA busy_timeout=5000")
                cursor.close()

        db.create_all()
        ensure_task_columns()
        ensure_trade_columns()

    return app


app = create_app()


if __name__ == "__main__":
    start_noon_task_email_scheduler(app)
    app.run(debug=True)
