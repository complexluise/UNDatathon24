import geopandas as gpd
from pathlib import Path


class GeoDataHandler:
    def __init__(self, geodata):
        self.geodata = geodata

    def filter_by_attribute(self, column: str, values: list):
        """Filter geodata by column values"""
        return GeoDataHandler(self.geodata[self.geodata[column].isin(values)])

    def count_by_attribute(self, column: str):
        """Count features grouped by column"""
        return self.geodata.groupby(column).size().reset_index(name='count')

    def spatial_join_count(self, other_layer: gpd.GeoDataFrame, join_column: str):
        """Count points within polygons"""
        joined = gpd.sjoin(other_layer, self.geodata, how='left', predicate='contains')
        return joined.groupby(join_column).size().reset_index(name='count')

    def buffer_analysis(self, distance):
        """Create buffer around features"""
        return GeoDataHandler(self.geodata.copy().buffer(distance))

    def calculate_area(self):
        """Calculate area for polygon features"""
        return self.geodata.area

    def calculate_density(self, area_column: str, value_column: str):
        """Calculate density (value per area)"""
        return self.geodata[value_column] / self.geodata[area_column]

    def find_nearest(self, other_layer: gpd.GeoDataFrame, k=1):
        """Find k-nearest features from other layer"""
        return GeoDataHandler(self.geodata.sjoin_nearest(other_layer, k=k))

    def dissolve_by_attribute(self, column: str):
        """Merge features based on attribute"""
        return GeoDataHandler(self.geodata.dissolve(by=column))

    def export_geojson(self, filepath: str, driver='GeoJSON'):
        """Export geodata to GeoJSON format"""
        output_path = Path(filepath)
        self.geodata.to_file(output_path, driver=driver)
        return self

    def simplify_geometry(self, tolerance=0.001):
        """Simplify geometries to reduce file size"""
        return GeoDataHandler(self.geodata.simplify(tolerance))

    def reproject(self, crs='EPSG:4326'):
        """Reproject to specified CRS (default WGS84 for web mapping)"""
        return GeoDataHandler(self.geodata.to_crs(crs))

    def add_centroid(self):
        """Add centroid coordinates as columns using proper projection"""
        # Project to UTM Zone 18N (Medellín) for accurate centroid calculation
        temp_geodata = self.geodata.to_crs('EPSG:32618')
        centroids = temp_geodata.geometry.centroid
        # Project centroids back to WGS84
        centroids = centroids.to_crs('EPSG:4326')
        self.geodata['longitude'] = centroids.x
        self.geodata['latitude'] = centroids.y
        return self
