"""
Enhanced RAG MCP Server
Handles BOTH policies and announcements via vector search
No more hallucination!
"""

import asyncio
from typing import Dict, Any, List
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os






class RAGMCPServer:
    """MCP Server for querying documents using RAG (policies + announcements)."""
    
    def __init__(self, chroma_dir: str = "data/chroma_store"):
        print("🔄 Initializing Enhanced RAG Server...")
        
        self.chroma_dir = chroma_dir
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Load vector store
        if os.path.exists(chroma_dir):
            print("📦 Loading existing vector store from data/chroma_store")
            self.vectorstore = Chroma(
                persist_directory=chroma_dir,
                embedding_function=self.embeddings
            )
            print(f"✅ Enhanced RAG Server initialized successfully!")
        else:
            print(f"❌ Vector store not found at {chroma_dir}")
            print("   Run: python setup_vector_db.py")
            raise FileNotFoundError(f"Vector store not found. Run setup_vector_db.py first.")
    




    async def query_documents(
        self, 
        query: str, 
        top_k: int = 3,
        doc_type: str = None
    ) -> Dict[str, Any]:
        """
        Query all documents (policies + announcements) using semantic search.
        
        Args:
            query: Natural language question
            top_k: Number of results to return
            doc_type: Filter by type ('policy', 'announcement', or None for all)
        """
        try:
            # Build filter
            filter_dict = None
            if doc_type:
                filter_dict = {"type": doc_type}
            
            # Perform similarity search
            results = self.vectorstore.similarity_search(
                query,
                k=top_k,
                filter=filter_dict
            )
            
            if not results:
                return {
                    "success": False,
                    "message": "No relevant documents found",
                    "results": []
                }
            
            # Format results
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "type": doc.metadata.get("type", "unknown"),
                    "category": doc.metadata.get("category", "unknown")
                })
            
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "count": len(formatted_results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    




    async def query_policies(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Query ONLY policy documents."""
        return await self.query_documents(query, top_k, doc_type="policy")
    




    async def query_announcements(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Query ONLY announcements."""
        return await self.query_documents(query, top_k, doc_type="announcement")
    



    
    async def get_policy_summary(self, policy_name: str) -> Dict[str, Any]:
        """Get summary of a specific policy document."""
        try:
            # Search for the specific policy
            results = self.vectorstore.similarity_search(
                f"summary of {policy_name}",
                k=5,
                filter={"type": "policy"}
            )
            
            # Filter for exact policy match
            policy_chunks = [
                r for r in results 
                if policy_name.lower() in r.metadata.get("source", "").lower()
            ]
            
            if not policy_chunks:
                return {
                    "success": False,
                    "message": f"Policy '{policy_name}' not found",
                    "summary": None
                }
            
            # Combine chunks
            summary = "\n\n".join([chunk.page_content for chunk in policy_chunks[:3]])
            
            return {
                "success": True,
                "policy_name": policy_name,
                "summary": summary,
                "source": policy_chunks[0].metadata.get("source", "unknown")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "summary": None
            }












# For backward compatibility
class RAGServer(RAGMCPServer):
    """Alias for backward compatibility."""
    pass


async def test_rag_server():
    """Test the Enhanced RAG Server."""
    print("\n" + "="*60)
    print("🧪 Testing Enhanced RAG Server")
    print("="*60)
    
    server = RAGMCPServer()
    
    # Test queries
    test_cases = [
        ("What holidays are coming up?", "announcement"),
        ("What is the leave policy?", "policy"),
        ("Any team events?", "announcement"),
        ("sick leave", "policy")
    ]
    
    for query, expected_type in test_cases:
        print(f"\n{'='*60}")
        print(f"📝 Query: {query}")
        print(f"🎯 Expected type: {expected_type}")
        print("-"*60)
        
        result = await server.query_documents(query, top_k=2)
        
        if result["success"]:
            print(f"✅ Found {result['count']} results:")
            for i, res in enumerate(result["results"], 1):
                print(f"\n   Result {i}:")
                print(f"   Type: {res['type']}")
                print(f"   Source: {res['source']}")
                print(f"   Content: {res['content'][:100]}...")
        else:
            print(f"❌ Error: {result.get('error', result.get('message'))}")
    
    print("\n" + "="*60)
    print("✅ Testing complete!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_rag_server())