from langchain_core.messages import AIMessage, HumanMessage
import streamlit as st
from core import upload_csv_into_db, init_database, get_sql_chain, get_response
from core import user, password, host, port, database

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
    print("**************************",uploaded_files)
    if uploaded_files is not None and uploaded_files !=[]:
        st.success("The file uploaded successfully", icon="✅")
        # intializing our SQLDatabase
        db = init_database(
                    user=user,
                    password=password,
                    host=host,
                    port=port,
                    database=database
                )
        # save database in a session variable
        st.session_state.db = db
        # CSVs to our Mysql database
        upload_csv_into_db(uploaded_files=uploaded_files)
        st.success("The file transfered to the database successfully", icon="✅")
    


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
