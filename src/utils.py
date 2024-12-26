import streamlit as st
from streamlit import session_state as ses

import io
import itertools
import subprocess
from typing import Literal

import pandas as pd
import streamlit as st
from Bio import SeqIO



# ················································································· #

class Layer:
    def __init__(self):
        pass

    def __contains__(self, item):
        return hasattr(self, item)



# ················································································· #

class Sequence:

    @staticmethod
    def upload_fasta() -> pd.DataFrame:
        uploaded_file = st.file_uploader("Upload FASTA file", type=["fasta"], on_change=st.rerun)
        if uploaded_file is not None:
            fasta = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            try:
                ids = []
                sequences = []
                for record in SeqIO.parse(fasta, "fasta"):
                    ids.append(record.id)
                    sequences.append(str(record.seq))
                df = pd.DataFrame({'ID': ids, 'Sequence': sequences})
                st.write(df)
                return df
            except Exception as e:
                if not e:
                    return None
                st.error(e)

    # ················································································· #

    @staticmethod
    def anarci_annotate(i, **kwargs: str) -> pd.DataFrame:
        # TODO: Typing for ANARCI: String or file input
        anarci_keywords = []
        for flag, value in kwargs.items():
            if len(flag) == 1:
                anarci_keywords += [f'-{flag}', f'{value}'.lower()]
            else:
                anarci_keywords += [f'--{flag}', f'{value}'.lower()]
        process = subprocess.Popen(
            ["ANARCI", "-i", i] + anarci_keywords,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"ANARCI failed with error: {stderr.decode()}")
        anarci_output = io.StringIO(stdout.decode()).readlines()
        anarci_entries = [list(y) for x, y in itertools.groupby(anarci_output, lambda z: z == '//\n') if not x]
        entries = []
        for anarci_entry in anarci_entries:
            entry_name = anarci_entry[0][2:-1]
            annotation = pd.Series([line.replace(' ', '').strip() for line in anarci_entry if line[0] != '#'][:-1])
            entry = (
                pd.DataFrame({
                    'Chain': annotation.str[0],
                    'Position': annotation.str[1:-1],
                    entry_name: annotation.str[-1]})
                .set_index(['Chain', 'Position'])
                .T
            )
            entries.append(entry)
        entries = pd.concat(entries)
        entries.sort_index(axis=1, key=Sequence._position_sort_key, inplace=True)
        return entries

    # ················································································· #

    @staticmethod
    def _position_sort_key(item):
        return [*map(lambda i: f'{i:0>4}', item)]

    # ················································································· #

    @staticmethod
    def position_slice(df: pd.DataFrame, pos_from: str, pos_to: str) -> pd.DataFrame:
        idx_from = df.columns.get_loc(str(pos_from))
        idx_to = df.columns.get_loc(str(pos_to))
        return df.iloc[:,idx_from:idx_to+1]

    @staticmethod
    def extract_cdrs(sequences, library_name: str, index=None):
        library = ses.Campaign.Data.Library.loc[library_name]
        progress = 0
        progress_increment = 1 / len(sequences)
        progress_bar = st.progress(0, text="Annotating sequences and extracting CDRs...")
        aligned = []
        for sequence in sequences:
            aligned.append(Sequence.anarci_annotate(sequence, scheme=library['Numbering scheme']))
            progress += progress_increment
            progress_bar.progress(progress, text="Annotating sequences and extracting CDRs...")
        alignment = (pd.concat(aligned)
                     .sort_index(axis=1, key=Sequence._position_sort_key)
                     .fillna('-'))
        if index is not None:
            alignment.index = index
        chains = ['L', 'H']
        if library.Class == 'VHH':
            chains = ['H']
        cdrs = {}
        for chain in chains:
            for cdr in [1, 2, 3]:
                cdr_seqs = Sequence.position_slice(
                    alignment[chain],
                    library[f'CDR{chain}{cdr} start'],
                    library[f'CDR{chain}{cdr} end'])
                cdrs[f'CDR{chain}{cdr}'] = cdr_seqs.sum(axis=1).str.replace('-', '')
        progress_bar.empty()
        with st.expander(f"Inspect the {library['Numbering scheme'].upper()} numbered alignment"):
            st.write("*Table can be downloaded via button in upper right corner*.")
            st.dataframe(alignment)
        return pd.concat(cdrs, axis=1)




# ················································································· #

class Names:

    @staticmethod
    def delim_extract(s: str, delimiter: str, n: int, end: Literal['Last', 'First']) -> str:
        if delimiter is None or delimiter == '':
            return s
        try:
            return s.split(delimiter)[-n if end == 'Last' else n - 1]
        except IndexError:
            return ''

    # ················································································· #

    @staticmethod
    def extract_from_ids(ids):
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
            .map(lambda s: Names.delim_extract(s, delim1, n1, end1))
            .map(lambda s: Names.delim_extract(s, delim2, n2, end2))
            .map(lambda s: prefix + s + suffix))
        st.write(pd.DataFrame({'ID': ids,
                               'Clone name': names}))
        return names