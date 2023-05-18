"""Module for creating a ClickHouse client."""

from clickhouse_driver import Client as ClickHouseClient

# ClickHouse connection configuration
connection_settings = {
    'host': 'clickhouse',
}


# Create a ClickHouse client
def create_client():
    """Create a ClickHouse client."""
    client_ch = ClickHouseClient(**connection_settings)
    return client_ch
