"""Alembic environment configuration for async migrations."""

import asyncio
import os
from logging.config import fileConfig
from urllib.parse import quote_plus

from alembic import context
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.db.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_url() -> str:
    """Build connection string from env vars (Azure) or fall back to alembic.ini (local dev)."""
    sql_server = os.environ.get("AZURE_SQL_SERVER")
    sql_database = os.environ.get("AZURE_SQL_DATABASE")

    if sql_server and sql_database:
        client_id = os.environ.get("AZURE_CLIENT_ID", "")
        # Use Managed Identity in Azure, Interactive auth locally
        auth_mode = os.environ.get("SQL_AUTH_MODE", "")
        if not auth_mode:
            auth_mode = "ActiveDirectoryInteractive" if not client_id else "ActiveDirectoryManagedIdentity"
        uid_part = f"UID={client_id};" if client_id and auth_mode == "ActiveDirectoryManagedIdentity" else ""
        odbc_connect = (
            "Driver={ODBC Driver 18 for SQL Server};"
            f"Server=tcp:{sql_server},1433;"
            f"Database={sql_database};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
            f"Authentication={auth_mode};"
            f"{uid_part}"
        )
        return f"mssql+aioodbc:///?odbc_connect={quote_plus(odbc_connect)}"

    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode - generates SQL script."""
    url = _get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    url = _get_url()
    ini_section = dict(config.get_section(config.config_ini_section, {}))
    ini_section["sqlalchemy.url"] = url

    connectable = async_engine_from_config(
        ini_section,
        prefix="sqlalchemy.",
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
