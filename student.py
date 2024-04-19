import streamlit as st
import pandas as pd
import re
import ast
import networkx as nx
import matplotlib.pyplot as plt
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid
import os

# Set the environment variable for the Google Cloud service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\HP\Desktop\streamlitFolder\datakeyfile.json"

# Import Firestore client from firebase_admin
from firebase_admin import firestore

# Initialize Firestore client
db = firestore.client()
# Path to your service account key file
path_to_keyfile = r'C:\Users\HP\Desktop\streamlitFolder\datakeyfile.json'



if not firebase_admin._apps:
    cred = credentials.Certificate(path_to_keyfile)
    firebase_admin.initialize_app(cred, {
        "databaseURL": " https://chaimadatare-default-rtdb.europe-west1.firebasedatabase.app/"
    })

db = firestore.client()
dataset = pd.read_csv('dataset.csv')
relation = pd.read_csv('relationships.csv')
# Register users in Firebase
def register_user(email, full_name, role, interests, password):
    user_ref = db.collection('users').document(email)
    user_ref.set({
        'full_name': full_name,
        'role': role,
        'interests': interests,
        'password': password  # Adding password field
    })


# Register chaima@gmail.com


# First Time Code
def first_time(session_state):
    # Create columns for layout control
    col1, col2 = st.columns([1, 3])
    # Display image in the first column
    with col1:
        st.image("black.svg.svg", width=200)
    # Display paragraph text in the second column
    with col2:
        # Adjust vertical alignment
        st.markdown("""
        <div style="display: flex; align-items: center; height: 200px;">
            <p style="margin-left: 20px;">Empowering education and research with ease, accuracy, and enjoyment. Explore, learn, and innovate with confidence.</p>
            
        </div>
        """, unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    with col1:
     search_query = st.text_input("Start your research journey")
    with col2:
     search_button = st.button("Search")
        
    # Display search results when the button is clicked
    if search_button:
        # Perform search and display results
        st.write("Search results for:", search_query)
        # Notification-like pop-up message
        notification_container = st.empty()
        notification_container.info("If you want a better experience in your research journey, try joining our family and log in!")
        # You can add your search logic here
        search_results = dataset[
            (dataset['title'].str.contains(search_query, case=False)) |
            (dataset['abstract'].str.contains(search_query, case=False)) |
            (dataset['topic'].str.contains(search_query, case=False)) |
            (dataset['keywords'].str.contains(search_query, case=False))
        ][:5]  # Limit to 10 results
        for index, row in search_results.iterrows():
            # Display title
            st.markdown(f"**{row['title']}**")
            # Display abstract (3 lines initially)
            abstract_lines = row['abstract'].split('\n')
            abstract_preview = '\n'.join(abstract_lines[:3])
            st.write(abstract_preview)
            if len(abstract_lines) > 3:
                if st.button("Read more"):
                    st.write('\n'.join(abstract_lines))
            # Display keywords
            st.markdown(f"**Keywords:** {row['keywords']}")
    
    # About Us section
    st.write("""
        <div style="padding: 20px;">
            <h1>About Us</h1>
            <div style="background-color: #f2f2f2; padding: 20px;">
                <p>Welcome to Algeria Intellect, the premier platform crafted by students of the Master's program in Intelligent Systems and Informatics Engineering (ISII) from  Ben Youcef Benkhedda's University . Our innovative system empowers both students and researchers alike, offering a delightful blend of professionalism and fun in navigating the vast sea of scientific articles. Whether you prefer the thrill of searching for specific topics or the serendipitous joy of exploring our meticulously curated recommendation articles, Algeria Intellect ensures a seamless journey through the realm of scholarly knowledge. Join us on this exhilarating quest for intellectual enlightenment!</p>
                <h3>Contact</h3>
                <a href="mailto:AlgeriaIntellect@gmail.com">📧 AlgeriaIntellect@gmail.com</a>
            </div>
           
        </div>
    """, unsafe_allow_html=True)
    
    # Log In and Create Account buttons in the same line
    
    
    row = st.columns([1, 1])

# Place the buttons within the row
    with row[0]:
     if st.button("Log In"):
        session_state['page'] = 'login'
    with row[1]:
     if st.button("Create Account"):
        session_state['page'] = 'newUser'

def login(session_state):
    # Create columns for layout control
    col1, col2 = st.columns([1, 3])
    # Display image in the first column
    with col2:
        st.image("black.svg.svg", width=300)
    if st.button("←"):
        session_state['page'] = 'first_time'
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # Retrieve user document from Firestore
        user_ref = db.collection('users').document(email)
        user_data = user_ref.get()
        
        # Check if user exists
        if user_data.exists:
            # Get user's stored password
            stored_password = user_data.get('password')

            # Check if provided password matches stored password
            if password == stored_password:
                # Passwords match, proceed with login
                session_state['logged_in'] = True
                session_state['email'] = email
                session_state['full_name'] = user_data.get('full_name')
                session_state['role'] = user_data.get('role')
                session_state['interests'] = user_data.get('interests')
                
                # Redirect user based on role
                if session_state['role'] == 'Student':
                    session_state['page'] = 'recommendation'
                else:
                    session_state['page'] = 'research'
            else:
                # Passwords don't match, display error message
                st.error("Incorrect password. Please try again.")
        else:
            # User not found, display error message
            st.error("User not found. Please check your email.")

 

def newUser(session_state):
    # Create columns for layout control
    col1, col2 = st.columns([1, 3])
    # Display image in the first column
    with col2:
        st.image("black.svg.svg", width=300)
    if st.button("←"):
        session_state['page'] = 'first_time'
    st.title("Create Account")
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Choose your role", ["Student", "Researcher"])
    st.write("Interests or Specialist Centers")
    options = ["Cell Biology", "Virology", "Chemistry", "Environmental Studies", "Physics", "Human Health Studies", "Technology and Computer Science", "Agricultural Studies", "Cancer Study", "Geology and Earth  Studies","Biotechnology","General Medicine","Astronomy","Psychology","Phisiology","Education","Pharmacy","Mathematics"]
    selected_options = st.multiselect("Select your interests", options)
    
    if st.button("Create Account"):
        # Validate email syntax
        email_valid = bool(re.match(r'^[\w\.-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email))
        
        # Validate inputs
        if full_name.strip() == "":
            st.error("Please enter your full name.")
        elif not email_valid:
            st.error("Please enter a valid email address.")
        elif len(selected_options) < 2:
            st.error("Please select at least 2 interest options.")
        else:
            # Check if email already exists in the database
            if email_exists(email):
                st.error("Email already exists. Please choose another email.")
            else:
                # Generate a unique user ID
                user_id = str(uuid.uuid4())
                
                # Add new user to the database
                register_user(email, full_name, role, selected_options, password)
                
                # Update session state
                session_state['logged_in'] = True
                session_state['email'] = email
                session_state['full_name'] = full_name
                session_state['role'] = role
                session_state['interests'] = selected_options
                
                # Redirect user based on role
                if role == 'Student':
                    session_state['page'] = 'recommendation'
                else:
                    session_state['page'] = 'research'

def email_exists(email):
    # Query the database to check if the email exists
    # Assuming you have a 'users' collection in your Firestore database
    user_ref = db.collection('users').where('email', '==', email).get()
    
    # If any documents are returned, it means the email exists
    if user_ref:
        return True
    else:
        return False

def display_recommended_papers(session_state, full_name):
    # Calculate recommendations
    email = session_state.get('email')
    if email is None:
        st.write("Email not found in session_state. Please log in again.")
        return

    # Check if the email exists in the database
    user_ref = db.collection('users').document(email)
    user_data = user_ref.get()
    if not user_data.exists:
        st.write("User not found. Please log in again.")
        return

    # Get user info and interests from the database
    user_info = user_data.to_dict()
    selected_interests = user_info.get('interests', [])

    # Your recommendation calculation logic goes here
    basic_data = dataset[dataset['topic'].isin(selected_interests)]
    pass_number = 100 // len(selected_interests)
    second_data = pd.DataFrame()
    for category in selected_interests:
        category_data = basic_data[basic_data['topic'] == category]
        category_data = category_data.sort_values(by=['pub_year', 'semantic_score'], ascending=[False, False])
        category_data = category_data.head(pass_number)
        second_data = pd.concat([second_data, category_data])
    if len(second_data) < 100:
        extra_data = basic_data[~basic_data['id'].isin(second_data['id'])]
        extra_data = extra_data.sample(n=100-len(second_data))
        second_data = pd.concat([second_data, extra_data])

    # Display UI elements for recommendations
    col1, col2 = st.columns([1, 3])
    # Display image in the first column
    with col1:
        st.image("only.svg", width=150)
    # Display paragraph text in the second column
    with col2:
        st.markdown("""
        <div style="display: flex; align-items: center; height: 200px;">
            <h3 style="margin-left: -20px;">AlgeriaIntellect</h3>
        </div>
        """, unsafe_allow_html=True)
    st.sidebar.title("AlgeriaIntellect")
    st.sidebar.write(f"Hello {full_name}, welcome to AlgeriaIntellect platform!")
    st.sidebar.write("This platform is a recommendation system for scientific papers. It aims to help you educate yourself in a fun and easy way.")
    st.sidebar.write("---")
    st.sidebar.write("check your profile")
    if st.sidebar.button("Profile Info"):
        session_state['page'] = 'profile_info'
    st.sidebar.write("---")
    st.sidebar.write("Contact Us")
    st.sidebar.markdown('<a href="mailto:AlgeriaIntellect@gmail.com">📧 AlgeriaIntellect@gmail.com</a>', unsafe_allow_html=True)
    st.sidebar.write("---")
    st.sidebar.write("Developed  by master's students from the esteemed University of Ben Youcef Benkhedda.")
    if st.sidebar.button("Log Out"):
        session_state['page'] = 'first_time'  # Set page to first time
        session_state['logged_in'] = False     # Reset login status
    search_query = st.text_input("Enter subject or keyword", "")
    if st.button("Search"):
        session_state['search_query'] = search_query
        session_state['page'] = 'search_recommendation'
    st.title("Articles recommended for you:")
    # Add a button to visualize the results as a graph
    if st.button("Visualize as Graph"):
        session_state['page'] = 'graph'

    # Retrieve recommendations from session state
    recommendations = second_data

    # Display recommendations
    page_number = session_state.get('current_page', 1)
    start_index = (page_number - 1) * 20
    end_index = min(start_index + 20, len(recommendations))
    for idx in range(start_index, end_index):
        paper = recommendations.iloc[idx]
        if st.button(f"{paper['title']}", key=f"paper_button_{idx}"):
            session_state['selected_paper'] = paper
            session_state['page'] = 'review_student'
        st.write("**Abstract:** ", paper["abstract"])
        st.markdown(f"**Keywords:** {paper['keywords']}")
        st.write("---")

    # Pagination logic
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if page_number != 1:
            if st.button("1"):
                session_state['current_page'] = 1
    with col2:
        if page_number != 2:
            if st.button("2"):
                session_state['current_page'] = 2
    with col3:
        if page_number != 3:
            if st.button("3"):
                session_state['current_page'] = 3
    with col4:
        if page_number != 4:
            if st.button("4"):
                session_state['current_page'] = 4
    with col5:
        if page_number != 5:
            if st.button("5"):
                session_state['current_page'] = 5

def researcher_page(session_state, full_name):
    # Calculate recommendations
    email = session_state.get('email')
    if email is None:
        st.write("Email not found in session_state. Please log in again.")
        return

    # Check if the email exists in the database
    user_ref = db.collection('users').document(email)
    user_data = user_ref.get()
    if not user_data.exists:
        st.write("User not found. Please log in again.")
        return

    # Get user info and interests from the database
    user_info = user_data.to_dict()
    selected_interests = user_info.get('interests', [])

    # Your recommendation calculation logic goes here
    basic_data = dataset[dataset['topic'].isin(selected_interests)]
    pass_number = 100 // len(selected_interests)
    second_data = pd.DataFrame()
    for category in selected_interests:
        category_data = basic_data[basic_data['topic'] == category]
        category_data = category_data.sort_values(by=['pub_year', 'semantic_score'], ascending=[False, False])
        category_data = category_data.head(pass_number)
        second_data = pd.concat([second_data, category_data])
    if len(second_data) < 100:
        extra_data = basic_data[~basic_data['id'].isin(second_data['id'])]
        extra_data = extra_data.sample(n=100-len(second_data))
        second_data = pd.concat([second_data, extra_data])

    # Display UI elements for recommendations
    col1, col2 = st.columns([1, 3])
    # Display image in the first column
    with col1:
        st.image("only.svg", width=150)
    # Display paragraph text in the second column
    with col2:
        st.markdown("""
        <div style="display: flex; align-items: center; height: 200px;">
            <h3 style="margin-left: -20px;">AlgeriaIntellect</h3>
        </div>
        """, unsafe_allow_html=True)
    st.sidebar.title("AlgeriaIntellect")
    st.sidebar.write(f"Hello {full_name}, welcome to AlgeriaIntellect platform!")
    st.sidebar.write("This platform is a recommendation system for scientific papers. It aims to help you educate yourself in a fun and easy way.")
    st.sidebar.write("---")
    st.sidebar.write("check your profile")
    if st.sidebar.button("Profile Info"):
        session_state['page'] = 'profile_info'
    st.sidebar.write("---")
    st.sidebar.write("Contact Us")
    st.sidebar.markdown('<a href="mailto:AlgeriaIntellect@gmail.com">📧 AlgeriaIntellect@gmail.com</a>', unsafe_allow_html=True)
    st.sidebar.write("---")
    st.sidebar.write("Developed by master's students from the esteemed University of Ben Youcef Benkhedda.")
    if st.sidebar.button("Log Out"):
        session_state['page'] = 'first_time'  # Set page to first time
        session_state['logged_in'] = False     # Reset login status
    search_query = st.text_input("Enter subject or keyword", "")
    if st.button("Search"):
        session_state['search_query'] = search_query
        session_state['page'] = 'search_recommendation'
    st.title("Articles recommended for you:")
    # Add a button to visualize the results as a graph
    if st.button("Visualize as Graph"):
        session_state['page'] = 'graph'

    # Retrieve recommendations from session state
    recommendations = second_data

    # Display recommendations
    page_number = session_state.get('current_page', 1)
    start_index = (page_number - 1) * 20
    end_index = min(start_index + 20, len(recommendations))
    for idx in range(start_index, end_index):
        paper = recommendations.iloc[idx]
        if st.button(f"{paper['title']}", key=f"paper_button_{idx}"):
            session_state['selected_paper'] = paper
            session_state['page'] = 'review_student'
        st.write("**Abstract:** ", paper["abstract"])
        st.markdown(f"**Keywords:** {paper['keywords']}")
        st.write("---")

    # Pagination logic
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if page_number != 1:
            if st.button("1"):
                session_state['current_page'] = 1
    with col2:
        if page_number != 2:
            if st.button("2"):
                session_state['current_page'] = 2
    with col3:
        if page_number != 3:
            if st.button("3"):
                session_state['current_page'] = 3
    with col4:
        if page_number != 4:
            if st.button("4"):
                session_state['current_page'] = 4
    with col5:
        if page_number != 5:
            if st.button("5"):
                session_state['current_page'] = 5
def display_profile_info(session_state):
    if st.button("← Back "):
        session_state['page'] = 'recommendation'
    st.title("Your Profile")
    st.markdown("---")
    email = session_state.get('email')
    if email is None:
        st.write("Email not found in session_state. Please log in again.")
        return

    user_ref = db.collection('users').document(email)
    user_data = user_ref.get()
    if not user_data.exists:
        st.write("User not found. Please log in again.")
        return

    user_info = user_data.to_dict()
    full_name = user_info.get('full_name', '')
    interests = user_info.get('interests', [])

    st.markdown("### Full Name:")
    st.write(full_name)

    st.markdown("### Email:")
    st.write(email)

    st.markdown("### Interests:")
    st.write(", ".join(interests))
    if st.button("Modify Profile"):
        session_state['page'] = 'modify_profile'

def modify_profile(session_state):
    if st.button("← Back "):
            session_state['page'] = 'recommendation'
    st.title("Modify Profile")
    st.markdown("---")
    email = session_state.get('email')
    if email is None:
        st.write("Email not found in session_state. Please log in again.")
        return

    user_ref = db.collection('users').document(email)
    user_data = user_ref.get()
    if not user_data.exists:
        st.write("User not found. Please log in again.")
        return

    user_info = user_data.to_dict()
    full_name = user_info.get('full_name', '')
    interests = user_info.get('interests', [])

    st.markdown("### Full Name:")
    st.write(full_name)

    st.markdown("### Email:")
    st.write(email)

    st.markdown("### Current Interests:")
    st.write(", ".join(interests))

    st.markdown("---")
    options = ["Cell Biology", "Virology", "Chemistry", "Environmental Studies", "Physics", "Human Health Studies", "Technology and Computer Science", "Agricultural Studies", "Cancer Study", "Geology and Earth  Studies","Biotechnology","General Medicine","Astronomy","Psychology","Phisiology","Education","Pharmacy","Mathematics"]
    new_interests = st.multiselect("Select your new interests:", options=options, default=[i for i in interests if i in options])
    
    if st.button("Submit"):
        # Update user profile in Firebase
        user_ref.update({
            'interests': new_interests
        })
        st.success("Profile updated successfully!")
        session_state['page'] = 'profile_info'

def review_page_student(session_state):
    paper = session_state.get('selected_paper')
    if st.button("← Back "):
            session_state['page'] = 'recommendation'
    if paper is not None and not paper.empty:
        st.title(paper['title'])
        st.write("**Abstract:**", paper['abstract'])
        st.write("**Publication Year:**", paper['pub_year'])
        st.write("**Author:**", paper['author'])
        st.write("**Pages:**", paper['pages'])
        st.write("**Publisher:**", paper['publisher'])
        st.write("**Number of Citations:**", paper['num_citations'])
        if st.button("Download"):
            st.write("Download link:", paper['pub_url'])
        # Display back button at the top
        
    else:
        st.write("Selected paper not found.")
# Review Page for Researcher
def review_page_researcher(session_state):
    paper = session_state.get('selected_paper')
    if paper:
        # Display back button at the top
        if st.button("← Back "):
            session_state['page'] = 'researcher'
        st.title(paper['title'])
        st.write("Conclusion:", paper['conclusion'])  # Displaying conclusion
        st.write("Publication Year:", paper['publication_year'])  # Displaying publication year
        st.write("Author:", paper['author'])  # Displaying author
        st.button("Download")
# Define the function to display the graph
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import streamlit as st

def display_graph(session_state, dataset, relation):
    if st.button("← Back "):
        session_state['page'] = 'recommendation'
        return

    selected_interests = session_state.get('interests', [])
    basic_data = dataset[dataset['topic'].isin(selected_interests)]

    # Calculate the pass number
    pass_number = 100 // len(selected_interests)

    # Collect articles per category
    second_data = pd.DataFrame()
    for category in selected_interests:
        category_data = basic_data[basic_data['topic'] == category]
        category_data = category_data.sort_values(by=['pub_year', 'semantic_score'], ascending=[False, False])
        category_data = category_data.head(pass_number)
        second_data = pd.concat([second_data, category_data])

    # Make sure second_data has exactly 100 articles
    if len(second_data) < 100:
        extra_data = basic_data[~basic_data['id'].isin(second_data['id'])]
        extra_data = extra_data.sample(n=100-len(second_data))
        second_data = pd.concat([second_data, extra_data])

    # Sample data of the first 10 articles
    data_sample = second_data.head(20)  # Get the top 20 articles

    # Create a graph
    G = nx.Graph()

    # Add nodes
    for idx, row in data_sample.iterrows():
        # Calculate node size with error handling for division by zero and missing values
        try:
            semantic_score_norm = (row['semantic_score'] - data_sample['semantic_score'].min()) / (data_sample['semantic_score'].max() - data_sample['semantic_score'].min())
            num_citations_norm = (row['num_citations'] - data_sample['num_citations'].min()) / (data_sample['num_citations'].max() - data_sample['num_citations'].min())
            node_size = 0.25 + 0.75 * ((semantic_score_norm + num_citations_norm) / 2)
        except (ZeroDivisionError, KeyError, ValueError):
            # Assign a default size for division by zero or missing values
            node_size = 0.25

        G.add_node(row['id'], size=node_size)

    # Add edges based on theme
    for idx, row in data_sample.iterrows():
        theme_articles = data_sample[data_sample['topic'] == row['topic']]
        for idx2, row2 in theme_articles.iterrows():
            if row['id'] != row2['id']:
                G.add_edge(row['id'], row2['id'], color='green')

    # Add edges based on citation relationships
    for idx, row in relation.iterrows():
        if row['file_id'] in data_sample['id'].values and row['citedby_id'] in data_sample['id'].values:
            G.add_edge(row['file_id'], row['citedby_id'], color='black')

    # Calculate PageRank
    pagerank = nx.pagerank(G)

    # Sort nodes by PageRank score
    sorted_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)

    # Get the top 20 nodes with highest PageRank scores
    top_20_nodes = [node for node, score in sorted_pagerank[:15]]

    # Create a subgraph containing only the top 20 nodes
    subgraph = G.subgraph(top_20_nodes)

    # Set the figure size
    plt.figure(figsize=(12, 8))

    # Draw nodes
    pos = nx.spring_layout(subgraph, k=0.9)
    node_sizes = [subgraph.nodes[node].get('size', 0) * 1000 for node in subgraph.nodes()]
    nx.draw_networkx_nodes(subgraph, pos, node_size=node_sizes)

    # Draw labels
    labels = {node: str(node) for node in subgraph.nodes()}
    nx.draw_networkx_labels(subgraph, pos, labels=labels)

    # Draw edges based on color
    edges = subgraph.edges()
    colors = [subgraph[u][v]['color'] for u, v in edges]
    edge_widths = [1 if color == 'black' else 2 for color in colors]
    nx.draw_networkx_edges(subgraph, pos, edge_color=colors, width=edge_widths, arrows=True)

    # Display the graph
    plt.axis('off')
    st.pyplot(plt)

    # Display article IDs and titles
    st.write("Article IDs and Titles:")
    for node in subgraph.nodes():
        article = data_sample[data_sample['id'] == node]
        if not article.empty:
            st.write(f"- ID: {article['id'].values[0]}, Title: {article['title'].values[0]}")


def search_recommendation(session_state, dataset):
    if st.button("Back to Recommendation"):
        session_state['page'] = 'recommendation'
    search_query = session_state.get('search_query', '')
    st.title(f"Search Results for: {search_query}")
    # Search logic
    search_results = dataset[
        (dataset['title'].str.contains(search_query, case=False)) |
        (dataset['abstract'].str.contains(search_query, case=False)) |
        (dataset['topic'].str.contains(search_query, case=False)) |
        (dataset['keywords'].str.contains(search_query, case=False))
    ][:20]  # Limit to 20 results

    if len(search_results) == 0:
        st.write("No results found.")

    for index, row in search_results.iterrows():
        # Display title
        st.markdown(f"**{row['title']}**")
        # Display abstract (3 lines initially)
        abstract_lines = row['abstract'].split('\n')
        abstract_preview = '\n'.join(abstract_lines[:3])
        st.write(abstract_preview)
        if len(abstract_lines) > 3:
            if st.button("Read more"):
                st.write('\n'.join(abstract_lines))
        st.markdown(f"**Keywords:** {row['keywords']}")
        st.markdown(f"[Download {row['title']} here]({row['pub_url']})")
        # Add a separator between articles
        st.write("---")

def main():
    # Initialize Session State
    session_state = st.session_state
    if 'logged_in' not in session_state:
        session_state['logged_in'] = False
    if 'page' not in session_state:
        session_state['page'] = 'first_time'
    if session_state['page'] == 'first_time':
        first_time(session_state)
        
    elif session_state['page'] == 'login':
        login(session_state)
        if session_state['logged_in']:
            if session_state['role'] == 'Student':
                session_state['page'] = 'recommendation'
            else:
                session_state['page'] = 'researcher'
    elif session_state['page'] == 'newUser':  # Handle newUser page here
        newUser(session_state)
        if session_state['logged_in']:
            if session_state['role'] == 'Student':
                session_state['page'] = 'recommendation'
            else:
                session_state['page'] = 'researcher'
    elif session_state['page'] == 'recommendation':
        # Always calculate and display recommendations
        display_recommended_papers(session_state, session_state.get('full_name', 'User'))
    elif session_state['page'] == 'review_student':
        review_page_student(session_state)
    elif session_state['page'] == 'review':
        review_page_researcher(session_state)
    elif session_state['page'] == 'researcher':
        researcher_page(session_state, session_state.get('full_name', 'User'))
        if session_state['role'] == 'researcher':
            if session_state['selected_paper']:
                review_page_researcher(session_state)
    elif session_state['page'] == 'graph':
        display_graph(session_state, dataset, relation)
        
    elif session_state['page'] == 'search_recommendation':
        search_recommendation(session_state, dataset)
    elif session_state['page'] == 'profile_info':
        display_profile_info(session_state)
    elif session_state['page'] == 'modify_profile':
        modify_profile(session_state)    

    # Update session state after each interaction
    st.session_state = session_state

if __name__ == "__main__":
    main()
