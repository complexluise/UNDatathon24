import pandas as pd
import requests
import os
import zipfile
import logging
from pathlib import Path
from enum import Enum
from tqdm import tqdm


class DataFormat(Enum):
    GEOPACKAGE = 'link_GeoPackage'
    GEODATABASE = 'link_FileGeodatabase'
    GEOJSON = 'link_GeoJson'
    CSV = 'link_CSV'
    SHAPEFILE = 'link_ShapeFile'
    KMZ = 'link_KMZ'


def download_and_extract(url: str, output_dir: Path) -> None:
    """
    Descarga y extrae un archivo zip de una URL dada.

    Args:
        url (str): URL del archivo zip a descargar
        output_dir (Path): Directorio donde se extraerá el contenido

    Returns:
        None
    """
    if not url.endswith('/'):
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            zip_path = output_dir / "temp.zip"

            with open(zip_path, 'wb') as f, tqdm(
                desc=f"Descargando {url.split('/')[-1]}",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for data in response.iter_content(chunk_size=1024):
                    size = f.write(data)
                    pbar.update(size)

            logging.info(f"Extrayendo archivo en {output_dir}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)

            os.remove(zip_path)
            logging.info("Extracción completada")


def process_geodata(formats: list[DataFormat] = [DataFormat.GEOJSON]):
    """
    Procesa y descarga datos geográficos desde un archivo CSV fuente.

    Args:
        formats (list[DataFormat], opcional): Lista de formatos a descargar.
            Por defecto descarga solo GeoJSON.

    Returns:
        None

    Ejemplo:
        >>> process_geodata([DataFormat.GEOJSON, DataFormat.CSV])
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.info("Iniciando proceso de descarga de datos")
    df = pd.read_csv('datasets/GeoMedellin/medellin_geodata_filtered.csv')
    base_dir = Path('datasets/GeoMedellin/data')

    # FIlter if needed

    for _, row in tqdm(list(df.iterrows()), desc="Procesando datasets"):
        theme_dir = base_dir / row['nombre_tematica'].replace(' ', '_')
        theme_dir.mkdir(parents=True, exist_ok=True)

        for format_type in formats:
            url = row[format_type.value]
            if pd.notna(url):
                format_dir = theme_dir / format_type.name.lower()
                format_dir.mkdir(exist_ok=True)
                logging.info(f"Procesando {row['nombre']} en formato {format_type.name}")
                download_and_extract(url, format_dir)

    logging.info("Proceso completado exitosamente")


if __name__ == "__main__":
    process_geodata()
