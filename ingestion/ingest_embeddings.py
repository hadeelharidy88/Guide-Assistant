from google.cloud import language_v1
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

# === CONFIG ===
PROJECT_ID = "gcp-hackathon-456421" 
DATASET_ID = "guide_data" 
TABLE_ID = "vector_index" 
BQ_TABLE = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}" 

# === INIT ===
client = language_v1.LanguageServiceClient()
bq = bigquery.Client(project=PROJECT_ID)

# Define schema for the BigQuery table
schema = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("text", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("sentiment_score", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("sentiment_magnitude", "FLOAT", mode="NULLABLE"),
]

# Ensure the dataset exists, and create it if not
try:
    dataset_ref = bq.dataset(DATASET_ID)
    bq.get_dataset(dataset_ref)
    print(f"Dataset '{DATASET_ID}' exists.")
except NotFound:
    print(f" Dataset '{DATASET_ID}' not found. Creating it now...")
    bq.create_dataset(dataset_ref)
    print(f" Dataset '{DATASET_ID}' created.")

# Ensure the table exists, and create it if not
table_ref = bq.dataset(DATASET_ID).table(TABLE_ID)
try:
    bq.get_table(table_ref)
    print(f" Table '{TABLE_ID}' exists.")
except NotFound:
    print(f" Table '{TABLE_ID}' not found. Creating it now...")
    table = bigquery.Table(table_ref, schema=schema)
    bq.create_table(table)
    print(f" Table '{TABLE_ID}' created.")

# Replace with your actual text data
docs = [
    "How to deploy a Cloud Function on GCP?",
    "How to create BigQuery tables?",
    "How IAM roles work in Google Cloud?",
]

rows_to_insert = []

for i, doc in enumerate(docs):
    print(f"Analyzing doc {i+1}: {doc}")

    # Analyze the sentiment of the document
    document = language_v1.Document(content=doc, type_=language_v1.Document.Type.PLAIN_TEXT)
    sentiment = client.analyze_sentiment(request={'document': document}).document_sentiment

    row = {
        "id": f"doc_{i}",
        "text": doc,
        "sentiment_score": sentiment.score,
        "sentiment_magnitude": sentiment.magnitude,
    }

    rows_to_insert.append(row)

# INSERT INTO BIGQUERY 
errors = bq.insert_rows_json(BQ_TABLE, rows_to_insert)

if errors == []:
    print("✅ Successfully inserted sentiment analysis results into BigQuery.")
else:
    print("❌ Failed to insert rows:", errors)