import geopandas as gpd
from sqlalchemy import create_engine, text
import os

class DataLoader:
    def _create_engine(self):
        db_host = os.getenv("DB_HOST", "postgres")
        db_name = os.getenv("DB_NAME", "my_db")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD")

        if db_password is None:
            raise RuntimeError("Database password is not set. Set DB_PASSWORD in the environment.")

        return create_engine(
            f'postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}'
        )

    def insert_raw_data(self, data: gpd.GeoDataFrame, layer_name: str, year: str):
        engine = self._create_engine()
        data.to_postgis(layer_name + '_' + year, con=engine, if_exists='replace', index=False, schema = 'raw')
