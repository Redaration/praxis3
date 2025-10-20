#!/usr/bin/env python3
"""
Cisco Web Scraper with ChromaDB RAG Implementation
A complete Python script that scrapes Cisco.com content and creates a RAG database.
"""

import subprocess
import sys
import os
import scrapy
from scrapy.crawler import CrawlerProcess
import chromadb
from chromadb.utils import embedding_functions

def install_packages():
    """Install required packages"""
    packages = ['scrapy', 'chromadb', 'transformers', 'sentence-transformers']
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")

# Install packages if running as standalone script
if __name__ == "__main__":
    print("Installing required packages...")
    install_packages()

# Define a simple spider
class CiscoSpider(scrapy.Spider):
    name = "cisco_text_spider"
    allowed_domains = ["cisco.com"]
    start_urls = ['https://www.cisco.com/c/en/us/solutions/index.html']
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'DOWNLOAD_DELAY': 1,  # Be respectful to the server
        'CONCURRENT_REQUESTS': 1,
    }

    def parse(self, response):
        """Extract text from common content tags, avoiding navigation/footer areas"""
        # Extract text from common content tags
        text_selectors = [
            '//main//p/text()',
            '//main//h1/text()',
            '//main//h2/text()',
            '//main//h3/text()',
            '//main//h4/text()',
            '//main//h5/text()',
            '//main//h6/text()',
            '//article//p/text()',
            '//section//p/text()',
            '//div[contains(@class, "content")]//p/text()',
        ]
        
        extracted_texts = []
        for selector in text_selectors:
            texts = response.xpath(selector).getall()
            extracted_texts.extend([text.strip() for text in texts if text.strip()])
        
        # If main content selectors don't work, fall back to general p and h tags
        if not extracted_texts:
            fallback_content = response.xpath('//p//text() | //h1//text() | //h2//text() | //h3//text()').getall()
            extracted_texts = [text.strip() for text in fallback_content if text.strip() and len(text.strip()) > 10]
        
        # Join all text content
        full_text = ' '.join(extracted_texts)
        
        if full_text:
            yield {'text': full_text}
        else:
            yield {'text': 'No content extracted from the page.'}

# Data storage for scraped content
scraped_data = []

class DataPipeline:
    """Pipeline to collect scraped data"""
    def process_item(self, item, spider):
        scraped_data.append(item['text'])
        print(f"Scraped {len(item['text'])} characters of content")
        return item

def run_spider():
    """Run the Scrapy spider"""
    print("Starting web scraping...")
    
    # Configure the crawler process
    process = CrawlerProcess(settings={
        'ITEM_PIPELINES': {'__main__.DataPipeline': 1},
        'LOG_LEVEL': 'INFO',
    })
    
    # Run the spider
    process.crawl(CiscoSpider)
    process.start()  # This will block until crawling is finished

def setup_chromadb():
    """Set up ChromaDB with RAG capabilities"""
    print("\nSetting up ChromaDB...")
    
    # Initialize Chroma client (in-memory for simplicity)
    chroma_client = chromadb.Client()
    
    # Define the embedding function using Hugging Face
    embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
    hf_ef = embedding_functions.HuggingFaceEmbeddingFunction(
        api_key=os.environ.get("HF_API_KEY"),  # Optional: use if you have an API key
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
    except Exception as e:
        try:
            collection = chroma_client.get_collection(
                name=collection_name,
                embedding_function=hf_ef
            )
            print(f"Using existing collection: {collection_name}")
        except:
            print(f"Error creating/accessing collection: {e}")
            return None, None
    
    return chroma_client, collection

def add_documents_to_chromadb(collection):
    """Add scraped documents to ChromaDB"""
    if not scraped_data:
        print("No data was scraped by the spider.")
        return False
    
    # Clean and prepare documents
    documents = [doc.strip() for doc in scraped_data if doc.strip()]
    
    if not documents:
        print("No non-empty documents to add to ChromaDB.")
        return False
    
    # Create simple IDs
    ids = [f"cisco_doc_{i}" for i in range(len(documents))]
    
    print(f"Adding {len(documents)} documents to ChromaDB...")
    
    try:
        # Split large documents into smaller chunks if needed
        chunked_documents = []
        chunked_ids = []
        
        for i, doc in enumerate(documents):
            # Split documents larger than 1000 characters into chunks
            if len(doc) > 1000:
                chunks = [doc[j:j+1000] for j in range(0, len(doc), 800)]  # 200 char overlap
                for k, chunk in enumerate(chunks):
                    chunked_documents.append(chunk)
                    chunked_ids.append(f"{ids[i]}_chunk_{k}")
            else:
                chunked_documents.append(doc)
                chunked_ids.append(ids[i])
        
        collection.add(
            documents=chunked_documents,
            ids=chunked_ids
        )
        print(f"Successfully added {len(chunked_documents)} document chunks.")
        return True
        
    except Exception as e:
        print(f"Error adding documents to ChromaDB: {e}")
        return False

def query_chromadb(collection):
    """Perform sample queries on the ChromaDB"""
    if collection.count() == 0:
        print("ChromaDB collection is empty, cannot perform queries.")
        return
    
    queries = [
        "What solutions does Cisco offer?",
        "network security",
        "cloud computing services"
    ]
    
    print(f"\nPerforming sample queries on {collection.count()} documents...")
    
    for query_text in queries:
        print(f"\n--- Query: '{query_text}' ---")
        
        try:
            results = collection.query(
                query_texts=[query_text],
                n_results=2
            )
            
            if results and 'documents' in results and results['documents']:
                for i, doc_list in enumerate(results['documents']):
                    for j, doc in enumerate(doc_list):
                        distance = results.get('distances', [[]])[i][j] if 'distances' in results else None
                        print(f"  Result {j+1}:")
                        print(f"    Document ID: {results.get('ids', [[]])[i][j]}")
                        if distance is not None:
                            print(f"    Distance: {distance:.4f}")
                        print(f"    Content preview: {doc[:200]}...")
                        print()
            else:
                print("  No documents found matching the query.")
                
        except Exception as e:
            print(f"  Error querying: {e}")

def main():
    """Main execution function"""
    print("=== Cisco Web Scraper with ChromaDB RAG ===")
    
    try:
        # Step 1: Run web scraping
        run_spider()
        
        # Step 2: Set up ChromaDB
        chroma_client, collection = setup_chromadb()
        if not collection:
            print("Failed to set up ChromaDB. Exiting.")
            return
        
        # Step 3: Add documents to ChromaDB
        success = add_documents_to_chromadb(collection)
        if not success:
            print("Failed to add documents to ChromaDB.")
            return
        
        # Step 4: Perform sample queries
        query_chromadb(collection)
        
        print("\n=== Script completed successfully! ===")
        
    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()