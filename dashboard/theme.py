import streamlit as st

# ---------------------------------------------------------
# GLOBAL THEME CONFIGURATION (FINAL, CLEAN, CENTRALIZED)
# ---------------------------------------------------------

def set_theme():
    """
    Applies a clean, modern F1‑style dark theme to the dashboard.
    Centralized theme — applies to all pages and sections.
    """

    st.markdown(
        """
        <style>

        /* ------------------------------
           GLOBAL PAGE STYLE
        ------------------------------ */
        html, body, .main {
            background-color: #0d0d0d !important;
            color: #e6e6e6 !important;
        }

        /* ------------------------------
           HEADERS
        ------------------------------ */
        h1, h2, h3, h4, h5 {
            color: #ff1e00 !important; /* Ferrari red */
            font-weight: 700 !important;
        }

        /* ------------------------------
           SIDEBAR
        ------------------------------ */
        section[data-testid="stSidebar"] {
            background-color: #111111 !important;
            border-right: 1px solid #333333 !important;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #ff1e00 !important;
        }

        /* ------------------------------
           METRICS
        ------------------------------ */
        div[data-testid="metric-container"] {
            background-color: #1a1a1a !important;
            border-radius: 10px !important;
            padding: 15px !important;
            border: 1px solid #333333 !important;
        }

        /* ------------------------------
           TABLES
        ------------------------------ */
        .dataframe {
            color: #e6e6e6 !important;
        }

        .dataframe th {
            background-color: #222222 !important;
            color: #ff1e00 !important;
        }

        .dataframe td {
            background-color: #111111 !important;
        }

        /* ------------------------------
           BUTTONS
        ------------------------------ */
        .stButton>button {
            background-color: #ff1e00 !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 0.6rem 1.2rem !important;
            border: none !important;
            font-weight: 600 !important;
        }

        .stButton>button:hover {
            background-color: #cc1900 !important;
        }

        /* ------------------------------
           SELECTBOX / DROPDOWNS
        ------------------------------ */
        div[data-baseweb="select"] {
            background-color: #1a1a1a !important;
            color: white !important;
        }

        /* ------------------------------
           FOOTER
        ------------------------------ */
        footer {
            visibility: hidden !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
