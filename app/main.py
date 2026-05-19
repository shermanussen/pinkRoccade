import json
from pathlib import Path
from DataFunctions.GpkgDataExtractor import GpkgDataExtractor
from DataFunctions.DataLoader import DataLoader

def get_dataset_paths() -> dict[str, str]:
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    return config

def main():
    loader = DataLoader()

    for index, dataset_path_str in get_dataset_paths().items():
        dataset_path = Path(dataset_path_str)
        
        if not dataset_path.exists():
            print(f"Warning: Dataset path for index '{index}' does not exist: {dataset_path}")
            continue
        data_extractor = GpkgDataExtractor()
        data = data_extractor.load_data(str(dataset_path))
        for layer_name, gdf in data.items():
            print(f"{dataset_path.name} - Layer: {layer_name}, Number of records: {len(gdf)}")

            # Insert raw data into the database
            loader.insert_raw_data(gdf, layer_name, index)
            loader.insert_production_data(layer_name, gdf, index)

main()