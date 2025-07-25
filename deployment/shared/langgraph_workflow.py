from typing import TypedDict, Annotated, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
import logging

logger = logging.getLogger(__name__)

# State definition
class MessagesState(TypedDict):
    """State for the agentic RAG workflow"""
    messages: Annotated[List[BaseMessage], add_messages]

class SimpleAgenticWorkflow:
    """Simplified agentic workflow that works with our fallback retriever"""
    
    def __init__(self, retriever_tool, model_name="llama3.1"):
        self.retriever_tool = retriever_tool
        
        # Initialize a simple chat model (or fallback to simple responses)
        try:
            self.chat_model = ChatOllama(
                model=model_name,
                temperature=0
            )
            self.use_llm = True
        except Exception as e:
            logger.warning(f"Could not initialize chat model: {e}")
            logger.info("Using simple response generation")
            self.use_llm = False
        
        # Build the workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build a simple workflow"""
        
        workflow = StateGraph(MessagesState)
        
        # Add nodes
        workflow.add_node("process_query", self._process_query)
        
        # Set entry point
        workflow.set_entry_point("process_query")
        workflow.add_edge("process_query", END)
        
        return workflow.compile()
    
    def _process_query(self, state: MessagesState) -> MessagesState:
        """Process the query and generate response"""
        try:
            messages = state["messages"]
            query = messages[-1].content if messages else ""
            
            logger.info(f"Processing query: {query}")
            
            # Use our retriever tool to get relevant documents
            if hasattr(self.retriever_tool, 'invoke'):
                # New format retriever tool
                try:
                    retrieved_docs = self.retriever_tool.invoke({"query": query})
                except:
                    retrieved_docs = self.retriever_tool.invoke(query)
            else:
                # Simple function call
                retrieved_docs = self.retriever_tool(query)
            
            logger.info(f"Retrieved documents: {len(str(retrieved_docs))} characters")
            
            # Generate response
            if self.use_llm:
                # Use LLM to generate response
                response = self._generate_llm_response(query, retrieved_docs)
            else:
                # Use simple template response
                response = self._generate_simple_response(query, retrieved_docs)
            
            return {"messages": [AIMessage(content=response)]}
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            error_response = f"I encountered an error while processing your query: {str(e)}"
            return {"messages": [AIMessage(content=error_response)]}
    
    def _generate_llm_response(self, query: str, retrieved_docs: str) -> str:
        """Generate response using LLM"""
        try:
            prompt = f"""Based on the following retrieved documents, answer the user's question.

Retrieved Documents:
{retrieved_docs}

User Question: {query}

Answer:"""
            
            response = self.chat_model.invoke([HumanMessage(content=prompt)])
            return response.content
            
        except Exception as e:
            logger.error(f"LLM response generation failed: {e}")
            return self._generate_simple_response(query, retrieved_docs)
    
    def _generate_simple_response(self, query: str, retrieved_docs: str) -> str:
        """Generate simple template response"""
        if not retrieved_docs or retrieved_docs == "No relevant documents found.":
            return f"I couldn't find specific information about '{query}' in the knowledge base. Please make sure relevant documents have been ingested first."
        
        # Simple template response
        response = f"Based on the available information, here's what I found regarding '{query}':\n\n"
        
        # Truncate retrieved docs if too long
        if len(retrieved_docs) > 1500:
            response += retrieved_docs[:1500] + "...\n\n"
        else:
            response += retrieved_docs + "\n\n"
        
        response += "This response is based on the documents in the knowledge base."
        
        return response
    
    def invoke(self, query: str) -> Dict[str, Any]:
        """Process query through the workflow"""
        try:
            logger.info(f"Starting workflow for query: {query}")
            
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=query)]
            }
            
            # Run the workflow
            final_state = self.workflow.invoke(initial_state)
            
            # Extract the final answer
            final_message = final_state["messages"][-1]
            answer = final_message.content if hasattr(final_message, 'content') else str(final_message)
            
            return {
                "answer": answer,
                "messages": [msg.content if hasattr(msg, 'content') else str(msg) 
                           for msg in final_state["messages"]],
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "answer": f"I encountered an error processing your request: {str(e)}",
                "messages": [],
                "status": "error",
                "error": str(e)
            }

def create_agentic_workflow(retriever_tool, model_name="llama3.1"):
    """Factory function to create the simplified workflow"""
    return SimpleAgenticWorkflow(retriever_tool, model_name)