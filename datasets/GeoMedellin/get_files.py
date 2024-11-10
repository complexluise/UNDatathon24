import pandas as pd
import requests
import os
import zipfile
from pathlib import Path
from enum import Enum


class DataFormat(Enum):
    GEOPACKAGE = 'link_GeoPackage'
    GEODATABASE = 'link_FileGeodatabase'
    GEOJSON = 'link_GeoJson'
    CSV = 'link_CSV'
    SHAPEFILE = 'link_ShapeFile'
    KMZ = 'link_KMZ'


def download_and_extract(url: str, output_dir: Path) -> None:
    if not url.endswith('/'):
        response = requests.get(url)
        if response.status_code == 200:
            zip_path = output_dir / "temp.zip"
            with open(zip_path, 'wb') as f:
                f.write(response.content)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)

            os.remove(zip_path)


def process_geodata(formats: list[DataFormat] = [DataFormat.GEOJSON]):
    # Read the CSV file
    df = pd.read_csv('datasets/GeoMedellin/medellin_geodata_filtered.csv')

    # Create base directory for organized data
    base_dir = Path('datasets/GeoMedellin/data')

    for _, row in df.iterrows():
        # Create directory structure based on tematica
        theme_dir = base_dir / row['nombre_tematica'].replace(' ', '_')
        theme_dir.mkdir(parents=True, exist_ok=True)

        # Download and extract selected formats
        for format_type in formats:
            url = row[format_type.value]
            if pd.notna(url):
                format_dir = theme_dir / format_type.name.lower()
                format_dir.mkdir(exist_ok=True)
                download_and_extract(url, format_dir)


if __name__ == "__main__":
    # Example usage with just GEOJSON
    process_geodata()

    # Example usage with multiple formats
    # process_geodata([DataFormat.GEOJSON, DataFormat.CSV, DataFormat.SHAPEFILE])
