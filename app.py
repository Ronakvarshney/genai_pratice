import streamlit as st 
from langchain_core.messages import HumanMessage , ToolMessage , SystemMessage
from graph import graph
import uuid
from dotenv import load_dotenv

load_dotenv()

st.title("Advanced chatbot with context memory")


def generate_threadId():
    thread = str(uuid.uuid4())
    return thread

    

if "threads_list" not in st.session_state:
    st.session_state.threads_list = []
    st.session_state.thread_id = generate_threadId()
    st.session_state.threads_list.append(st.session_state.thread_id)




st.session_state.messages = graph.get_state({"configurable" : {
    "thread_id" : st.session_state.thread_id
}}).values.get('messages' , [])



for message in st.session_state.messages:
    if message.type == "system":
        continue
    role = "assistant" if message.type == "ai" else "human"
    with st.chat_message(role):
        st.write(message.content)
        
prompt = st.chat_input("Enter your thoughts which you want to clarify")


if prompt:
    # st.session_state.messages.append({
    #     "role": "user",
    #     "content": prompt
    # })
    
    with st.chat_message('human'):
        st.write(prompt)
        

    with st.chat_message('assistant'):
        message = [SystemMessage(
        content="""
You are a helpful assistant.

When you receive a ToolMessage, use the tool result directly to answer the user.

Do not ignore tool outputs.
Do not tell the user to check another website if the tool has already provided the answer.
"""
    ),HumanMessage(content=prompt)]

        response = graph.invoke({"messages" : message}, config={
            "configurable" : {
                "thread_id" : st.session_state.thread_id
            }
        })
        st.session_state.messages = graph.get_state({"configurable" : {
            "thread_id" : st.session_state.thread_id
        }}).values.get('messages')
        # st.rerun()
        st.write(response["messages"][-1].content)

        # ai_msg = llm_with_tool.invoke(message)
        # if ai_msg.tool_calls:
        #     message.append(ai_msg)
        #     print("message" , message)

        #     for tool_call in ai_msg.tool_calls:
        #         selected_tool = {"get_weather": get_weather, "calculator": calculator}[tool_call["name"]]
        #         response = selected_tool.invoke(tool_call["args"])
        #         message.append(ToolMessage(content=str(response) , tool_call_id = tool_call["id"]))
        #         def stream_response():
        #           for chunk in llm_with_tool.stream(message):
        #             print("chunk", chunk)
        #             yield chunk.content
        #         response = st.write_stream(stream_response)
        #         print("response" , response)
        # else:
            # def stream_response():
            #     for chunk in llm.stream(message):
            #         if chunk.content:
            #             yield chunk.content

            # response = st.write_stream(stream_response)
                    
    # st.session_state.messages.append({"role": "assistant", "content": response})

        



with st.sidebar:
    st.header("Histories")
    for thread in st.session_state.threads_list:
        if st.button(thread):
            st.session_state.thread_id = thread
            st.rerun()
    
    if st.button('New Thread'):
        st.session_state.thread_id = generate_threadId()
        st.session_state.threads_list.append(st.session_state.thread_id)
        st.rerun()



# sqlite , checkpointer , resume chat feature 
