import sqlite3
from langgraph.graph import StateGraph , START , END 
from typing_extensions import TypedDict , Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode , tools_condition
from config import get_weather , calculator
import sqlite3
from config import llm_with_tool , llm
from dotenv import load_dotenv

load_dotenv()

conn = sqlite3.connect(database="chatbot.db" , check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

class Chat(TypedDict):
    messages : Annotated[list[BaseMessage] , add_messages]


def chatNode(state : Chat):
    return {"messages" : llm_with_tool.invoke(state['messages'])}
    


graph = StateGraph(Chat)
graph.add_node('chat_node' , chatNode)
graph.add_node('tools' , ToolNode([get_weather , calculator]))
graph.add_edge(START , 'chat_node')
graph.add_conditional_edges(
    "chat_node",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END,
    },
)
graph.add_edge('tools' , 'chat_node')
graph = graph.compile(checkpointer=checkpointer)
