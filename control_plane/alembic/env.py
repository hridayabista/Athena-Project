# control_plane/alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# CRITICAL: Allow importing the 'control_plane' package from the parent directory
# This ensures Alembic can find control_plane.app.db and models.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from control_plane.app.db import Base, DATABASE_URL
from control_plane.app import models  # noqa: F401 - Register models with Base.metadata

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# CRITICAL: Set the target metadata to your application's Base
target_metadata = Base.metadata

# CRITICAL: Configure the database URL based on environment variable
# This ensures Alembic uses the DATABASE_URL environment variable 
# even if sqlalchemy.url is commented out in alembic.ini.
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", DATABASE_URL))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # CRITICAL FIX: Pass the URL explicitly to engine_from_config
    # to avoid KeyError: 'url' when the URL is missing from alembic.ini
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=config.get_main_option("sqlalchemy.url"), # Injects the URL
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()