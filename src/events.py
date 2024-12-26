import streamlit as st
from streamlit import session_state as ses, text_input

import os
import pandas as pd

import src.data as data
import src.utils as utils



# ················································································· #

class Campaign:

    @staticmethod
    def create():
        ses.CreateCampaign.target = st.text_input("Target", None)
        ses.CreateCampaign.placement = st.text_input("Placement", os.getcwd())

        if ses.CreateCampaign.target is not None:
            ses.CreateCampaign.database = os.path.join(ses.CreateCampaign.placement, f'{ses.CreateCampaign.target}_campaign.xlsx')
            ses.target = ses.CreateCampaign.target

            if os.path.exists(ses.CreateCampaign.database):
                st.error(f"A Campaign already exists at:\n'{ses.CreateCampaign.database}'")
                lcol, rcol = st.columns(2)
                with lcol:
                    if st.button("Overwrite Existing", type='primary'):
                        data.Data.create(ses.CreateCampaign.database)
                        ses.CreateCampaign.Data = data.Data.read(ses.CreateCampaign.database)
                        st.rerun()
                with rcol:
                    if st.button("Load Existing", type='primary'):
                        ses.CreateCampaign.Data = data.Data.read(ses.CreateCampaign.database)
                        st.rerun()

            else:
                if st.button("Create Campaign", type='primary'):
                    data.Data.create(ses.CreateCampaign.database)
                    ses.CreateCampaign.Data = data.Data.read(ses.CreateCampaign.database)
                    st.rerun()

    # ·············································································· #

    @staticmethod
    def upload():
        ses.LoadCampaign.database = st.file_uploader("Choose the Campaign Excel database file", type=["xlsx"])
        if getattr(ses.LoadCampaign, 'database') is not None:
            if st.button("Load Campaign", type='primary'):
                ses.LoadCampaign.Data = data.Data.read(ses.LoadCampaign.database)
                ses.target = ses.LoadCampaign.database.name.replace('_campaign.xlsx', '')
                st.rerun()

    # ·············································································· #

    @staticmethod
    def submit(tables):
        ses.Campaign = utils.Layer()
        ses.Campaign.Data = utils.Layer()

        for entity, table in tables.items():
            setattr(ses.Campaign.Data, entity, table)
        setattr(ses, 'initialized', True)
        if hasattr(ses, 'CreateCampaign'):
            delattr(ses, 'CreateCampaign')
        if hasattr(ses, 'LoadCampaign'):
            delattr(ses, 'LoadCampaign')
        st.rerun()

    # ·············································································· #

    @staticmethod
    def save(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            for entity in data.data_model.keys():
                if 'Name' in data.data_model[entity]:
                    ses.Campaign.Data.get(entity).to_excel(writer, sheet_name=entity, index=True)
                else:
                    ses.Campaign.Data.get(entity).to_excel(writer, sheet_name=entity, index=False)



# ················································································· #

class Antigen:

    @staticmethod
    def input():
        st.write("Antigens are specified for experiments.")
        name = st.text_input('Antigen name', None)
        description = st.text_input('Antigen description', None)
        return name, description

    # ·············································································· #

    @staticmethod
    def submit(name, description):
        if name is not None:
            if st.button('Submit'):
                data.Data.Create.Antigens(
                    pd.DataFrame({'Description': [description]}, index=[name]))
                st.rerun()



# ················································································· #

class Library:

    @staticmethod
    def download_template():
        st.download_button('Download Library template',
                           pd.DataFrame(columns=data.data_model['Library']).to_csv(index=False),
                           'AbDapp_Library_template.csv',
                           type='secondary')
        guide = st.expander("Instructions for filling out template")
        with guide:
            st.write("""
                                The fields must be filled out according to these constraints:

                                * **Name**: `text` The name that will be displayed in dropdowns
                                * **Class**: `text = [scFv, VHH]` Either `scFv` or `VHH` (note the case)
                                * **Numbering scheme**: `text = [imgt, kabat, chothia, martin]` The Ab numbering scheme to pass to [ANARCI](https://github.com/oxpig/ANARCI). This numbering scheme is used to extract CDRs.
                                * **FRW{}{}** The amino acid sequence for the framework regions. Used to graft together CDRs.
                                * **CDR{}{} start/end** The start and end positions of the CDRs. Will be used to extract CDRs from sequences annotated by ANARCI.
                                """)

    # ·············································································· #

    @staticmethod
    def upload():
        uploaded_file = st.file_uploader("Upload Template", ['CSV'])
        if uploaded_file is not None:
            entries = pd.read_csv(uploaded_file, index_col=0)
            # TODO: Data validation
            return entries

    # ·············································································· #

    @staticmethod
    def submit(entries):
        st.dataframe(entries, use_container_width=True)
        if len(entries) > 0:
            if st.button('Submit', type='primary'):
                data.Data.Create.Library(entries)
                st.rerun()



# ················································································· #

class Clone:

    @staticmethod
    def create(names):
        sample = text_input("Name clone sample (i.e. 'Phage R1' etc.)", None)
        if sample is not None:
            entries = pd.DataFrame({
                'Name': names,
                'Sample': sample
            }).set_index('Name')
            entries = entries[~data.Data.Exists.Clone(entries)]
            if entries is not None:
                st.dataframe(entries, use_container_width=True)
                if st.button('Confirm clones', type='primary'):
                    return entries

    # ·············································································· #

    @staticmethod
    def submit(entries):
        if len(entries) > 0:
            data.Data.Create.Clone(entries)
            st.write(f"Created {len(entries)} new clones:")
            st.dataframe(entries, use_container_width=True)
        else:
            st.write("All clones already exist.")

    # ·············································································· #

    @staticmethod
    def cleanup():
        deprecated_clones = data.Data.Cleanup.Clone()
        st.write(f"Deleted {len(deprecated_clones)} deprecated clones with no measurement data:")
        st.dataframe(deprecated_clones, use_container_width=True)



# ················································································· #

class Sanger:

    @staticmethod
    def upload():
        st.write("Choose the FASTA file containing the translated clone Sanger sequences.")
        fasta = utils.Sequence.upload_fasta()
        if st.button("Process FASTA", type='primary', disabled=fasta is None):
            return fasta

    # ·············································································· #

    @staticmethod
    def submit_names(names):
        if st.button("Confirm clone names", type='primary', disabled=any([name is None for name in names]), key=f'names_{names}'):
            ses.CreateSanger.clone_names = names


    @staticmethod
    def auto_clone_names():
        names = utils.Names.extract_from_ids(ses.CreateSanger.fasta['ID'])
        Sanger.submit_names(names)

    @staticmethod
    def upload_clone_names():
        names = None
        Sanger.submit_names(names)

    @staticmethod
    def input_clone_names():
        # TODO: Populate ses.CreateSanger.mapping with the two more automated methods by default
        ses.CreateSanger.mapping = {}
        for id in ses.CreateSanger.fasta['ID']:
            ses.CreateSanger.mapping[id] = st.text_input(f"Clone name for `{id}`", key=f'sanger_name_{id}')
        if not all([name is not None for name in ses.CreateSanger.mapping.values()]):
            names = None
        else:
            names = [ses.CreateSanger.mapping[id] for id in ses.CreateSanger.fasta['ID']]
        Sanger.submit_names(names)

    # ·············································································· #

    @staticmethod
    def submit(entries):
        data.Data.Create.Sanger(entries)
        st.write(f"Adding {len(entries)} Sanger entries:")
        st.dataframe(entries, use_container_width=True)

# ················································································· #

class Hit:

    @staticmethod
    def create(cdrs, library_name):
        entries = cdrs[~data.Data.Exists.Hit(cdrs)].drop_duplicates()
        names = Hit.generate_names(len(entries))
        if names is not None:
            entries['Name'] = names
            entries['Library'] = library_name
            entries = entries.set_index('Name')
            st.dataframe(entries, use_container_width=True)
            if st.button('Confirm hits', type='primary'):
                return entries

    # ·············································································· #

    @staticmethod
    @st.cache_data
    def extract_cdrs(sequences, library_name: str):
        library = ses.Campaign.Data.Library.loc[library_name]
        progress = 0
        progress_increment = 1 / len(sequences)
        progress_bar = st.progress(0, text="Annotating sequences and extracting CDRs...")
        aligned = []
        for sequence in sequences:
            aligned.append(utils.Sequence.anarci_annotate(sequence, scheme=library['Numbering scheme']))
            progress += progress_increment
            progress_bar.progress(progress, text="Annotating sequences and extracting CDRs...")
        alignment = (pd.concat(aligned)
                     .sort_index(axis=1, key=utils.Sequence._position_sort_key)
                     .fillna('-'))
        if hasattr(sequences, 'index'):
            alignment.index = sequences.index
        chains = ['L', 'H']
        if library.Class == 'VHH':
            chains = ['H']
        cdrs = {}
        for chain in chains:
            for cdr in [1, 2, 3]:
                cdr_seqs = utils.Sequence.position_slice(
                    alignment[chain],
                    library[f'CDR{chain}{cdr} start'],
                    library[f'CDR{chain}{cdr} end'])
                cdrs[f'CDR{chain}{cdr}'] = cdr_seqs.sum(axis=1).str.replace('-', '')
        progress_bar.empty()
        with st.expander(f"Inspect the {library['Numbering scheme'].upper()} numbered alignment"):
            st.write("*Table can be downloaded via button in upper right corner*.")
            st.dataframe(alignment)
        return pd.concat(cdrs, axis=1)

    # ·············································································· #

    @staticmethod
    def choose_library():
        if len(ses.Campaign.Data.Library) == 0:
            st.error("Please enter Library data first.")
        else:
            library_name = [st.selectbox('Select Library', [None, *ses.Campaign.Data.Library.index])][0]
            if library_name is not None:
                return library_name

    # ·············································································· #

    @staticmethod
    def generate_names(n):
        prefix = text_input("Prefix for hit names")
        taken = ses.Campaign.Data.Hit.index.str.replace(prefix, '')
        taken = taken[taken.str.isnumeric()]
        if len(taken) > 0:
            i = int(taken.max())
        else:
            i = 1
        return [f'{prefix}{k}' for k in range(i, i + n)]

    # ·············································································· #

    @staticmethod
    def submit(entries):
        if len(entries) > 0:
            data.Data.Create.Hit(entries)
            st.write(f"Created {len(entries)} new hits:")
            st.dataframe(entries, use_container_width=True)
        else:
            st.write(f"All hits already exist.")


# ················································································· #

class Names:

    @staticmethod
    def by_delimiters(ids):
        dcol, ncol, ecol = st.columns(3)
        with dcol:
            delim1 = st.text_input("Split by...", '.', key='delim1')
            st.write("Then...")
            delim2 = st.text_input("Split by...", '_', key='delim2')
        with ncol:
            n1 = st.slider("And choose the number...", 1, 10, key='n1')
            st.write("")
            n2 = st.slider("And choose the number...", 1, 10, key='n2')
        with ecol:
            end1 = st.selectbox("", ["First", "Last"], 0, key='end1')
            st.write("")
            end2 = st.selectbox("", ["First", "Last"], 1, key='end2')
        st.write("And finally add...")
        pcol, scol = st.columns(2)
        with pcol:
            prefix = st.text_input('Prefix', 'LibX_', key='prefix')
        with scol:
            suffix = st.text_input('Suffix', key='suffix')
        names = (
            ids
            .map(lambda s: utils.Names.delim_extract(s, delim1, n1, end1))
            .map(lambda s: utils.Names.delim_extract(s, delim2, n2, end2))
            .map(lambda s: prefix + s + suffix))
        st.dataframe(pd.DataFrame({'ID': ids, 'Clone name': names}), use_container_width=True)
        return names

