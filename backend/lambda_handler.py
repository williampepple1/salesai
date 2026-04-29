import logging

from alembic import command
from alembic.config import Config
from mangum import Mangum
from sqlalchemy import inspect

from app.database import engine
from app.main import app

logger = logging.getLogger(__name__)
asgi_handler = Mangum(app, lifespan="off")
BASELINE_TABLES = {"users", "products", "conversations", "discount_rules", "orders"}


def handler(event, context):
    """Lambda entrypoint for HTTP traffic and IAM-invoked maintenance actions."""
    if isinstance(event, dict) and event.get("action") == "run_migrations":
        logger.info("Running Alembic migrations")
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("script_location", "alembic")
        if _has_unversioned_existing_schema():
            logger.warning("Existing unversioned schema detected; stamping Alembic head")
            command.stamp(alembic_cfg, "head")
        else:
            command.upgrade(alembic_cfg, "head")
        return {"status": "ok", "action": "run_migrations"}

    return asgi_handler(event, context)


def _has_unversioned_existing_schema() -> bool:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    return "alembic_version" not in table_names and bool(BASELINE_TABLES & table_names)
