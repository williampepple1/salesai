import logging

from alembic import command
from alembic.config import Config
from mangum import Mangum

from app.main import app

logger = logging.getLogger(__name__)
asgi_handler = Mangum(app, lifespan="off")


def handler(event, context):
    """Lambda entrypoint for HTTP traffic and IAM-invoked maintenance actions."""
    if isinstance(event, dict) and event.get("action") == "run_migrations":
        logger.info("Running Alembic migrations")
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("script_location", "alembic")
        command.upgrade(alembic_cfg, "head")
        return {"status": "ok", "action": "run_migrations"}

    return asgi_handler(event, context)
