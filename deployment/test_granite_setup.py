#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.granite_db2_store import get_granite_db2_store
from shared.langgraph_workflow import AgenticRAGWorkflow

def test_complete_setup():
    """Test your complete notebook setup"""
    try:
        print("🔍 Testing Granite + DB2 setup...")
        
        # Test granite DB2 store
        store = get_granite_db2_store()
        
        if not store.health_check():
            print("❌ Store health check failed")
            return False
        
        print("✅ Granite embeddings + DB2 connection healthy")
        
        # Test document ingestion
        test_docs = [{
            'id': 'blog_post_1',
            'content': 'This is a blog post about machine learning, deep learning, and artificial intelligence. It covers various topics including neural networks, natural language processing, and computer vision.',
            'source': 'https://shaikh.blog/ml-post-1',
            'title': 'Introduction to Machine Learning',
            'metadata': {'author': 'Shaikh', 'category': 'ML'}
        }]
        
        print("📝 Testing document ingestion with Granite embeddings...")
        doc_ids = store.add_documents(test_docs)
        print(f"✅ Added documents: {len(doc_ids)} chunks created")
        
        # Test retriever tool
        retriever_tool = store.get_retriever_tool()
        if retriever_tool:
            print("✅ Retriever tool created successfully")
        
        # Test LangGraph workflow
        print("🤖 Testing LangGraph agentic workflow...")
        workflow = AgenticRAGWorkflow(retriever_tool)
        
        # Test query
        result = workflow.invoke("What does Shaikh's blog say about machine learning?")
        print(f"✅ Workflow result: {result['status']}")
        print(f"📄 Answer preview: {result['answer'][:100]}...")
        
        # Show stats
        stats = store.get_stats()
        print(f"📊 System stats: {stats}")
        
        print("🎉 Complete setup test passed! Your notebook setup is working in production.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_complete_setup()