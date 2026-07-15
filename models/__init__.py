from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User  # noqa: E402,F401
from .pending_signup import PendingSignup  # noqa: E402,F401
from .trade import Trade  # noqa: E402,F401
from .capital_transaction import CapitalTransaction  # noqa: E402,F401
from .expense import Expense  # noqa: E402,F401
from .task import Task  # noqa: E402,F401
from .task_completion import TaskCompletion  # noqa: E402,F401
from .task_email_log import TaskEmailLog  # noqa: E402,F401
from .discipline_log import DisciplineLog  # noqa: E402,F401
from .ai_insight import AIInsight  # noqa: E402,F401
