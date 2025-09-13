import chromadb
from embedding_service import EmbeddingService

def verify_chromadb():
    """Verify ChromaDB connection and display statistics."""
    try:
        # Connect to the same persistent database
        client = chromadb.PersistentClient(path="./chroma_db")

        # Get the collection
        collection = client.get_collection(name="healthtech_kb")

        # Get the total number of items in the collection
        count = collection.count()

        print(f"✅ Verification successful!")
        print(f"   The 'healthtech_kb' collection contains {count} embeddings.")

        # Get more detailed stats using the embedding service
        try:
            embedding_service = EmbeddingService()
            stats = embedding_service.get_collection_stats()
            
            print(f"\n📊 Detailed Statistics:")
            print(f"   Total chunks: {stats.get('total_chunks', 0)}")
            print(f"   Unique documents: {stats.get('unique_documents', 0)}")
            print(f"   Chunk types: {stats.get('chunk_types', {})}")
            print(f"   Collection name: {stats.get('collection_name', 'Unknown')}")
            
        except Exception as e:
            print(f"   Warning: Could not get detailed stats: {e}")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        print(f"   Make sure ChromaDB is properly initialized.")
        print(f"   Run 'python init_database.py' to initialize the database.")

def test_search():
    """Test search functionality."""
    try:
        embedding_service = EmbeddingService()
        
        # Test queries
        test_queries = [
            "validation",
            "FDA compliance",
            "software development",
            "documentation requirements"
        ]
        
        print(f"\n🔍 Testing Search Functionality:")
        print(f"=" * 40)
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            results = embedding_service.search_similar_documents(query, n_results=2)
            
            if results['total_found'] > 0:
                print(f"   ✅ Found {results['total_found']} results")
                for i, doc in enumerate(results['results']['documents'][0][:2]):
                    metadata = results['results']['metadatas'][0][i]
                    print(f"     {i+1}. {metadata.get('filename', 'Unknown')}")
                    print(f"        Preview: {doc[:80]}...")
            else:
                print(f"   ❌ No results found")
        
    except Exception as e:
        print(f"❌ Error testing search: {e}")

if __name__ == "__main__":
    print("🔍 ChromaDB Verification")
    print("=" * 30)
    
    verify_chromadb()
    test_search()
    
    print(f"\n✅ Verification complete!")
    print(f"   If you see errors, run: python init_database.py")