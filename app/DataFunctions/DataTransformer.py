from DatabaseAdapter import _create_engine
from DataFunctions.DatabaseMigrator import get_table_columns, add_new_columns
import geopandas as gpd

def remove_duplicates(data: gpd.GeoDataFrame): 
    bad_values = [-99997, 99997, 99995, 99991]
    dup_mask = data.duplicated(subset=['gemeentecode', 'jaar'], keep=False)
    bad_mask = data.isin(bad_values).any(axis=1)
    df_clean = data[~(dup_mask & bad_mask)]
    return df_clean

def transform_and_load_data_for_production(layer_name: str, year: str, data:gpd.GeoDataFrame):
    engine = _create_engine()
    
    layer_to_name_mapping = {
        'gemeenten': 'gemeente',
        'wijken': 'wijk',
        'buurten': 'buurt'
    }
    data_clean = remove_duplicates(data)
    
    with engine.begin() as connect:
        
        # Create temporary table
        data_clean.to_postgis('temp_' + layer_name + '_' + year, con=connect, if_exists='replace', index=False, schema = 'raw')

        # Add id_master column to temporary table
        connect.exec_driver_sql(f"ALTER TABLE raw.temp_{layer_name}_{year} ADD COLUMN id_master INT;")

        columns_list = list(data_clean.columns)
        columns_list_with_id_master = columns_list
        columns_list_with_id_master.insert(0, 'id_master')
        cols_list = ', '.join(columns_list_with_id_master)
        update_list = ', '.join([f"{c} = EXCLUDED.{c}" for c in columns_list])

        connect.exec_driver_sql(f"""
            CREATE SEQUENCE master_id_seq START WITH 1;
            SELECT setval('master_id_seq', GREATEST(
                COALESCE((SELECT MAX(id_master) FROM raw.temp_{layer_name}_{year}), 0),
                COALESCE((SELECT MAX(id_master) FROM production.master_{layer_name}), 0)
            ) + 1, false);

            UPDATE raw.temp_{layer_name}_{year} AS temp
            SET id_master = (
                CASE
                    WHEN temp.indelingswijziging_wijken_en_buurten = 1 THEN
                        (SELECT id_master
                         FROM production.master_{layer_name}
                         WHERE temp.{layer_to_name_mapping[layer_name]}code = production.master_{layer_name}.{layer_to_name_mapping[layer_name]}code
                           AND temp.jaar - 1 = production.master_{layer_name}.jaar
                         LIMIT 1)
                    WHEN temp.indelingswijziging_wijken_en_buurten = 2 THEN
                        (SELECT id_master
                         FROM production.{layer_name}
                         WHERE ST_Equals(temp.geometry, production.{layer_name}.geometry)
                           AND temp.jaar - 1 = production.{layer_name}.jaar
                         LIMIT 1)
                    ELSE nextval('master_id_seq')
                END
            );

            DROP SEQUENCE master_id_seq;
            """)
        
        connect.exec_driver_sql(f"""
            INSERT INTO production.{layer_name} ({cols_list})
            SELECT {cols_list}
            FROM raw.temp_{layer_name}_{year} AS temp
            ON CONFLICT ({layer_to_name_mapping[layer_name]}code, jaar) DO UPDATE SET {update_list}
        """)
        connect.exec_driver_sql(f"DROP TABLE raw.temp_{layer_name}_{year};")