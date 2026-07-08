from langgraph.graph import StateGraph , START , END
from typing import TypedDict , Annotated 
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage , HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
import os

from dotenv import load_dotenv

load_dotenv()


class ChatHistory(TypedDict):
    chats : Annotated[list[BaseMessage] , add_messages]


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv('GROQ_API_KEY'),
    temperature=0.6
)

def chatNode(state : ChatHistory):
    messages = state['chats']
    for message in messages:
        print(message)
    response = llm.invoke(messages)
    for respone in response:
        print(respone)
    return {'chats' : [response]}
    

checkpointer = InMemorySaver()

graph = StateGraph(ChatHistory)
graph.add_node('chat_node' , chatNode)
graph.add_edge(START , 'chat_node')
graph.add_edge('chat_node' , END)

chatbot = graph.compile(checkpointer=checkpointer)

config = {'configurable' : {'thread_id' : '1'}}
while True:
    question = input('Enter your question')
    if question in['end' , 'exit']:
        break
    result = chatbot.invoke({'chats' : [HumanMessage(content=question)]} , config=config)
    print(result['chats'][-1].content)
    print(chatbot.get_state(config))
    
    





