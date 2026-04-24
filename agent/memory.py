# agent/memory.py
# Simplified Vector-backed Memory
# Uses ChromaDB directly for storing conversation history
# Semantic search retrieves relevant past context

import chromadb
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.schema import TextNode
from llama_index.vector_stores.chroma import ChromaVectorStore
import config


class ConversationMemory:
    """Simple vector-backed memory using ChromaDB directly."""
    
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path=config.CHROMA_PATH)
        self.collection = self.chroma_client.get_or_create_collection("conversation_memory")
        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
        self._initialized = False
    
    def initialize(self):
        from llama_index.llms.google_genai import GoogleGenAI
        from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
        
        if not config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not set")
        
        self.llm = GoogleGenAI(model=config.GEMINI_MODEL, api_key=config.GOOGLE_API_KEY)
        self.embed_model = GoogleGenAIEmbedding(model_name=config.EMBED_MODEL, api_key=config.GOOGLE_API_KEY)
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        self._initialized = True
        print("[memory] Initialized")
    
    def get_context(self, query: str) -> str:
        """
        Get relevant past conversation context for current query.
        Uses vector semantic search to find related messages.
        """
        if not self._initialized:
            return ""
        
        try:
            index = VectorStoreIndex.from_vector_store(self.vector_store)
            retriever = index.as_retriever(similarity_top_k=config.MEMORY_TOP_K)
            nodes = retriever.retrieve(query)
            
            if nodes:
                lines = []
                for node in nodes:
                    text = node.text[:200] if len(node.text) > 200 else node.text
                    lines.append(f"- {text}")
                return "\n".join(lines)
        except Exception as e:
            print(f"[memory] Error retrieving context: {e}")
        return ""
    
    def add_message(self, role: str, content: str):
        """
        Add a message to conversation history.
        Stores in ChromaDB for vector-based retrieval.
        """
        if not self._initialized:
            self.initialize()
        
        try:
            index = VectorStoreIndex.from_vector_store(self.vector_store)
            node = TextNode(
                text=f"{role}: {content}",
                metadata={"role": role}
            )
            index.insert(node)
        except Exception as e:
            print(f"[memory] Insert error: {e}")


# Global instance
_conversation_memory = None


def get_memory():
    """Get or create the global conversation memory instance."""
    global _conversation_memory
    if _conversation_memory is None:
        _conversation_memory = ConversationMemory()
    return _conversation_memory