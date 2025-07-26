import os
import sys
import time
from pathlib import Path
from typing import Literal

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import ibm_db_dbi
import logging
import traceback

# LangChain and LangGraph imports
from langchain_core.messages import convert_to_messages
from langchain.tools.retriever import create_retriever_tool
from langchain_ibm import ChatWatsonx
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

# Vector store imports
from langchain_community.embeddings import LlamaCppEmbeddings
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_db2.db2vs import DB2VS

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Agentic RAG Search API", version="1.0.0")

# Request/Response models
class SearchRequest(BaseModel):
    question: str
    table_name: str = "Documents_EUCLIDEAN"

class SearchResponse(BaseModel):
    answer: str
    success: bool
    sources_used: int = 0
    execution_path: list = []

# Global variables for caching
embeddings = None
llm = None

def get_db_connection():
    """Establish database connection"""
    conn_str = f"DATABASE={os.getenv('DB_NAME')};hostname={os.getenv('DB_HOST')};port={os.getenv('DB_PORT')};protocol={os.getenv('DB_PROTOCOL')};uid={os.getenv('DB_USER')};pwd={os.getenv('DB_PASSWORD')}"
    
    try:
        return ibm_db_dbi.connect(conn_str, '', '')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

def get_embeddings():
    """Initialize LlamaCpp embeddings (cached)"""
    global embeddings
    
    if embeddings is None:
        try:
            model_paths = [
                Path(__file__).parent.parent / "granite-embedding-30m-english-Q6_K.gguf",
                Path(__file__).parent / "granite-embedding-30m-english-Q6_K.gguf"
            ]
            
            model_path = None
            for path in model_paths:
                if path.exists():
                    model_path = str(path)
                    break
            
            if not model_path:
                raise FileNotFoundError("Embedding model file not found")
                
            embeddings = LlamaCppEmbeddings(model_path=model_path)
            logger.info("Embeddings initialized successfully")
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize embeddings: {str(e)}")
    
    return embeddings

def get_llm():
    """Initialize Watsonx LLM (cached)"""
    global llm
    
    if llm is None:
        try:
            llm = ChatWatsonx(
                url="https://us-south.ml.cloud.ibm.com",
                apikey=os.getenv("WATSONX_APIKEY", ""),
                model_id="mistralai/mistral-large",
                project_id=os.getenv("WATSONX_PROJECT", ""),
                params={"temperature": 0}
            )
            logger.info("Watsonx LLM initialized successfully")
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize LLM: {str(e)}")
    
    return llm

def table_exists(connection, table_name: str) -> bool:
    """Check if table exists"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM SYSCAT.TABLES 
            WHERE TABNAME = ? AND TABSCHEMA = CURRENT SCHEMA
        """, (table_name.upper(),))
        result = cursor.fetchone()
        cursor.close()
        return result[0] > 0
    except Exception:
        return False

def create_retriever(table_name: str):
    """Create retriever from vector store"""
    connection = get_db_connection()
    
    if not table_exists(connection, table_name):
        connection.close()
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    
    embeddings_model = get_embeddings()
    
    # Use the exact same pattern as in from_texts method
    vectorstore = DB2VS(
        embeddings=embeddings_model,
        client=connection, 
        table_name=table_name,
        distance_strategy=DistanceStrategy.EUCLIDEAN_DISTANCE
    )
    
    retriever = vectorstore.as_retriever()
    
    retriever_tool = create_retriever_tool(
        retriever,
        "retrieve_documents",
        f"Search and return information from the {table_name} document collection.",
    )
    
    return retriever_tool, connection

# Grade documents model (from your notebook)
class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""
    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )

# Graph functions (from your notebook)
def generate_query_or_respond(state: MessagesState, retriever_tool):
    """Call the Watsonx model to generate a response based on the current state."""
    llm = get_llm()
    response = (
        llm
        .bind_tools([retriever_tool])
        .invoke(state["messages"])
    )
    return {"messages": [response]}

def grade_documents(state: MessagesState) -> Literal["generate_answer", "rewrite_question"]:
    """Determine whether the retrieved documents are relevant to the question."""
    GRADE_PROMPT = (
        "You are a grader assessing relevance of a retrieved document to a user question. \n "
        "Here is the retrieved document: \n\n {context} \n\n"
        "Here is the user question: {question} \n"
        "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n"
        "Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."
    )
    
    question = state["messages"][0].content
    context = state["messages"][-1].content

    prompt = GRADE_PROMPT.format(question=question, context=context)
    llm = get_llm()
    response = (
        llm
        .with_structured_output(GradeDocuments).invoke(
            [{"role": "user", "content": prompt}]
        )
    )
    score = response.binary_score

    if score == "yes":
        return "generate_answer"
    else:
        return "rewrite_question"

