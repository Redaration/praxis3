# RAG Database Creation Script for macOS
# Adapted from Google Colab notebook

# Install required packages
# NOTE: On macOS, you may want to run these in a virtual environment first
# python -m venv venv
# source venv/bin/activate
# Run in Terminal or as a cell with ! prefix in Jupyter
"""
pip install scrapy chromadb transformers sentence-transformers
"""

import scrapy
from scrapy.crawler import CrawlerProcess
import chromadb
from chromadb.utils import embedding_functions
import os

# Define paths for macOS
# Store RAG data in the same directory as the project
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
RAG_DIR = os.path.join(PROJECT_DIR, "rag")

# Create the RAG directory if it doesn't exist
os.makedirs(RAG_DIR, exist_ok=True)

# Define a simple spider
class CiscoSpider(scrapy.Spider):
    name = "cisco_text_spider"
    allowed_domains = ["cisco.com"]
    start_urls = ['https://www.cisco.com/c/en/us/solutions/index.html']
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15'  # macOS-specific user agent
    }

    def parse(self, response):
        # Extract text from common content tags, avoiding known navigation/footer areas
        text_content = response.xpath('//p | //h1 | //h2 | //h3 | //h4 | //h5 | //h6').getall()
        yield {'text': ' '.join(text_content).strip()}

# --- Scrapy Execution ---
# We need to run Scrapy within the script. CrawlerProcess is suitable for this.
# The scraped data will be captured and stored in a list.
scraped_data = []

class DataPipeline:
    def process_item(self, item, spider):
        scraped_data.append(item['text'])
        return item

# Configure Scrapy process
process = CrawlerProcess(settings={
    'ITEM_PIPELINES': {'__main__.DataPipeline': 1},
    # macOS-specific settings (prevent temp file errors)
    'JOBDIR': os.path.join(RAG_DIR, "crawl_jobs"),
})

# Run the spider and wait for it to finish
process.crawl(CiscoSpider)
process.start() # the script will block here until the crawling is finished

# --- ChromaDB Setup and RAG ---
# Initialize Chroma client with persistent storage for macOS
# Using 'rag' directory as requested
persistence_directory = RAG_DIR
chroma_client = chromadb.PersistentClient(path=persistence_directory)

# Define the embedding function using local sentence-transformers model
# This doesn't require an API key
embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
hf_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=embedding_model_name
)

# Create or get a collection
collection_name = "cisco_rag_collection"
try:
    collection = chroma_client.create_collection(
        name=collection_name,
        embedding_function=hf_ef
    )
    print(f"Created collection: {collection_name}")
except:
    collection = chroma_client.get_collection(
        name=collection_name,
        embedding_function=hf_ef
    )
    print(f"Using existing collection: {collection_name}")


# Add the scraped data to the collection
if scraped_data:
    # Chroma expects lists for ids and documents
    documents = scraped_data
    # Simple IDs based on index
    ids = [f"doc_{i}" for i in range(len(documents))]

    # Clean empty documents before adding
    cleaned_documents = [doc for doc in documents if doc.strip()]
    cleaned_ids = [ids[i] for i, doc in enumerate(documents) if doc.strip()]

    if cleaned_documents:
        print(f"Adding {len(cleaned_documents)} documents to ChromaDB.")
        # Chroma's add method can handle the embedding generation
        collection.add(
            documents=cleaned_documents,
            ids=cleaned_ids
        )
        print("Documents added successfully.")
    else:
        print("No non-empty documents to add to ChromaDB.")
else:
    print("No data was scraped by the spider.")


# --- Sample Query ---
if collection.count() > 0:
    query_text = "What solutions does Cisco offer?"
    print(f"\nQuerying ChromaDB: '{query_text}'")

    results = collection.query(
        query_texts=[query_text],
        n_results=2 # Get top 2 results
    )

    print("\nQuery Results:")
    # Accessing results carefully as structure can vary
    if results and 'documents' in results and results['documents']:
        for i, doc_list in enumerate(results['documents']):
             print(f"Results for query '{query_text}':")
             for j, doc in enumerate(doc_list):
                 print(f"  Result {j+1}:")
                 print(f"    Document ID: {results.get('ids', [[]])[i][j]}")
                 # Truncate long documents for display
                 print(f"    Content: {doc[:200]}...") # Display first 200 characters
    else:
        print("No documents found matching the query.")

else:
    print("ChromaDB collection is empty, cannot perform a query.")

# Optional: Delete the collection if you want to start fresh on next run
# chroma_client.delete_collection(name=collection_name)
# print(f"\nDeleted collection: {collection_name}")
