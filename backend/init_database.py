#!/usr/bin/env python3
"""
Script to initialize ChromaDB with existing documents in the data folder.
This will parse and store embeddings for all documents in the data directory.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.parser import parse_document
from services.embedding_service import EmbeddingService, process_and_store_document
from config.config import validate_config

def initialize_document_database():
    """Initialize ChromaDB with documents from the data folder."""
    
    # Validate configuration
    try:
        validate_config()
        print("✅ Configuration validated successfully")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Initialize embedding service
    try:
        embedding_service = EmbeddingService()
        print("✅ Embedding service initialized")
    except Exception as e:
        print(f"❌ Failed to initialize embedding service: {e}")
        return False
    
    # Get data directory
    data_dir = Path(__file__).parent / "data"
    
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return False
    
    # Find all supported documents
    supported_extensions = ['.pdf', '.docx']
    documents = []
    
    for ext in supported_extensions:
        documents.extend(data_dir.glob(f"*{ext}"))
    
    if not documents:
        print(f"❌ No supported documents found in {data_dir}")
        print(f"   Looking for files with extensions: {supported_extensions}")
        return False
    
    print(f"📁 Found {len(documents)} documents to process:")
    for doc in documents:
        print(f"   - {doc.name}")
    
    # Process each document
    successful = 0
    failed = 0
    
    for doc_path in documents:
        try:
            print(f"\n📄 Processing: {doc_path.name}")
            
            # Read file content
            with open(doc_path, 'rb') as f:
                file_content = f.read()
            
            # Parse document
            print(f"   Parsing document...")
            parsed_data = parse_document(file_content, doc_path.name)
            
            # Store embeddings
            print(f"   Storing embeddings...")
            result = process_and_store_document(parsed_data, doc_path.name)
            
            if result['status'] == 'success':
                print(f"   ✅ Success: {result['chunks_stored']} chunks stored")
                successful += 1
            elif result['status'] == 'already_exists':
                print(f"   ℹ️  Already exists: skipped")
                successful += 1
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ Error processing {doc_path.name}: {e}")
            failed += 1
    
    # Print summary
    print(f"\n📊 Summary:")
    print(f"   ✅ Successfully processed: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📄 Total documents: {len(documents)}")
    
    # Get final stats
    try:
        stats = embedding_service.get_collection_stats()
        print(f"\n📈 ChromaDB Statistics:")
        print(f"   Total chunks: {stats.get('total_chunks', 0)}")
        print(f"   Unique documents: {stats.get('unique_documents', 0)}")
        print(f"   Chunk types: {stats.get('chunk_types', {})}")
    except Exception as e:
        print(f"   ❌ Error getting stats: {e}")
    
    return successful > 0

def verify_database():
    """Verify the database contains data."""
    try:
        embedding_service = EmbeddingService()
        stats = embedding_service.get_collection_stats()
        
        print(f"\n🔍 Database Verification:")
        print(f"   Collection: {stats.get('collection_name', 'Unknown')}")
        print(f"   Total chunks: {stats.get('total_chunks', 0)}")
        print(f"   Unique documents: {stats.get('unique_documents', 0)}")
        
        if stats.get('total_chunks', 0) > 0:
            print("   ✅ Database contains data")
            return True
        else:
            print("   ❌ Database is empty")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verifying database: {e}")
        return False

def search_test(query: str = "validation"):
    """Test search functionality."""
    try:
        print(f"\n🔍 Testing search with query: '{query}'")
        embedding_service = EmbeddingService()
        results = embedding_service.search_similar_documents(query, n_results=3)
        
        if results['total_found'] > 0:
            print(f"   ✅ Found {results['total_found']} results:")
            for i, doc in enumerate(results['results']['documents'][0][:3]):
                metadata = results['results']['metadatas'][0][i]
                print(f"     {i+1}. {metadata.get('filename', 'Unknown')} - {doc[:100]}...")
        else:
            print("   ❌ No results found")
            
    except Exception as e:
        print(f"   ❌ Error testing search: {e}")

if __name__ == "__main__":
    print("🚀 Initializing Document Database...")
    print("=" * 50)
    
    # Initialize database
    success = initialize_document_database()
    
    if success:
        # Verify database
        verify_database()
        
        # Test search
        search_test("validation")
        search_test("FDA")
        
        print("\n🎉 Database initialization completed successfully!")
        print("\nYou can now:")
        print("   1. Start the API server: python main.py")
        print("   2. Upload documents through the web interface")
        print("   3. Search documents using the API endpoints")
        
    else:
        print("\n❌ Database initialization failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)
