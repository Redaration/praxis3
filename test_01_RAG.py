#!/usr/bin/env python3
"""
Cisco AI PDF RAG Database Query Interface
--------------------------------------
This script provides a simple interactive interface to query the Cisco PDF-based RAG database.
Enter questions about Cisco's AI technologies and get relevant information from the PDF documents.

Usage:
    To run as an interactive script:
        python test_01_RAG.py

    To use as a module:
        from test_01_RAG import query_rag_database
        results = query_rag_database("Your query here")
"""

import os
import chromadb
from chromadb.utils import embedding_functions

# Define paths (same as in a01_RAG_DB_Creation.py)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
RAG_DIR = os.path.join(PROJECT_DIR, "rag")

def query_rag_database(query_text, num_results=3):
    """
    Query the RAG database with the given text and return results
    
    Args:
        query_text: The question or query text
        num_results: Number of top results to return (default: 3)
        
    Returns:
        Dictionary containing query results or None if error occurs
    """
    try:
        # Initialize ChromaDB client with the same persistent storage
        chroma_client = chromadb.PersistentClient(path=RAG_DIR)
        
        # Use the same embedding function as in creation
        embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        hf_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model_name
        )
        
        # Get the collection
        collection_name = "cisco_ai_pdf_collection"
        collection = chroma_client.get_collection(
            name=collection_name,
            embedding_function=hf_ef
        )
        
        # Check if collection has documents
        if collection.count() == 0:
            print("Error: The RAG database is empty. Run a01_RAG_DB_Creation_PDF.py first.")
            return None
        
        # Query the collection
        results = collection.query(
            query_texts=[query_text],
            n_results=num_results
        )
        
        return results
    
    except Exception as e:
        print(f"Error querying RAG database: {str(e)}")
        return None

def display_results(results, query_text):
    """
    Display the query results in a formatted way
    
    Args:
        results: The query results from ChromaDB
        query_text: The original query text
    """
    if not results or 'documents' not in results or not results['documents']:
        print("No relevant information found in the database.")
        return
    
    print("\n" + "="*80)
    print(f"QUERY: {query_text}")
    print("="*80)
    
    # Display each result with metadata
    for i, doc_list in enumerate(results['documents']):
        for j, doc in enumerate(doc_list):
            print(f"\nRESULT {j+1}:")
            print(f"Document ID: {results.get('ids', [[]])[i][j]}")
            
            # Calculate similarity score if available
            if 'distances' in results and results['distances']:
                # Distance might be cosine distance where lower is better
                # or direct similarity where higher is better - handle both cases
                distance = results['distances'][i][j]
                similarity = distance if distance > 0 else 1.0 + distance
                print(f"Relevance: {abs(similarity):.2%}")
            
            # Format and display content
            content = doc.strip()
            
            # Clean up the content (remove HTML tags and excess whitespace)
            import re
            content = re.sub('<.*?>', '', content)
            content = re.sub(r'\s+', ' ', content).strip()
            
            # Truncate very long documents for display, with ellipsis
            if len(content) > 500:
                content = content[:500] + "..."
            
            print("-"*80)
            print(content)
            print("-"*80)
    
    print("\n")

def main():
    """Main interactive query loop"""
    print("\n" + "="*80)
    print("Cisco AI PDF RAG Database Query Interface")
    print("="*80)
    print("Ask questions about Cisco's AI technologies, or type 'exit' to quit.\n")
    print("The database contains information from the following PDF documents:")
    print(" - Cisco Responsible AI Principles and Framework")
    print(" - Cisco AI Defense")
    print(" - Cisco AI Pods")
    print(" - Cisco CX Agentic AI Research")
    print(" - Cisco DNA AI/ML Primer\n")
    
    try:
        while True:
            # Get user input
            query = input("\nEnter your question: ").strip()
            
            # Check for exit command
            if query.lower() in ["exit", "quit", "q"]:
                print("Thank you for using the Cisco RAG Database Query Interface. Goodbye!")
                break
                
            # Skip empty queries
            if not query:
                continue
                
            # Process the query
            results = query_rag_database(query)
            
            # Display results
            if results:
                display_results(results, query)
    except EOFError:
        # Handle piped input (e.g., from echo command)
        pass
    except KeyboardInterrupt:
        print("\nOperation cancelled. Exiting.")
    finally:
        print("\nThank you for using the Cisco AI PDF RAG Database Query Interface.")

if __name__ == "__main__":
    main()
