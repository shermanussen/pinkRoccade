from DatabaseAdapter import _create_engine
from DataFunctions.DatabaseMigrator import get_table_columns, add_new_columns
import geopandas as gpd
import pandas as pd
from sqlalchemy import text

layer_to_name_mapping = {
    'gemeenten': 'gemeente',
    'wijken': 'wijk',
    'buurten': 'buurt'
}

bad_values = [-99997, 99997, 99995, 99991]

def remove_duplicates(data: gpd.GeoDataFrame, layer: str):
    key_cols = [layer_to_name_mapping[layer] + 'code', 'jaar']
    dup_mask = data.duplicated(subset=key_cols, keep=False)
    bad_mask = data.isin(bad_values).any(axis=1)
    dup_groups = data[dup_mask].groupby(key_cols, sort=False)

    rows_to_keep = []

    for _, group in dup_groups:
        merged_row = group.iloc[0].copy()
        for _, other_row in group.iloc[1:].iterrows():
            for col in data.columns:
                if merged_row[col] in bad_values and other_row[col] not in bad_values:
                    merged_row[col] = other_row[col]

        rows_to_keep.append(merged_row)
    non_dups = data[~dup_mask]
    df_clean = pd.concat(
        [non_dups, gpd.GeoDataFrame(rows_to_keep)],
        ignore_index=True
    )
    return df_clean
    

def replace_fauly_values_with_null(data: gpd.GeoDataFrame):
    bad_values = [-99997, 99997, 99995, 99991]
    return data.replace(bad_values, pd.NA)

def transform_data(layer_name: str, year: str, data:gpd.GeoDataFrame):
    data_deduplicated = remove_duplicates(data, layer_name)
    data_clean = replace_fauly_values_with_null(data_deduplicated)
    print(f"Data cleaned for layer: {layer_name}, year: {year}")
    return data_clean