def rewrite_question(state: MessagesState):
    """Rewrite the original user question using Watsonx."""
    REWRITE_PROMPT = (
        "Look at the input and try to reason about the underlying semantic intent / meaning.\n"
        "Here is the initial question:"
        "\n ------- \n"
        "{question}"
        "\n ------- \n"
        "Formulate an improved question:"
    )
    
    messages = state["messages"]
    question = messages[0].content
    prompt = REWRITE_PROMPT.format(question=question)

    llm = get_llm()
    response = llm.invoke([
        {"role": "user", "content": prompt}
    ])

    return {"messages": [{"role": "user", "content": response.content}]}

def generate_answer(state: MessagesState):
    """Generate an answer."""
    GENERATE_PROMPT = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, just say that you don't know. "
        "Use three sentences maximum and keep the answer concise.\n"
        "Question: {question} \n"
        "Context: {context}"
    )
    
    question = state["messages"][0].content
    context = state["messages"][-1].content
    prompt = GENERATE_PROMPT.format(question=question, context=context)
    
    llm = get_llm()
    response = llm.invoke([{"role": "user", "content": prompt}])
    return {"messages": [response]}

def create_graph(retriever_tool):
    """Create the LangGraph workflow (from your notebook)"""
    workflow = StateGraph(MessagesState)

    # Define the nodes
    workflow.add_node("generate_query_or_respond", lambda state: generate_query_or_respond(state, retriever_tool))
    workflow.add_node("retrieve", ToolNode([retriever_tool]))
    workflow.add_node("rewrite_question", rewrite_question)
    workflow.add_node("generate_answer", generate_answer)

    workflow.add_edge(START, "generate_query_or_respond")

    # Decide whether to retrieve
    workflow.add_conditional_edges(
        "generate_query_or_respond",
        tools_condition,
        {
            "tools": "retrieve",
            END: END,
        },
    )

    # Edges taken after the `action` node is called
    workflow.add_conditional_edges(
        "retrieve",
        grade_documents,
    )
    workflow.add_edge("generate_answer", END)
    workflow.add_edge("rewrite_question", "generate_query_or_respond")

    # Compile
    return workflow.compile()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Initializing agentic RAG search API...")
    get_embeddings()
    get_llm()
    logger.info("Agentic RAG search API ready!")

@app.post("/search", response_model=SearchResponse)
async def search_and_answer(request: SearchRequest):
    """Search the vector store and generate an answer using agentic RAG"""
    try:
        logger.info(f"Processing agentic RAG query: '{request.question}' in table '{request.table_name}'")
        
        # Create retriever and graph for this request
        retriever_tool, connection = create_retriever(request.table_name)
        graph = create_graph(retriever_tool)
        
        # Track execution path
        execution_path = []
        sources_used = 0
        
        # Run the graph
        final_state = None
        for chunk in graph.stream({
            "messages": [
                {
                    "role": "user",
                    "content": request.question,
                }
            ]
        }):
            final_state = chunk
            # Track which nodes were executed
            for node_name in chunk.keys():
                execution_path.append(node_name)
                if node_name == "retrieve":
                    sources_used += 1
        
        # Close database connection
        connection.close()
        
        # Extract the final answer
        answer = "I couldn't generate an answer to your question."
        success = False
        
        if final_state:
            for node, update in final_state.items():
                if "messages" in update and update["messages"]:
                    last_message = update["messages"][-1]
                    if hasattr(last_message, 'content'):
                        answer = last_message.content
                        success = True
                    else:
                        answer = str(last_message)
                        success = True
                    break
        
        logger.info(f"Agentic RAG completed. Success: {success}, Execution path: {execution_path}")
        
        return SearchResponse(
            answer=answer,
            success=success,
            sources_used=sources_used,
            execution_path=execution_path
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agentic RAG search failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/search/tables")
async def list_tables():
    """List available vector tables"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT DISTINCT TABNAME 
            FROM SYSCAT.COLUMNS 
            WHERE TABSCHEMA = CURRENT SCHEMA 
            AND COLNAME LIKE '%EMBEDDING%'
            ORDER BY TABNAME
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        
        return {
            "success": True,
            "tables": tables,
            "count": len(tables)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tables: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "Agentic RAG Search API",
        "embeddings_loaded": embeddings is not None,
        "llm_loaded": llm is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)