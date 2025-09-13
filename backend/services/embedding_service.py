import chromadb
import openai
import uuid
import hashlib
from typing import List, Dict, Any
from config.config import (
    AZURE_EMBEDDING_ENDPOINT,
    AZURE_EMBEDDING_API_KEY,
    AZURE_EMBEDDING_API_VERSION,
    AZURE_EMBEDDING_DEPLOYMENT,
    CHROMA_DB_PATH,
    COLLECTION_NAME
)

class EmbeddingService:
    """Service to handle document embeddings and ChromaDB operations."""
    
    def __init__(self):
        """Initialize the embedding service with Azure OpenAI and ChromaDB clients."""
        # Initialize Azure OpenAI client for embeddings
        self.openai_client = openai.AzureOpenAI(
            azure_endpoint=AZURE_EMBEDDING_ENDPOINT,
            api_version=AZURE_EMBEDDING_API_VERSION,
            api_key=AZURE_EMBEDDING_API_KEY
        )
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(name=COLLECTION_NAME)
            print(f"✅ Connected to existing collection: {COLLECTION_NAME}")
        except:
            self.collection = self.chroma_client.create_collection(name=COLLECTION_NAME)
            print(f"✅ Created new collection: {COLLECTION_NAME}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a given text using Azure OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model=AZURE_EMBEDDING_DEPLOYMENT
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    def create_document_id(self, filename: str, content_hash: str) -> str:
        """Create a unique document ID based on filename and content hash."""
        combined = f"{filename}_{content_hash}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def create_content_hash(self, content: str) -> str:
        """Create a hash of the document content for uniqueness checking."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for better embedding storage."""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                sentence_ends = ['.', '!', '?', '\n']
                best_break = end
                
                for i in range(max(start + chunk_size - 100, start), min(end + 100, len(text))):
                    if text[i] in sentence_ends:
                        best_break = i + 1
                        break
                
                end = best_break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def store_document_embeddings(self, parsed_document: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Store document embeddings in ChromaDB with metadata."""
        try:
            # Extract content
            full_text = parsed_document.get('full_text', '')
            sections = parsed_document.get('sections', {})
            metadata = parsed_document.get('metadata', {})
            
            if not full_text:
                raise ValueError("No text content found in document")
            
            # Create content hash and document ID
            content_hash = self.create_content_hash(full_text)
            doc_id = self.create_document_id(filename, content_hash)
            
            # Check if document already exists
            existing = self.collection.get(ids=[doc_id])
            if existing['ids']:
                print(f"Document {filename} already exists in database")
                return {
                    'document_id': doc_id,
                    'status': 'already_exists',
                    'chunks_stored': 0
                }
            
            # Chunk the full text
            text_chunks = self.chunk_text(full_text)
            
            # Also chunk sections separately for better retrieval
            section_chunks = []
            for section_name, section_content in sections.items():
                if section_content.strip():
                    section_chunk_texts = self.chunk_text(section_content)
                    for i, chunk_text in enumerate(section_chunk_texts):
                        section_chunks.append({
                            'text': chunk_text,
                            'section': section_name,
                            'chunk_index': i,
                            'type': 'section'
                        })
            
            # Prepare data for ChromaDB
            all_chunks = []
            chunk_ids = []
            chunk_embeddings = []
            chunk_metadatas = []
            
            # Process full text chunks
            for i, chunk in enumerate(text_chunks):
                chunk_id = f"{doc_id}_full_{i}"
                embedding = self.generate_embedding(chunk)
                
                chunk_metadata = {
                    'document_id': doc_id,
                    'filename': filename,
                    'chunk_type': 'full_text',
                    'chunk_index': i,
                    'total_chunks': len(text_chunks),
                    'content_hash': content_hash,
                    **metadata  # Include document metadata
                }
                
                all_chunks.append(chunk)
                chunk_ids.append(chunk_id)
                chunk_embeddings.append(embedding)
                chunk_metadatas.append(chunk_metadata)
            
            # Process section chunks
            for i, section_info in enumerate(section_chunks):
                chunk_id = f"{doc_id}_section_{section_info['section']}_{i}"
                embedding = self.generate_embedding(section_info['text'])
                
                chunk_metadata = {
                    'document_id': doc_id,
                    'filename': filename,
                    'chunk_type': 'section',
                    'section_name': section_info['section'],
                    'chunk_index': section_info['chunk_index'],
                    'content_hash': content_hash,
                    **metadata
                }
                
                all_chunks.append(section_info['text'])
                chunk_ids.append(chunk_id)
                chunk_embeddings.append(embedding)
                chunk_metadatas.append(chunk_metadata)
            
            # Store in ChromaDB
            self.collection.add(
                ids=chunk_ids,
                embeddings=chunk_embeddings,
                documents=all_chunks,
                metadatas=chunk_metadatas
            )
            
            print(f"✅ Successfully stored {len(all_chunks)} chunks for document: {filename}")
            
            return {
                'document_id': doc_id,
                'status': 'success',
                'chunks_stored': len(all_chunks),
                'full_text_chunks': len(text_chunks),
                'section_chunks': len(section_chunks),
                'content_hash': content_hash
            }
            
        except Exception as e:
            print(f"❌ Error storing document embeddings: {e}")
            raise
    
    def search_similar_documents(self, query: str, n_results: int = 5, filter_metadata: Dict = None) -> Dict[str, Any]:
        """Search for similar documents using semantic similarity."""
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata
            )
            
            return {
                'query': query,
                'results': results,
                'total_found': len(results['documents'][0]) if results['documents'] else 0
            }
            
        except Exception as e:
            print(f"❌ Error searching documents: {e}")
            raise
    
    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Retrieve all chunks for a specific document."""
        try:
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            chunks = []
            if results['ids']:
                for i in range(len(results['ids'])):
                    chunks.append({
                        'id': results['ids'][i],
                        'text': results['documents'][i],
                        'metadata': results['metadatas'][i]
                    })
            
            return chunks
            
        except Exception as e:
            print(f"❌ Error retrieving document chunks: {e}")
            raise
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its chunks from ChromaDB."""
        try:
            # Get all chunks for this document
            chunks = self.get_document_chunks(document_id)
            
            if not chunks:
                print(f"No chunks found for document: {document_id}")
                return False
            
            # Delete all chunks
            chunk_ids = [chunk['id'] for chunk in chunks]
            self.collection.delete(ids=chunk_ids)
            
            print(f"✅ Deleted {len(chunk_ids)} chunks for document: {document_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting document: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the ChromaDB collection."""
        try:
            total_count = self.collection.count()
            
            # Get unique documents
            all_metadata = self.collection.get()['metadatas']
            unique_docs = set()
            doc_types = {}
            
            for metadata in all_metadata:
                if 'document_id' in metadata:
                    unique_docs.add(metadata['document_id'])
                if 'chunk_type' in metadata:
                    chunk_type = metadata['chunk_type']
                    doc_types[chunk_type] = doc_types.get(chunk_type, 0) + 1
            
            return {
                'total_chunks': total_count,
                'unique_documents': len(unique_docs),
                'chunk_types': doc_types,
                'collection_name': COLLECTION_NAME
            }
            
        except Exception as e:
            print(f"❌ Error getting collection stats: {e}")
            return {}


# Utility function to process and store a document
def process_and_store_document(parsed_document: Dict[str, Any], filename: str) -> Dict[str, Any]:
    """
    Convenience function to process and store a document.
    
    Args:
        parsed_document: Output from parse_document() function
        filename: Original filename
    
    Returns:
        Dictionary with storage results
    """
    embedding_service = EmbeddingService()
    return embedding_service.store_document_embeddings(parsed_document, filename)


# Utility function to search documents
def search_documents(query: str, n_results: int = 5) -> Dict[str, Any]:
    """
    Convenience function to search documents.
    
    Args:
        query: Search query text
        n_results: Number of results to return
    
    Returns:
        Search results
    """
    embedding_service = EmbeddingService()
    return embedding_service.search_similar_documents(query, n_results)
