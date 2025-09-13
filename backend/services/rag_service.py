import chromadb
import openai
from config.config import (
    AZURE_EMBEDDING_ENDPOINT,
    AZURE_EMBEDDING_API_KEY,
    AZURE_EMBEDDING_API_VERSION,
    AZURE_EMBEDDING_DEPLOYMENT,
    CHROMA_DB_PATH,
    COLLECTION_NAME
)

# Initialize the Azure OpenAI client for embeddings
client = openai.AzureOpenAI(
    azure_endpoint=AZURE_EMBEDDING_ENDPOINT,
    api_version=AZURE_EMBEDDING_API_VERSION,
    api_key=AZURE_EMBEDDING_API_KEY
)

class RAGService:
    def __init__(self):
        """Initializes the ChromaDB client and gets the collection."""
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.collection = self.client.get_collection(name=COLLECTION_NAME)

    def query(self, query_text: str, n_results: int = 3) -> list:
        """Finds the most similar documents to the query_text."""
        try:
            # Generate the query embedding using the configured model
            response = client.embeddings.create(
                input=query_text,
                model=AZURE_EMBEDDING_DEPLOYMENT
            )
            query_embedding = response.data[0].embedding

            results = self.collection.query(
                # Query using the generated embedding vector
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            return results['documents'][0]
        except Exception as e:
            print(f"Error querying ChromaDB: {e}")
            return []
