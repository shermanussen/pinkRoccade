import geopandas as gpd

class GpkgDataExtractor:
    layers = ['gemeente', 'wijk', 'buurt']
    layer_to_name_mapping = {
        'gemeente': 'gemeenten',
        'wijk': 'wijken',
        'buurt': 'buurten'
    }

    def __init__(self):
        self.data: dict[str, gpd.GeoDataFrame] = {}

    def load_data(self, source: str) -> dict[str, gpd.GeoDataFrame]:
        data = dict[str, gpd.GeoDataFrame]()
        for layer in self.layers:
            data[layer] = gpd.read_file(source, layer=self.layer_to_name_mapping[layer])
        return data