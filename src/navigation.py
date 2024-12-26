import streamlit as st
from streamlit import session_state as ses

# TODO: Refactor to data/

# ················································································· #

main_navigation = {
  "Campaign": {
    "00_dashboard.py": "Dashboard",
    "01_data.py": "Data",
    "02_constructs.py": "Output sequences for expression",
    "03_settings.py": "Settings"
  },
  "Hit Discovery": {
    "10_hit_discovery.py": "Inspect hit marker data",
    "11_hit_analysis.py": "Hit analysis",
    "12_hit_trends.py": "Hit trends",
    "13_inspect_hit.py": "Check out individual hits"
  },
  "Hit-to-lead": {
    "20_hit_selection.py": "Hit selection",
    "21_hit_grafting.py": "Graft hits into leads",
    "22_lead_discovery.py": "Inspect lead marker data",
    "23_lead_analysis.py": "Lead analysis",
    "24_inspect_lead.py": "Check out individual leads"
  },
  "Lead optimization": {
    "30_lead_trends.py": "Lead trends",
    "31_custom.py": "Customize leads"
  },
  "Experimental": {
    "40_ai.py": "Predicted affinities"
  }
}
