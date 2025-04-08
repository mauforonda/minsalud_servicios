#!/usr/bin/env python

import pandas as pd
from tqdm import tqdm
from common import load_conf
import os

filenames = load_conf(['filenames'])
index = pd.read_csv(filenames['clean'])
prefix = "minsalud_servicios"

def read_file(filename, service_group, service):
    """
    Read a single `clean` file, append service columns.
    """

    df = pd.read_csv(
        filename, 
        dtype={'department': 'category', 'municipality_id': int, 'municipality': 'category', 'year':int, 'month':int, 'population':str, 'value':float}
    )
    if df.shape[0] > 0:
        for col, value in zip(['service', 'service_group'], [service, service_group]):
            df.insert(0, col, value)
        return df

def create_release(index_rows, filename):
    """
    Read, concatenate and apply correct types to a collection
    of rows in the `clean` index, then save all as a parquet file.
    """

    complete = []
    
    for i, row in tqdm(index_rows.iterrows(), total=index_rows.shape[0]):
        
        complete.append(
            read_file(row['file'], row['service_group'], row['service'])
        )

    complete = pd.concat(complete)
    complete = complete.astype({
        'service_group':'category', 'service':'category', 'department': 'category', 'municipality_id': int, 'municipality': 'category', 'year':int, 'month':int, 'population':str, 'value':float
    })
    
    complete.sort_values(['year', 'month', 'department', 'service_group', 'service', 'population', 'municipality_id']).to_parquet(
        filename,
        engine='pyarrow',
        compression='zstd',
        index=False,
        row_group_size=1e7
    )

# Make a release for each year.
os.makedirs("releases", exist_ok=True)
for year in index.year.unique():
    print(f"Release for {year} ...")
    create_release(index[index.year == year], f"releases/{prefix}_{year}.parquet")
    
# And a release for all.
print("Release for all ...")
create_release(index, f"releases/{prefix}_complete.parquet")