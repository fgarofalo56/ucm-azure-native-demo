"""SQLAlchemy async session factory for Azure SQL Database."""

import struct
from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# Build async connection URL for aioodbc
# Use basic ODBC connection without built-in MSI auth - we'll inject the token via event
_connection_string = (
    f"Driver={{ODBC Driver 18 for SQL Server}};"
    f"Server=tcp:{settings.azure_sql_server},1433;"
    f"Database={settings.azure_sql_database};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

# aioodbc connection string format
DATABASE_URL = f"mssql+aioodbc:///?odbc_connect={_connection_string}"

engine = create_async_engine(
    DATABASE_URL,
    echo=not settings.is_production,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)


# Inject Azure AD token before each connection is made
@event.listens_for(engine.sync_engine, "do_connect")
def _inject_azure_token(dialect, conn_rec, cargs, cparams):
    """Inject Entra ID access token into pyodbc connection attributes."""
    from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

    try:
        # Use ManagedIdentityCredential with specific client_id for user-assigned identity
        if settings.azure_client_id:
            credential = ManagedIdentityCredential(client_id=settings.azure_client_id)
        else:
            credential = DefaultAzureCredential()

        token = credential.get_token("https://database.windows.net/.default")
        token_bytes = token.token.encode("utf-16-le")
        token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)

        # SQL_COPT_SS_ACCESS_TOKEN = 1256
        attrs = cparams.get("attrs_before", {})
        attrs[1256] = token_struct
        cparams["attrs_before"] = attrs
    except Exception:
        # If running locally without managed identity, let it fail naturally
        pass


async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides a database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
