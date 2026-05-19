import geopandas as gpd
from DatabaseAdapter import _create_engine
from DataFunctions.DatabaseMigrator import add_new_columns
from DataFunctions.DataTransformer import layer_to_name_mapping
from sqlalchemy import text

class DataLoader:
    def insert_raw_data(self, data: gpd.GeoDataFrame, layer_name: str, year: str):
        engine = _create_engine()
        data.to_postgis(layer_name + '_' + year, con=engine, if_exists='replace', index=False, schema = 'raw')

    def insert_production_data(self, layer_name: str, data_clean:gpd.GeoDataFrame, year: str):
        add_new_columns('production', layer_name, data_clean)
        engine = _create_engine()
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
                            COALESCE(
                                (SELECT id_master
                                FROM production.master_{layer_name}
                                WHERE temp.{layer_to_name_mapping[layer_name]}code = production.master_{layer_name}.{layer_to_name_mapping[layer_name]}code
                                AND temp.jaar = production.master_{layer_name}.jaar
                                LIMIT 1),
                                (SELECT id_master
                                FROM production.master_{layer_name}
                                WHERE temp.{layer_to_name_mapping[layer_name]}code = production.master_{layer_name}.{layer_to_name_mapping[layer_name]}code
                                AND temp.jaar - 1 = production.master_{layer_name}.jaar
                                LIMIT 1), 
                                nextval('master_id_seq'))
                        WHEN temp.indelingswijziging_wijken_en_buurten = 2 THEN
                            COALESCE(
                                (SELECT id_master
                                FROM production.{layer_name}
                                WHERE ST_Equals(temp.geometry, production.{layer_name}.geometry)
                                AND temp.jaar = production.{layer_name}.jaar
                                LIMIT 1),
                                (SELECT id_master
                                FROM production.{layer_name}
                                WHERE ST_Equals(temp.geometry, production.{layer_name}.geometry)
                                AND temp.jaar - 1 = production.{layer_name}.jaar
                                LIMIT 1),
                            nextval('master_id_seq'))
                        ELSE nextval('master_id_seq')
                    END
                );

                DROP SEQUENCE master_id_seq;
                """)
            result = connect.execute(text(f"SELECT id_master FROM raw.temp_{layer_name}_{year}"))
            print(result.fetchall())
            
            connect.exec_driver_sql(f"""
                INSERT INTO production.{layer_name} ({cols_list})
                SELECT {cols_list}
                FROM raw.temp_{layer_name}_{year} AS temp
                ON CONFLICT ({layer_to_name_mapping[layer_name]}code, jaar) DO UPDATE SET {update_list}
            """)
            connect.exec_driver_sql(f"""
                INSERT INTO production.master_{layer_name} (id_master, {layer_to_name_mapping[layer_name]}code, jaar)
                SELECT id_master, {layer_to_name_mapping[layer_name]}code, jaar
                FROM raw.temp_{layer_name}_{year}
                ON CONFLICT ({layer_to_name_mapping[layer_name]}code, jaar) DO UPDATE SET
                    {layer_to_name_mapping[layer_name]}code = EXCLUDED.{layer_to_name_mapping[layer_name]}code, 
                    jaar = EXCLUDED.jaar
            """)
            connect.exec_driver_sql(f"DROP TABLE raw.temp_{layer_name}_{year};")
