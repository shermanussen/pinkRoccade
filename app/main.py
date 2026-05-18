import json
from pathlib import Path
from DataFunctions.GpkgDataExtractor import GpkgDataExtractor
from DataFunctions.DataLoader import DataLoader

def main():
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    loader = DataLoader()

    for index, dataset_path_str in config.items():
        dataset_path = Path(dataset_path_str)
        
        if not dataset_path.exists():
            print(f"Warning: Dataset path for index '{index}' does not exist: {dataset_path}")
            continue
        data_extractor = GpkgDataExtractor()
        data = data_extractor.load_data(str(dataset_path))
        for layer_name, gdf in data.items():
            print(f"{dataset_path.name} - Layer: {layer_name}, Number of records: {len(gdf)}")
            loader.insert_raw_data(gdf, layer_name, index)

main()