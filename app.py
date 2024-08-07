from langchain_core.messages import AIMessage, HumanMessage
import streamlit as st
from core import upload_csv_into_db, init_database, get_sql_chain, get_response
from core import user, password, host, port, database
import time

# Function to simulate streaming a string
def stream_string(text, delay=0.02):
    placeholder = st.empty()
    stream_text = ""
    for char in text:
        stream_text += char
        placeholder.text(stream_text)
        time.sleep(delay)

# Saving chat history in streamlit session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content = "Hello! I am an ai Csv/Sql assistant"),
    ]

st.set_page_config(page_title="Chat with CSV data", page_icon=":speech_balloon:" )
st.title("Chat with your CSV")

with st.sidebar:

    # upload csv file
    st.subheader("Upload your csv")
    uploaded_files = st.file_uploader("",type="csv", accept_multiple_files=True)

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
        try:
            db = st.session_state.db
            sql_chain = get_sql_chain(db)
            # response = get_response(user_query=user_input, db=st.session_state.db, chat_history=st.session_state.chat_history)
            response = st.write_stream(get_response(user_query=user_input, db=st.session_state.db, chat_history=st.session_state.chat_history))
            if response is not None and response!="":
                st.session_state.chat_history.append(AIMessage(content=response))
        except:
            stream_string("please try to upload your csv files first!")
