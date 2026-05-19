from DatabaseAdapter import _create_engine
from DatabaseMigrator import get_table_columns, add_new_columns
import geopandas as gpd

def transform_and_load_data_for_production(layer_name: str, year: str, data:gpd.GeoDataFrame):
    engine = _create_engine()
    
    with engine.begin() as connect:
        data.to_postgis('temp_' + layer_name + '_' + year, con=connect, if_exists='replace', index=False, schema = 'raw')
        connect().execute(f"ALTER TABLE raw.temp_{layer_name}_{year} ADD COLUMN id_master")
        columns_list = list(data.columns)
        columns_list_with_id_master = columns_list
        columns_list_with_id_master.insert(0, 'id_master')
        cols_list = ', '.join(columns_list_with_id_master)
        update_list = ', '.join([f"{c} = EXCLUDED.{c}" for c in columns_list])
        
        connect.execute(f"""
            CREATE SEQUENCE master_id_seq START WITH (
            SELECT GREATEST(
                COALESCE((SELECT MAX(id_master) FROM raw.temp_{layer_name}_{year}), 0),
                COALESCE((SELECT MAX(id_master) FROM production.master_{layer_name}), 0)
            ) + 1);

            UPDATE raw.temp_{layer_name}_{year} AS temp
            SET id_master = (
                CASE
                    WHEN temp.indelingswijziging_wijken_en_buurten = 1 THEN
                        (SELECT id_master 
                        FROM production.master_{layer_name}
                        WHERE 
                            temp.{layer_name}_code = production.master_{layer_name}.{layer_name}_code
                            AND temp.jaar - 1 = production.master_{layer_name}.jaar
                        LIMIT 1)
                    WHEN temp.indelingswijziging_wijken_en_buurten = 2 THEN
                        (SELECT id_master 
                        FROM production.{layer_name}
                        WHERE 
                            ST_Equals(temp.geometry, production.{layer_name}.geometry)
                            AND temp.jaar - 1 = production.{layer_name}.jaar
                        LIMIT 1)
                    ELSE nextval('master_id_seq')
            )
            
            DROP SEQUENCE master_id_seq;
            """)
        
        connect.execute(f"""
            INSERT INTO production.{layer_name} ({cols_list})
            SELECT {cols_list}
            FROM raw.temp_{layer_name}_{year} AS temp
            ON CONFLICT ({layer_name}, jaar) DO UPDATE SET {update_list}
        """)
        connect.execute(f"DROP TABLE raw.temp_{layer_name}_{year};")