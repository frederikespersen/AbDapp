import streamlit as st
from streamlit import session_state as ses, title

import os

import src.layouts as layouts
import src.navigation as navigation

# ················································································· #

def run(debug: bool=False) -> None:
    """
    The standard setup to run every rerun.

    :return: Ensures `ses.Campaign` is loaded, otherwise runs `main`
    """

    layouts.page_template()

    if not hasattr(ses, 'initialized'):
        initialize()

    else:
        main()

    if debug:
        with st.sidebar:
            layouts.debugger()

# ················································································· #

def initialize() -> None:
    """
    The setup to run when initializing a session.

    :return: Sets `ses.Campaign`
    """

    layouts.front_page()

# ················································································· #

def main() -> None:
    """
    The setup to run by default.

    :return:
    """

    pg = st.navigation({
        category:
            [st.Page(os.path.join('stpages', file), title=title) for file, title in pages.items()]
        for category, pages in navigation.main_navigation.items()
    })
    pg.run()
