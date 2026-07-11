from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
from langchain.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from config import llm
import sqlite3

config = {"configurable": {"thread_id": "1234"}}
conn = sqlite3.connect(database="rag.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def build_graph(retriever):

    @tool
    def rag_tool(query: str):
        """
        Retrieve relevant information from the pdf document. Use this tool when the user asks factual / conceptual questions that might be answered from the stored documents.
        """
        
        docs = retriever.invoke(query)
        return {
            "context": [d.page_content for d in docs],
            "query": query,
        }

    tools = [rag_tool]

    llm_with_tool = llm.bind_tools(tools)
    tool_node = ToolNode(tools)

    def chat_node(state: State):
        response = llm_with_tool.invoke(state["messages"])
        return {"messages": [response]}

    graph = StateGraph(State)

    graph.add_node("chat", chat_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chat")
    graph.add_conditional_edges("chat", tools_condition)
    graph.add_edge("tools", "chat")

    return graph.compile(checkpointer=checkpointer)