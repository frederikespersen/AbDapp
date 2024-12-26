import streamlit as st
from streamlit import session_state as ses

import src.processes as processes
import src.data as data
import src.utils as utils


# ················································································· #

class Campaign:

    @staticmethod
    def creator():
        """
        The component for creating a new campaign.

        :component:
        :return: Creates a database file locally and sets `ses.Campaign`.
        """

        if hasattr(ses, 'CreateCampaign'):
            processes.Campaign.create()
        else:
            with st.container():
                st.subheader("Create New Campaign", divider='blue')
                lcol, rcol = st.columns(2)
                with lcol:
                    st.write("Create a new campaign and a local `[]_campaign.xlsx` database file.")
                with rcol:
                    if st.button("Create New Campaign", type='secondary'):
                        if hasattr(ses, 'LoadCampaign'):
                            delattr(ses, 'LoadCampaign')
                            st.rerun()
                        else:
                            processes.Campaign.create()

    # ············································································· #

    @staticmethod
    def loader():
        """
        The component for loading an existing campaign.

        :return: Loads a database file and sets `ses.Campaign`.
        """
        if hasattr(ses, 'LoadCampaign'):
            processes.Campaign.load()

        else:
            with st.container():
                st.subheader("Load Existing Campaign", divider='blue')
                lcol, rcol = st.columns(2)
                with lcol:
                    st.write("Load an existing campaign from a local `[]_campaign.xlsx` database file.")
                with rcol:
                    if st.button("Load Existing Campaign", type='secondary'):
                        if hasattr(ses, 'CreateCampaign'):
                            delattr(ses, 'CreateCampaign')
                        processes.Campaign.load()



# ················································································· #

class Data:

    @staticmethod
    def viewer(entity: str) -> tuple:
        st.header(f"{entity} entries")
        st.dataframe(getattr(ses.Campaign.Data, entity), use_container_width=True)

    # ············································································· #

    @staticmethod
    def clear_creators():
        rerun = False
        for entity in data.data_model:
            if hasattr(ses, f'Create{entity}'):
                delattr(ses, f'Create{entity}')
                rerun = True
        if rerun:
            st.rerun()

    # ············································································· #

    @staticmethod
    def creator(entity: str):
        if hasattr(processes, entity):
            if hasattr(getattr(processes, entity), 'create'):
                if st.button("Add entries", type='secondary', key=f'add_{entity}'):
                    Data.clear_creators()
                    setattr(ses, f'Create{entity}', utils.Layer())
                if hasattr(ses, f'Create{entity}'):
                    getattr(getattr(processes, entity), 'create')()

    # ············································································· #

    @staticmethod
    def updater(entity: str):
        # Note: Must take data model into account; Keys are immutable
        if hasattr(processes, entity):
            if hasattr(getattr(processes, entity), 'update'):
                if st.button("Update entries", type='secondary', key=f'update_{entity}'):
                    getattr(getattr(processes, entity), 'update')()

    # ············································································· #

    @staticmethod
    def deleter(entity: str):
        # Note: Must take data model into account when deleting
        if hasattr(processes, entity):
            if hasattr(getattr(processes, entity), 'delete'):
                if st.button("Delete entries", type='secondary', key=f'delete_{entity}'):
                    getattr(getattr(processes, entity), 'delete')()



# ················································································· #

class Utils:

    @staticmethod
    def ses_debugger():
        """
        A component for debugging the st.session_data.

        :return: Shows the st.session_data in JSON
        """
        st.subheader(":ladybug: :red[Debugging mode] :ladybug:")
        st.write("Session data:")
        session_data = {name: value for name, value in ses.items()}
        for name, value in session_data.items():
            if isinstance(value, utils.Layer):
                session_data[name] = {attr: getattr(value, attr) for attr in dir(value) if attr[0] != '_'}
        st.write(session_data)
