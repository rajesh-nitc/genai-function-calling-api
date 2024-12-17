from dotenv import load_dotenv

load_dotenv()
import os

import pandas as pd
import vertexai
from google.cloud import storage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

file_path = os.path.join(os.path.dirname(__file__), "retail_toy_dataset.csv")
print(file_path)
REGION = os.getenv("REGION")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
MODEL_EMB = os.getenv("MODEL_EMB")
BUCKET_EMB = os.getenv("BUCKET_EMB")
DIMENSIONALITY = int(os.getenv("DIMENSIONALITY"))  # type: ignore
TASK = os.getenv("TASK")
BLOB_NAME = os.getenv("BLOB_NAME")
DF_HEAD = int(os.getenv("DF_HEAD"))  # type: ignore


def load_dataset(location) -> pd.DataFrame:
    """Loads the dataset from the specified location"""
    df = pd.read_csv(location)
    df = df.loc[:, ["product_id", "product_name", "description", "list_price"]]
    df = df.dropna()
    return df.head(DF_HEAD)


def split_product_descriptions(df: pd.DataFrame):
    """Splits long product descriptions into smaller chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        separators=[".", "\n"],
        chunk_size=500,
        chunk_overlap=0,
        length_function=len,
    )
    chunked = []
    for _, row in df.iterrows():
        product_name = row["product_name"]
        desc = row["description"]
        splits = text_splitter.create_documents([desc])
        for s in splits:
            r = {
                "product_name": product_name,
                "content": s.page_content,
            }
            chunked.append(r)
    return chunked


def generate_vector_embeddings(df: pd.DataFrame, batch_size=5):
    """Generate vector embeddings for each chunk of text and save to GCS."""
    vertexai.init(project=GOOGLE_CLOUD_PROJECT, location=REGION)
    model = TextEmbeddingModel.from_pretrained(MODEL_EMB)  # type: ignore
    chunked = split_product_descriptions(df)
    print(f"chunked: {chunked}")

    for i in range(0, len(chunked), batch_size):
        texts = [x["content"] for x in chunked[i : i + batch_size]]
        inputs = [TextEmbeddingInput(text, TASK) for text in texts]
        embeddings = model.get_embeddings(inputs, auto_truncate=False, output_dimensionality=DIMENSIONALITY)  # type: ignore
        for x, e in zip(chunked[i : i + batch_size], embeddings):
            x["embedding"] = e.values

    product_embeddings = pd.DataFrame(chunked)

    # Rename the column
    product_embeddings = product_embeddings.rename(columns={"product_name": "id"})
    print(product_embeddings.head(25))

    # Save as JSONL to GCS
    save_to_gcs_as_json(product_embeddings, BUCKET_EMB, BLOB_NAME)  # type: ignore

    return product_embeddings


def save_to_gcs_as_json(dataframe: pd.DataFrame, BUCKET_EMB: str, blob_name: str):
    """
    Save a DataFrame as a JSON in a GCS bucket.

    Args:
        dataframe (pd.DataFrame): DataFrame to save.
        BUCKET_EMB (str): Name of the GCS bucket.
        blob_name (str): Destination path and file name in the GCS bucket.
    """
    # Convert DataFrame to JSON string
    json_string = dataframe.to_json(
        orient="records", lines=True
    )  # 'records' for each row as a dict

    # Initialize GCS client
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_EMB)
    blob = bucket.blob(blob_name)

    # Upload JSON string to GCS
    blob.upload_from_string(json_string, content_type="application/json")
    print(f"File saved to GCS: gs://{BUCKET_EMB}/{blob_name}")


def main():
    df = load_dataset(file_path)
    generate_vector_embeddings(df)


if __name__ == "__main__":
    main()