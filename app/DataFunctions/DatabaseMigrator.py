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
    with engine.begin() as connection:
        table_columns = get_table_columns(schema, table_name)
        for column in data.columns:
            if column not in table_columns:
                dtype_str = str(data[column].dtype)
                sql_type = 'TEXT'
                if 'int' in dtype_str:
                    sql_type = 'INTEGER'
                elif 'float' in dtype_str:
                    sql_type = 'FLOAT'
                elif 'bool' in dtype_str:
                    sql_type = 'BOOLEAN'
                elif 'datetime' in dtype_str:
                    sql_type = 'TIMESTAMP'
                elif 'geometry' in dtype_str:
                    sql_type = 'GEOMETRY'
                alter_query = text(f"ALTER TABLE {schema}.{table_name} ADD COLUMN {column} {sql_type};")
                connection.execute(alter_query)