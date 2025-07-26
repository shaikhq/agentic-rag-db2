# deployment/shared/granite_db2_store.py

from __future__ import annotations  # <-- Must be the very first line

import logging
import os
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from langchain_community.embeddings import LlamaCppEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Forward reference hinting
if TYPE_CHECKING:
    from .granite_db2_store import GraniteDB2Store

# Try to import DistanceStrategy, fallback if not available
try:
    from langchain_db2.db2vs import DistanceStrategy
except ImportError:
    try:
        from langchain_db2 import DistanceStrategy
    except ImportError:
        logger = logging.getLogger(__name__)
        logger.warning("DistanceStrategy not found, will use default")
        DistanceStrategy = None

# Try different imports for create_retriever_tool
try:
    from langchain_community.tools import create_retriever_tool
except ImportError:
    try:
        from langchain.tools.retriever import create_retriever_tool
    except ImportError:
        try:
            from langchain_core.tools import create_retriever_tool
        except ImportError:
            def create_retriever_tool(retriever, name, description):
                def retriever_tool_func(query: str):
                    try:
                        docs = retriever.get_relevant_documents(query)
                        return "\n\n".join([doc.page_content for doc in docs])
                    except Exception as e:
                        return f"Error retrieving documents: {str(e)}"

                class SimpleRetrieverTool:
                    def __init__(self, func, name, description):
                        self.func = func
                        self.name = name
                        self.description = description
                    
                    def invoke(self, args):
                        query = args.get('query', '') if isinstance(args, dict) else str(args)
                        return self.func(query)
                    
                    def __call__(self, query):
                        return self.func(query)

                return SimpleRetrieverTool(retriever_tool_func, name, description)

try:
    import ibm_db
    import ibm_db_dbi
    DB2_AVAILABLE = True
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("IBM DB2 drivers not available - using fallback mode")
    DB2_AVAILABLE = False
    ibm_db = None
    ibm_db_dbi = None

from .config import config

logger = logging.getLogger(__name__)

class GraniteDB2Store:
    def __init__(self):
        self.embeddings = LlamaCppEmbeddings(model_path=config.GRANITE_MODEL_PATH)
        logger.info("✅ Granite embeddings model loaded successfully")

        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
        self.connection = None
        self.dbi_connection = None
        self.vectorstore = None
        self.retriever = None
        self.retriever_tool = None
        self.db2_available = False
        self.simple_storage = []

        self._initialize_connection()

    def _initialize_connection(self):
        if not DB2_AVAILABLE:
            logger.warning("⚠️  DB2 drivers not available - using simple storage")
            return

        try:
            conn_str = config.get_db2_connection_string()
            logger.info(f"Attempting DB2 connection to {config.DB2_HOST}:{config.DB2_PORT}")
            self.connection = ibm_db.connect(conn_str, "", "")
            self.dbi_connection = ibm_db_dbi.connect(conn_str, "", "")  # ✅ correct usage
            logger.info("✅ DB2 DBI connection established")
            self.db2_available = True
        except Exception as e:
            logger.warning(f"⚠️  DB2 connection failed: {e}")
            self.connection = None
            self.dbi_connection = None

    # rest of your class definition continues unchanged...
    # all existing methods (add_documents, get_retriever_tool, etc.) remain as you posted them

# Singleton pattern
_granite_store = None

def get_granite_db2_store() -> GraniteDB2Store:
    global _granite_store
    if _granite_store is None:
        _granite_store = GraniteDB2Store()
    return _granite_store
