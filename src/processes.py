import streamlit as st
from matplotlib.style.core import library
from streamlit import session_state as ses

import pandas as pd

import src.events as events
import src.data as data
import src.utils as utils


# ················································································· #

class Campaign:

    @staticmethod
    @st.dialog("Create a New Campaign")
    def create():
        """
        The process for filling out information to create a database file.

        :session return: `ses.Campaign`
        :return: Creates a database file locally. Sets `ses.Campaign`
        """
        if not hasattr(ses, 'CreateCampaign'):
            ses.CreateCampaign = utils.Layer()
        if not hasattr(ses.CreateCampaign, 'Data'):
            events.Campaign.create()
        else:
            events.Campaign.submit(ses.CreateCampaign.Data)

    # ·············································································· #

    @staticmethod
    @st.dialog("Select Existing Campaign")
    def load():
        if not hasattr(ses, 'LoadCampaign'):
            ses.LoadCampaign = utils.Layer()
        if not hasattr(ses.LoadCampaign, 'Data'):
            events.Campaign.upload()
        else:
            events.Campaign.submit(ses.LoadCampaign.Data)



# ················································································· #

class Antigen:

    @staticmethod
    @st.dialog("Add antigen", width='large')
    def create():
        st.write("Antigens are specified for experiments.")
        name, description = events.Antigen.input()
        events.Antigen.submit(name, description)



# ················································································· #

class Library:

    @staticmethod
    @st.dialog("Add antigen", width='large')
    def create():
        st.header("Define Library Frameworks")
        st.write("""
                    To be able to define hits by CDRs and to perform CDR grafting, the library
                    framework and its CDR definitions must be defined.

                    AbDapp comes with preset common libraries.
                    """)

        # ····· Template ····· #
        st.markdown("##")
        st.subheader("1. Fill out framework template", divider='blue')
        st.write("""
                    Download and fill out the following Library template. 
                    For VHH libraries, omit the light chain fields (CDRLX start/end, FRWLX). 
                    Fill out CDR start and end positions according to the specified scheme.
                    """)
        st.write("Be sure to check whether the library does already exists in the database first:")
        st.dataframe(ses.Campaign.Data.Library, use_container_width=True)
        events.Library.download_template()

        # ····· Upload ····· #
        st.markdown("##")
        st.subheader("2. Submit entry", divider='blue')
        st.write("Upload the filled out template and submit the entry.")
        entries = events.Library.upload()
        if entries is not None:
            events.Library.submit(entries)



# ················································································· #

class Sanger:

    @staticmethod
    @st.dialog("Add Sanger sequences", width='large')
    def create():
        st.header("Upload translated Sanger sequencing reads")
        st.write("""
                    The sequences of individual clones can be determined by Sanger sequencing. 
                    Clone samples are sent for sequencing, and the subsequent sequencing chromatograms are
                    analysed in XLibraryDisplay. The input for *AbDapp* are the translated reads from XlibraryDesign. \n
                    Be sure to align sequencing reads of clones to the appropriate frameworks and to remove
                    any sequencing reads that you do not feel confident in from the XLibraryDesign alignment,
                    before exporting the sequences to FASTA format.

                    Data is uploaded library-wise.
                    """)
        # TODO: Guide: What to do in XLibraryDisplay

        # ····· Upload ····· #
        if not hasattr(ses.CreateSanger, 'fasta') or getattr(ses.CreateSanger, 'fasta') is None:
            st.subheader("1. Upload FASTA", divider='blue')
            ses.CreateSanger.fasta = events.Sanger.upload()

        # ····· Clone names ····· #
        elif not hasattr(ses.CreateSanger, 'clone_names'):
            st.subheader("2. Specify clone names", divider='blue')
            st.write("Each Sanger read is registered to a specific single-colony clone. Therefore, a clone name must be specified for each Sanger entry.")

            auto_tab, upload_tab, manual_tab = st.tabs(
                ['Extract clone names from FASTA', 'Upload clone names', 'Manually enter clone names'])

            with auto_tab:
                events.Sanger.auto_clone_names()
            with upload_tab:
                pass # TODO: Complete other naming options
            with manual_tab:
                events.Sanger.input_clone_names()

        # ····· Entries ····· #
        # TODO: Inform of overwriting
        if 'clone_names' in ses.CreateSanger:
            ses.CreateSanger.fasta['Clone'] = ses.CreateSanger.clone_names
            ses.CreateSanger.entries = ses.CreateSanger.fasta[data.data_model['Sanger']].copy()

        # ····· Clones ····· #
        if 'entries' in ses.CreateSanger:
            st.subheader("3. Register clones", divider='blue')
            st.write("If a clone is not already registered, new entries should be created.")
            new_clones = events.Clone.create(ses.CreateSanger.clone_names)
            if new_clones is not None:
                ses.CreateSanger.clone_entries = new_clones

        # ····· Hits ····· #
        if 'clone_entries' in ses.CreateSanger:
            st.subheader("4. Register hits", divider='blue')
            st.write("Each sequence is associated with a hit, which is characterized by its library and its CDR set. A unique set of CDRs in a library constitute a hit. The hit of each sequence is deduced, and if it does not exist yet, will be created in the database.")
            st.write("Each Sanger sequence will be annotated according to its library framework. ")
            library_name = events.Hit.choose_library()
            if library_name is not None:
                if not hasattr(ses.CreateSanger, 'cdrs'):
                    ses.CreateSanger.cdrs = utils.Sequence.extract_cdrs(
                        ses.CreateSanger.entries.Sequence,
                        library_name,
                        ses.CreateSanger.clone_entries.index)
                ses.CreateSanger.hit_entries = events.Hit.create(ses.CreateSanger.cdrs, library_name)
            # TODO: Map clones to hits
            # TODO: Remove deprecated hits

        # ····· Submit ····· #
        if getattr(ses.CreateSanger, 'hit_entries', None) is not None:
            st.subheader("5. Submit data", divider='blue')
            if st.button('Submit Sanger data', type='primary'):
                st.write(":ladybug: The button at least works")
                # events.Sanger.submit(ses.CreateSanger.entries)
                # events.Clone.submit(ses.CreateSanger.clone_entries)
                # events.Hit.submit(ses.CreateSanger.hit_entries)
                # delattr(ses, 'add_Sanger')
                # delattr(ses, 'CreateSanger')
                # # TODO: Reroute to save campaign
