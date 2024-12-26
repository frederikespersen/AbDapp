import streamlit as st
from streamlit import session_state as ses

import src.components as components

# ················································································· #

def page_template() -> None:
    """
    A common template for all stpages in app.
    """

    st.set_page_config(layout='centered',
                       page_title=f"{ses.get('target', '')} Antibody Discovery Campaign",
                       page_icon='static/favicon.ico')
    st.logo('static/epi_logo.png')

# ················································································· #

def front_page():
    """
    The front page.
    Written as a function as an excpetion.
    """

    st.title("AbDapp: The _Antibody Discovery app_")

    components.Campaign.loader()
    st.markdown('#')
    components.Campaign.creator()

# ················································································· #

def data_interaction(entities):
    tabs = st.tabs(entities)
    for entity, tab in zip(entities, tabs):
        with tab:
            components.Data.viewer(entity)

            coll, colm, colr = st.columns(3)
            with coll:
                components.Data.creator(entity)
            with colm:
                components.Data.updater(entity)
            with colr:
                components.Data.deleter(entity)

# ················································································· #

def debugger():
    """
    A layout for debugging.
    """

    components.Utils.ses_debugger()