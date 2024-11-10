import requests
import pandas as pd
import math


def process_formats(formats_str):
    base_url = "https://www.medellin.gov.co/apigeomedellin/atributos/archivos/openDataExt/"
    formats_list = formats_str.split('--/') if formats_str else []
    processed_formats = {}

    for format_item in formats_list:
        parts = format_item.split('--')
        if len(parts) >= 4:
            format_type = parts[2]
            path = parts[3]
            processed_formats[format_type] = base_url + path

    return processed_formats


def fetch_geomedellin_data():
    base_url = "https://www.medellin.gov.co/apigeomedellin/geomed/buscador"
    records_per_page = 50
    all_data = []

    total_records = 1005
    total_pages = math.ceil(total_records / records_per_page)

    for page in range(total_pages):
        min_record = page * records_per_page
        params = {
            'comp': 2,
            'page': page + 1,
            'min': min_record,
            'max': records_per_page,
            'element': '',
            'filtros': 'W3siVGlwbyI6W119LHsiVGVtYXRpY2FzIjpbbnVsbF19LHsiT3JkZW4iOlsyXX0seyJSZWNpZW50ZSI6WzFdfSx7IkZvcm1hdG9zIjpbXX0seyJDYXRlZ29yaWEiOltdfSx7IkZlY2hhcyI6W119XQ==',
            'texto': '',
            'superAdmin': 'false'
        }

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            all_data.extend(data['data'])
            print(f"Fetched page {page + 1}/{total_pages}")
        else:
            print(f"Error fetching page {page + 1}: {response.status_code}")

    # Create initial DataFrame
    df = pd.DataFrame(all_data)

    # Select required columns
    selected_columns = [
        'id_fuente_dato',
        'id_tipo_fuente',
        'metadato_privado',
        'fecha_publicacion',
        'fecha_actualizacion',
        'id_tipo_licencia',
        'id_termino_condiciones',
        'nombre',
        'descripcion',
        'formatos',
        'nombre_tematica',
        'dependencia',
        'id_metadata'
    ]

    df_filtered = df[selected_columns].copy()

    # Process formats into separate columns with download links
    df_filtered['processed_formats'] = df_filtered['formatos'].apply(process_formats)

    # Create separate columns for each format type
    format_types = ['GeoPackage', 'FileGeodatabase', 'GeoJson', 'CSV', 'ShapeFile', 'KMZ']
    for format_type in format_types:
        df_filtered[f'link_{format_type}'] = df_filtered['processed_formats'].apply(
            lambda x: x.get(format_type, '')
        )

    # Drop the intermediate formats columns
    df_filtered = df_filtered.drop(['formatos', 'processed_formats'], axis=1)

    # Save to CSV
    output_file = 'medellin_geodata_filtered.csv'
    df_filtered.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Data saved to {output_file}")

    return df_filtered


if __name__ == "__main__":
    df = fetch_geomedellin_data()
