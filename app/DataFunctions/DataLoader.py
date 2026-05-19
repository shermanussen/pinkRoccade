import geopandas as gpd
from DatabaseAdapter import _create_engine
from DataFunctions.DatabaseMigrator import add_new_columns
from DataFunctions.DataTransformer import transform_and_load_data_for_production
from sqlalchemy import text

class DataLoader:
    def insert_raw_data(self, data: gpd.GeoDataFrame, layer_name: str, year: str):
        engine = _create_engine()
        data.to_postgis(layer_name + '_' + year, con=engine, if_exists='replace', index=False, schema = 'raw')

    def insert_production_data(self, layer_name: str, data:gpd.GeoDataFrame, year: str):
        add_new_columns('production', layer_name, data)
        transform_and_load_data_for_production(layer_name, year, data)