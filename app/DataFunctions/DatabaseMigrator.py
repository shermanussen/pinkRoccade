import geopandas as gpd
from DatabaseAdapter import _create_engine
from sqlalchemy import text

def get_table_columns(schema: str, table_name: str) -> list[str]:
    engine = _create_engine()
    with engine.connect() as connection:
        query = text(f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = :schema AND table_name = :table_name;
        """)
        result = connection.execute(query, {"schema": schema, "table_name": table_name})
        return [row[0] for row in result]

def add_new_columns(schema: str, table_name: str, data: gpd.GeoDataFrame):
    engine = _create_engine()
    with engine.connect() as connection:
        for column in data.columns:
            if column not in get_table_columns(schema, table_name):
                alter_query = text(f"ALTER TABLE {schema}.{table_name} ADD COLUMN {column} TEXT;")
                connection.execute(alter_query)