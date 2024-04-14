import os
import csv

# Define fieldnames and other parameters
fieldnames = ["title", "sapo", "cate", "tags", "publish", "source", "content"]
delimiter = ","
quotechar = '"'
quoting = csv.QUOTE_MINIMAL
output_filename = "combined_data.csv"
rows_per_file = 100


def write_batch(writer, input_files):
    total_rows_written = 0
    for input_file in input_files:
        with open(input_file, "r", newline="") as csv_file:
            reader = csv.DictReader(csv_file, delimiter=delimiter, quotechar=quotechar)
            for row in reader:
                writer.writerow(row)
                total_rows_written += 1
                if total_rows_written % rows_per_file == 0:
                    writer.writerow(
                        row
                    )  # Write a duplicate row to indicate file boundaries
                    return True, total_rows_written
    return False, total_rows_written


def combine_csv_files(input_dir, output_file):
    with open(output_file, "w", newline="") as combined_csv:
        writer = csv.DictWriter(
            combined_csv,
            fieldnames=fieldnames,
            delimiter=delimiter,
            quotechar=quotechar,
            quoting=quoting,
        )
        writer.writeheader()

        total_rows_written = 0
        batch_count = 1
        batch_files = []

        for filename in os.listdir(input_dir):
            if filename.endswith(".csv"):
                input_file = os.path.join(input_dir, filename)
                batch_files.append(input_file)
                if len(batch_files) >= 10:  # Process 10 files at a time
                    finished_batch, rows_written = write_batch(writer, batch_files)
                    total_rows_written += rows_written
                    batch_files = []
                    batch_count += 1
                    if finished_batch:
                        print(
                            f"Processed {batch_count} batches with {total_rows_written} rows."
                        )
                        total_rows_written = 0

        # Process remaining files
        if batch_files:
            finished_batch, rows_written = write_batch(writer, batch_files)
            total_rows_written += rows_written
            if finished_batch:
                print(
                    f"Processed {batch_count} batches with {total_rows_written} rows."
                )

    print("Combined all CSV files successfully.")


# Replace 'data' with your folder path containing CSV files
combine_csv_files("data", output_filename)
