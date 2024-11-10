import requests
import pandas as pd
import math

def fetch_geomedellin_data():
    base_url = "https://www.medellin.gov.co/apigeomedellin/geomed/buscador"
    records_per_page = 50
    all_data = []

    # Calculate total pages needed
    total_records = 1005
    total_pages = math.ceil(total_records / records_per_page)

    for page in range(total_pages):
        min_record = page * records_per_page
        max_record = records_per_page

        params = {
            'comp': 2,
            'page': page + 1,
            'min': min_record,
            'max': max_record,
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

    # Create DataFrame
    df = pd.DataFrame(all_data)

    # Save to CSV
    output_file = 'medellin_geodata.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Data saved to {output_file}")


if __name__ == "__main__":
    fetch_geomedellin_data()
