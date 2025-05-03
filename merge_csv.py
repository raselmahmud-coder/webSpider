import pandas as pd


def merge_csv(file1_path, file2_path, output_path):
    # Read the two CSV files into DataFrames
    df1 = pd.read_csv(file1_path)
    df2 = pd.read_csv(file2_path)

    # Concatenate the two DataFrames
    merged_df = pd.concat([df1, df2], ignore_index=True)

    # Save the merged DataFrame to a new CSV file
    merged_df.to_csv(output_path, index=False)

    print("CSV files merged successfully and saved to:", output_path)


# Example usage:
file1 = 'E:\VM\data\company_data.csv'
file2 = 'E:\VM\local_web_spider\company_data.csv'
output_file = 'E:\VM\\final_job_data\merged_company_data.csv'

merge_csv(file1, file2, output_file)
