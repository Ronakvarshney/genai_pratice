from langgraph.graph import StateGraph , START ,END
from typing_extensions import TypedDict , Annotated
from langchain_groq import ChatGroq
from config import llm
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import BaseMessage , HumanMessage , AIMessage
from langgraph.graph.message import add_messages
import sqlite3
from langgraph.types import Command , interrupt



conn = sqlite3.connect(database="rag.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

class chatState(TypedDict):
    chats : Annotated[list[BaseMessage] , add_messages]
    


def chat_node(state : chatState):
    decision = interrupt({
        "type" : "check_first",
        "reason" : "Model is about to answer user question",
        "question" : state['chats'][-1].content,
        "insturction":"Approve this question? yes/no"
    })
    
    if decision['check_first'] == 'no':
        return{"chats" : [AIMessage(content="Not approved")]}
    else:
        return {"chats" : llm.invoke(state['chats'])}
    

graph = StateGraph(chatState)

graph.add_node('chat' , chat_node)
graph.add_edge(START , 'chat')
graph.add_edge('chat' , END)


chatbot = graph.compile(checkpointer=checkpointer)

config = {"configurable" : {"thread_id" : "123"}}

result = chatbot.invoke({"chats" : [HumanMessage(content="what is langchain")]} , config=config)

user_input = input(f"\nBackend message - {result} \n Approve this question? (y/n): ")

final_result = chatbot.invoke(Command(resume={"check_first" : user_input}) , config = config)
print(final_result)