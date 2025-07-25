import logging

logger = logging.getLogger(__name__)

class SimpleDB:
    """Very simple in-memory database for testing"""
    
    def __init__(self):
        self.data = []
        logger.info("Simple database initialized")
    
    def add_document(self, doc_id, content, source):
        """Add a document"""
        doc = {
            'id': doc_id,
            'content': content,
            'source': source
        }
        self.data.append(doc)
        logger.info(f"Added document: {doc_id}")
        return doc_id
    
    def search(self, query):
        """Improved keyword search with flexible matching"""
        results = []
        query_lower = query.lower()
    
        # Split query into words for better matching
        query_words = query_lower.split()
    
        for doc in self.data:
            content_lower = doc['content'].lower()
        
            # Check if any query word is in content
            found_words = 0
            for word in query_words:
                # Remove punctuation and check
                word_clean = word.strip('.,!?;:')
                if word_clean in content_lower:
                    found_words += 1
        
            # If we found at least half the words, include the document
            if found_words > 0 and found_words >= len(query_words) * 0.5:
                results.append(doc)
    
        logger.info(f"Found {len(results)} documents for query: {query}")
        return results
    
    def health_check(self):
        return True
    
    def get_stats(self):
        return {"total_documents": len(self.data)}

# Test if run directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    db = SimpleDB()
    db.add_document("doc1", "This is about machine learning and AI", "test.com")
    db.add_document("doc2", "Python programming is fun", "example.com")
    
    results = db.search("machine learning")
    print(f"Search results: {results}")