from langgraph.graph import StateGraph , START 
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import BaseMessage , HumanMessage , RemoveMessage
from langgraph.graph import MessagesState
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from config import llm

load_dotenv()

model = llm


class State(MessagesState):
    summary : str


def SummarizeNode(state : State):
    summary = state['summary']
    if summary:
        prompt = (
            f"Existing summary:\n{summary}\n\n"
            "Extend the summary using the new conversation above."
        )
    else:
        prompt=("Summarize the above conversation.")
        
    message_for_summary = state['messages'] + [HumanMessage(content=prompt)]
    response = model.invoke(message_for_summary)
    message_to_del = state['messages'][:-2]
    return{
        "summary" : response.content ,
        "messages" : [RemoveMessage(id=m.id) for m in message_to_del]
    }
    
    
def chatNode(state : State):
    message = []
    if state['summary']:
        message.append({
            "role" : "system",
            "content": f"Conversation summary:\n{state['summary']}"
        })
    message.extend(state['messages'])
    response = model.invoke(message)
    return {
       "messages" : [response]
    }
    
    
def condition_Node(state : State):
    return len(state['messages']) > 6 

graph = StateGraph(State)
graph.add_node("chat" , chatNode)
graph.add_node("summarize" , SummarizeNode)


graph.add_edge(START , "chat")
graph.add_conditional_edges("chat" , condition_Node , {True : "summarize" , False : "__end__"})
graph.add_edge("summarize" , "__end__")


checkpointer = InMemorySaver()
config = {"configurable" : {"thread_id" : "22"}}

chatbot = graph.compile(checkpointer=checkpointer)

def run(text : str):
    result = chatbot.invoke({"messages" : [HumanMessage(content=text)] , "summary" : ""} , config=config )
    return result


# gives the current version of the state
def show_state():
    snap = chatbot.get_state(config)
    vals = snap.values
    print("\n--- STATE ---")
    print("summary:", vals.get("summary", ""))
    print("num_messages:", len(vals.get("messages", [])))
    print("messages:")
    for m in vals.get("messages", []):
        print("-", type(m).__name__, ":", m.content[:300])
        

run("how the photsynthesis works")
show_state()
run('How is Albert Einstien related?')
show_state()
run('What are some of Einstien"s fampus work')
show_state()
run('Explain special theory of relativity')
show_state()