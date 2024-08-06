from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine

load_dotenv()

user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
database = os.getenv("DATABASE")
# upload csv files into Mysql db
def upload_csv_into_db(uploaded_files):
    for file in uploaded_files:
        if file is not None:
            data_frame = pd.read_csv(file)

            # creating an engine
            engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")
            
            # upload the dataframe to MySql
            # this will create the table if it does not exist, or replace it if it does
            file_name = file.name.split(".")[0]
            data_frame.to_sql(name=f"uploaded_csv_{file_name}", con=engine, if_exists='replace',index=False)
            st.success("The file uploaded successfully", icon="✅")


# intializing the langchain Sql database
def init_database(user:str, password: str, host:str, port: str, database: str) -> SQLDatabase:
    db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    return SQLDatabase.from_uri(db_uri)

# returning sql chain
def get_sql_chain(db):
    # creating our template
    template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, write a MySQL query that would answer the user's question. Take the conversation history into account.
    
    <SCHEMA>{schema}</SCHEMA>
    
    Conversation History: {chat_history}
    
    Write only the MySQL query and nothing else. Do not wrap the MySQL query in any other text, not even backticks.
    
    
    For example:
    Question: which 3 artists have the most tracks?
    MySQL Query: SELECT ArtistId, COUNT(*) as track_count FROM Track GROUP BY ArtistId ORDER BY track_count DESC LIMIT 3;
    Question: Name 10 artists
    MySQL Query: SELECT Name FROM Artist LIMIT 10;
    
    Your turn:
    
    Question: {question}
    MySQL Query:
    """
    
    prompt = ChatPromptTemplate.from_template(template)

    # initializing the model
    llm = ChatGroq(model="Llama-3.1-70b-Versatile", temperature=0)

    def get_schema(_):
        return db.get_table_info()
  
    return (
        RunnablePassthrough.assign(schema=get_schema)
        | prompt
        | llm
        | StrOutputParser()
        )

# creating the full chain
def get_response(user_query: str, db:SQLDatabase, chat_history:list):
    sql_chain = get_sql_chain(db)

    template ="""
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, question, sql query, and sql response, write a detailed natural language response with additional information.
    Stay clear, kind and professional.
    Be aware in the case of multiple queries : you have to run each querie individually and then return the result.
    <SCHEMA>{schema}</SCHEMA>

    Conversation History: {chat_history}
    SQL Query: <SQL>{query}</SQL>
    User question: {question}
    Response: {response}"""
    
    prompt = ChatPromptTemplate.from_template(template=template)

    llm = ChatGroq(model="Llama-3.1-70b-Versatile", temperature=0.9)

    chain = (
    RunnablePassthrough.assign(query=sql_chain).assign(
      schema=lambda _: db.get_table_info(),
      response=lambda vars: db.run(vars["query"]),
        )
        | prompt
        | llm
        | StrOutputParser()
         )
  
    return chain.stream({
            "question": user_query,
            "chat_history": chat_history,
              })



# Saving chat history in streamlit session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content = "Hello! I am ai-sql assistant"),
    ]




st.set_page_config(page_title="Chat with MySQL", page_icon=":speech_balloon:" )
st.title("Chat with mysql")

with st.sidebar:

    # upload csv file
    st.subheader("Upload your csv")
    uploaded_files = st.file_uploader("",type="csv", accept_multiple_files=True)
    upload_csv_into_db(uploaded_files=uploaded_files)
# setting the Side bar
with st.sidebar:
        
    st.subheader("Setting")
    st.write("This is a sample app for chating with MySql. Connect to the databse and start chatting.")

    st.text_input("Host", value="localhost", key="Host")
    st.text_input("Port", value="3306", key="Port")
    st.text_input("User", value="root", key="User")
    st.text_input("Password", type="password",value="Younes921722", key="Password")
    st.text_input("Database", value="Chinook", key="Database")

    if st.button("Connect"):
        with st.spinner("connecting to db..."):
            db = init_database(
                st.session_state["User"],
                st.session_state["Password"],
                st.session_state["Host"],
                st.session_state["Port"],
                st.session_state["Database"]
            )
            st.session_state.db = db
            st.success("Connected successfully to the database:)")

# setting the Main chat page
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content )

user_input=st.chat_input("start asking!")
if user_input is not None and user_input.strip() !="":
    st.session_state.chat_history.append(HumanMessage(content=user_input))

    with st.chat_message("Human"):
        st.markdown(user_input)
    
    with st.chat_message("Ai"):
        sql_chain = get_sql_chain(st.session_state.db)
        # response = get_response(user_query=user_input, db=st.session_state.db, chat_history=st.session_state.chat_history)
        response = st.write_stream(get_response(user_query=user_input, db=st.session_state.db, chat_history=st.session_state.chat_history))
    
    st.session_state.chat_history.append(AIMessage(content=response))
