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
from services.noon_task_scheduler import start_noon_task_email_scheduler


def ensure_task_columns():
    inspector = inspect(db.engine)
    if "tasks" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("tasks")}
    with db.engine.begin() as connection:
        if "task_scope" not in columns:
            connection.execute(text("ALTER TABLE tasks ADD COLUMN task_scope VARCHAR(20) DEFAULT 'today'"))
        if "due_date" not in columns:
            connection.execute(text("ALTER TABLE tasks ADD COLUMN due_date DATE"))


def ensure_trade_columns():
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
