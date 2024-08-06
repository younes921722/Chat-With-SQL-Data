
![Screenshot 2024-08-06 232116](https://github.com/user-attachments/assets/a88bedc8-2e79-44e7-95eb-ab630813cb1a)



# Streamlit MySQL Chatbot

This project is a Streamlit application that allows users to upload CSV files to a MySQL database and interact with the database using natural language queries. The application uses Langchain for handling SQL queries and OpenAI for processing and responding to user inputs.

## Features

- **Upload CSV Files**: Users can upload CSV files to a MySQL database. The application automatically creates or replaces tables based on the uploaded files.
- **Natural Language Queries**: Users can ask questions about the database using natural language. The application generates and executes corresponding SQL queries.
- **Streamlit Interface**: A user-friendly web interface built with Streamlit.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- MySQL database
- Environment variables set for database credentials

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/streamlit-mysql-chatbot.git
    cd streamlit-mysql-chatbot
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the project directory with your database credentials:
    ```plaintext
    USER=your_db_user
    PASSWORD=your_db_password
    HOST=your_db_host
    DATABASE=your_db_name
    ```

### Running the Application

1. Start the Streamlit application:
    ```bash
    streamlit run app.py
    ```

2. Open your web browser and go to `http://localhost:8501`.

### Uploading CSV Files

1. Use the "Upload Files" section to upload one or more CSV files.
2. The files will be uploaded to the connected MySQL database, creating or replacing tables as needed.

### Connecting to the Database

1. Fill in your database credentials in the sidebar under "Settings".
2. Click "Connect" to establish a connection to your MySQL database.
3. A success message will appear if the connection is successful.

### Interacting with the Chatbot

1. After connecting to the database, use the chat input at the bottom of the page to ask questions about your data.
2. The chatbot will process your question and return the relevant information from the database.

## Project Structure

- `app.py`: The main application file.
- `requirements.txt`: List of required Python packages.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.


## Contact

For questions or issues, please open an issue in this repository or contact [younes.saw2001@gmail.com].

