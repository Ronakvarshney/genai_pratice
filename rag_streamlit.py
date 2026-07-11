import streamlit as st 

from rag_graph import build_graph , config
from rag_backend import create_retriever
from langchain_core.messages import HumanMessage
import os




with st.sidebar:
    st.title("Rag based Chatbot")
    
    file_input = st.file_uploader('upload a file')
    
if file_input:
    os.makedirs("upload", exist_ok=True)

    file_path = os.path.join("upload", file_input.name)

    with open(file_path, "wb") as f:
        f.write(file_input.getbuffer())

    retriever = create_retriever(file_path)

    st.success("Uploaded!")

        
    
if 'chats' not in st.session_state:
    st.session_state.chats = []   
    

for chat in st.session_state.chats:
    with st.chat_message(chat["role"]):
        st.write(chat["content"])
        
input_data = st.chat_input("Enter your thoughts to ask..")
if input_data:
    with st.chat_message('user'):
        st.write(input_data)
        st.session_state.chats.append({"role" : "user" , "content" : input_data})
    
    
    with st.chat_message('assistant'):
        
        chatbot = build_graph(retriever)
        
        response = chatbot.invoke({"messages" : HumanMessage(content=input_data) } , config=config)
        st.write(response['messages'][-1].content)
        st.session_state.chats.append({"role" : "assistant" , "content" : response['messages'][-1].content})
        
