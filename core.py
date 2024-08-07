from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import pandas as pd
import os
from sqlalchemy import create_engine

# loading the envirement variables
load_dotenv()
user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
port = os.getenv("PORT")
database = os.getenv("DATABASE")

# upload csv files into Mysql db
def upload_csv_into_db(uploaded_files):
    for file in uploaded_files:
        if file is not None:
            data_frame = pd.read_csv(file)

            # creating an engine
            db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"

            # using a context manager to ensure the engine is closed
            with create_engine(db_uri).connect() as conn:
                # uploading the dataframe to MySql
                # this will create the table if it does not exist, or replace it if it does
                file_name = file.name.split(".")[0]
                data_frame.to_sql(name=f"uploaded_csv_{file_name}", con=conn, if_exists='replace',index=False)


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
    
    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

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
    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
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
