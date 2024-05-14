import argparse
import os.path

import pandas as pd
import glob


def merge_csv(input_dir: str):
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Results directory {input_dir} does not exist.")
    # Define the path to your CSV files
    csv_files_path = os.path.join(input_dir, '*.csv')

    # List all CSV files in the specified path
    csv_files = glob.glob(csv_files_path)

    if len(csv_files) == 0:
        raise FileNotFoundError(f"No CSV files found in {input_dir}.")

    # Create an empty list to hold DataFrames
    dataframes = []

    # Loop through the list of CSV files and read each one into a DataFrame
    for csv_file in csv_files:
        # Read the CSV file
        df = pd.read_csv(csv_file)
        # Add a column for the file name or a tag
        df['tag'] = csv_file.split('/')[-1]  # You can modify this to add a more meaningful tag
        # Append the DataFrame to the list
        dataframes.append(df)

    # Concatenate all DataFrames into a single DataFrame
    merged_df = pd.concat(dataframes, ignore_index=True)

    # Optionally, save the merged DataFrame to a new CSV file
    merged_df.to_parquet(os.path.join(input_dir, 'merged_locust_data.parquet'), index=False)


if __name__ == "__main__":
    ar = argparse.ArgumentParser()
    ar.add_argument("--results-dir", type=str, required=True, help="Path to the results directory")
    a = ar.parse_args()
    merge_csv(a.results_dir)
