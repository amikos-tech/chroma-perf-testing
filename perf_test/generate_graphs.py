import argparse

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the parquet file using pyarrow

import os

# Display the first few rows of the dataframe to understand its structure

# Set the style for the plots
sns.set(style="whitegrid")


def generate_graphs(result_dir: str, file_path: str) -> None:
    df = pd.read_parquet(file_path, engine='pyarrow')
    # Create a directory to save the plots

    if not os.path.exists(os.path.join(result_dir, "plots")):
        os.makedirs(os.path.join(result_dir, "plots"), exist_ok=True)

    # Histogram of Median Response Time
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Median Response Time'], bins=30, kde=True)
    plt.title('Distribution of Median Response Times')
    plt.xlabel('Median Response Time')
    plt.ylabel('Frequency')
    plt.savefig(f'{os.path.join(result_dir, "plots", "median_response_time_distribution.png")}')

    # Box Plot of Median Response Time by Name
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='Name', y='Median Response Time', data=df)
    plt.title('Median Response Times by Name')
    plt.xlabel('Name')
    plt.ylabel('Median Response Time')
    plt.xticks(rotation=90)
    plt.savefig(f'{os.path.join(result_dir, "plots", "median_response_time_by_name.png")}')

    # Box Plot of Median Response Time by Name
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='Name', y='Median Response Time', data=df)
    plt.title('Median Response Times by Name')
    plt.xlabel('Tag')
    plt.ylabel('Median Response Time')
    plt.xticks(rotation=90)
    plt.savefig(f'{os.path.join(result_dir, "plots", "median_response_time_by_tag.png")}')

    # Bar Plot of Request Count by Name
    plt.figure(figsize=(14, 7))
    sns.barplot(x='Name', y='Request Count', data=df)
    plt.title('Request Count by Name')
    plt.xlabel('Name')
    plt.ylabel('Request Count')
    plt.xticks(rotation=90)
    plt.savefig(f'{os.path.join(result_dir, "plots", "request_count_by_name.png")}')

    # Line Plot of Requests/s over 50th Percentile Response Time
    plt.figure(figsize=(14, 7))
    sns.lineplot(x='50%', y='Requests/s', hue='Name', data=df)
    plt.title('Requests per Second over 50th Percentile Response Time')
    plt.xlabel('50th Percentile Response Time')
    plt.ylabel('Requests/s')
    plt.legend(title='Name')
    plt.savefig(f'{os.path.join(result_dir, "plots", "requests_per_second_over_50th_percentile_response_time.png")}')

    # Line Plot of Requests/s over 95th Percentile Response Time
    plt.figure(figsize=(14, 7))
    sns.lineplot(x='95%', y='Requests/s', hue='Name', data=df)
    plt.title('Requests per Second over 95th Percentile Response Time')
    plt.xlabel('95th Percentile Response Time')
    plt.ylabel('Requests/s')
    plt.legend(title='Name')
    plt.savefig(f'{os.path.join(result_dir, "plots", "requests_per_second_over_95th_percentile_response_time.png")}')

    # Line Plot of Requests/s over 99th Percentile Response Time
    plt.figure(figsize=(14, 7))
    sns.lineplot(x='99%', y='Requests/s', hue='Name', data=df)
    plt.title('Requests per Second over 95th Percentile Response Time')
    plt.xlabel('99th Percentile Response Time')
    plt.ylabel('Requests/s')
    plt.legend(title='Name')
    plt.savefig(f'{os.path.join(result_dir, "plots", "requests_per_second_over_99th_percentile_response_time.png")}')


if __name__ == "__main__":
    ar = argparse.ArgumentParser()
    ar.add_argument("--results-dir", type=str, required=True, help="Path to the results directory")
    ar.add_argument("--results-file", type=str, required=True, help="Path to the merged results file.")
    a = ar.parse_args()
    generate_graphs(a.results_dir, a.results_file)
