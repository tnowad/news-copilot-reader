import csv
import json
import os


# Function to process a CSV file and extract article data
def process_csv(file_path, limit=10000):
    articles = []
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(
            csvfile,
            fieldnames=fieldnames,
            delimiter=delimiter,
            quotechar=quotechar,
            quoting=quoting,
        )
        count = 0
        for row in reader:
            if count >= limit:
                break
            entry = {
                "title": row["title"],
                "summary": row["sapo"],
                "categories": row["cate"].split(
                    ","
                ),  # Assuming categories are separated by comma
                "tags": row["tags"].split(","),  # Assuming tags are separated by comma
                "create_at": row["publish"],
                "content": row["content"],
                "slug": row["source"],  # Assuming source is the slug
            }
            articles.append(entry)
            count += 1
    return articles


# Define the fieldnames and CSV parameters
fieldnames = ["title", "sapo", "cate", "tags", "publish", "source", "content"]
delimiter = ","
quotechar = '"'
quoting = csv.QUOTE_MINIMAL  # This will handle minimal quoting

# Define the folder containing the CSV files
folder_path = "data"

# Initialize an empty list to store all articles
all_articles = []

# Iterate over each CSV file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(folder_path, filename)
        articles = process_csv(file_path, limit=10000)
        all_articles.extend(articles)

# Save all articles to a single JSON file
with open("articles.json", "w", encoding="utf-8") as jsonfile:
    json.dump(all_articles, jsonfile, ensure_ascii=False, indent=4)
