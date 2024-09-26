import streamlit as st

# Set the page configuration
st.set_page_config(page_title='Stock Tracker App', layout='wide')

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        max-width: 2000px;
        margin: 0 auto;
    }
    .spacer {
        height: 100px;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar menu for page navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'  # Default page

# Function to handle page changes
def change_page(new_page):
    if new_page != st.session_state.current_page:
        st.session_state.current_page = new_page

# Sidebar to select the page
page = st.sidebar.selectbox("Select Page", ["Home", "Portfolio", "News", "Profile"])

# Call the page change function
change_page(page)

# Placeholder to clear content when switching between pages
placeholder = st.empty()

# Load the selected page content
with placeholder.container():  # Scoped container for page content
    if st.session_state.current_page == "Home":
        from Home import home_page
        home_page()
    elif st.session_state.current_page == "Portfolio":
        from Portfolio import portfolio_page
        portfolio_page()
    elif st.session_state.current_page == "Profile":
        from Profile import profile_page
        profile_page()
    elif st.session_state.current_page == "News":
        from news import news_page
        news_page()
