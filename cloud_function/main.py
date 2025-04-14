from flask import Flask, request, jsonify
from google.cloud import bigquery
import vertexai
from vertexai.language_models import TextEmbeddingModel, TextGenerationModel
import os
import functions_framework
from google.auth import exceptions
from google.auth.transport.requests import Request

# === INIT ===
app = Flask(__name__)
vertexai.init(project="gcp-hackathon-456421", location="us-central1")

# Set up BigQuery and Vertex AI models
bq = bigquery.Client()
embed_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
llm = TextGenerationModel.from_pretrained("gemini-pro")

# Dataset and Table Configuration
PROJECT_ID = "gcp-hackathon-456421"  # Replace with your Google Cloud project ID
DATASET_ID = "guide_data"  # Dataset name
TABLE_ID = "vector_index"  # Table name
BQ_TABLE = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"  # Fully qualified table name




# POST Request handler for the Cloud Function
@app.route("/my-handler", methods=["POST"])
def handler():
    data = request.get_json()
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Get embedding for the question using Vertex AI
    embedding = embed_model.get_embeddings([question])[0].values

    # Convert embedding to a string representation for the query
    embedding_str = ', '.join(map(str, embedding))

    # Query BigQuery to find the most similar documents
    query = f"""
        SELECT text, ML.DOT_PRODUCT(embedding, ARRAY[{embedding_str}]) AS score
        FROM `{BQ_TABLE}`  -- Use backticks for table name
        ORDER BY score DESC
        LIMIT 3
    """
    df = bq.query(query).to_dataframe()
    context = "\n".join([f"- {row['text']}" for _, row in df.iterrows()])

    # Use the LLM model for answer generation
    prompt = f"Based on the following guide docs:\n{context}\n\nAnswer: {question}"
    response = llm.predict(prompt=prompt)
    return jsonify({"answer": response.text})

@functions_framework.http
def cloud_function(request):
    return app(request)

# The entry point for Google Cloud Functions
def cloud_function(request):
    return app(request)