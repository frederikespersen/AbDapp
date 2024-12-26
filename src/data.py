from streamlit import session_state as ses

import os

import pandas as pd
import json



# ················································································· #

with open('data/data_model.json', 'r') as file:
    data_model = json.load(file)

# ················································································· #

cdr_cols = ['CDRL1', 'CDRL2', 'CDRL3', 'CDRH1', 'CDRH2', 'CDRH3']

# ················································································· #

class Data:

    # ················································································· #

    @staticmethod
    def from_template():
        tables = {name: pd.DataFrame(columns=columns) for name, columns in data_model.items()}
        for entity in data_model:
            template_path = f'data/templates/{entity}.csv'
            if os.path.isfile(template_path):
                tables[entity] = pd.read_csv(template_path)
            if 'Name' in data_model[entity]:
                tables[entity].set_index('Name', inplace=True)
        return tables

    # ················································································· #

    @staticmethod
    def read(path):
        tables = pd.read_excel(path, sheet_name=None)
        for entity, table in tables.items():
            if 'Name' in data_model[entity]:
                tables[entity] = table.set_index('Name')
        return tables

    @staticmethod
    def create(path):
        tables = Data.from_template()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            for entity in data_model.keys():
                if 'Name' in data_model[entity]:
                    tables[entity].to_excel(writer, sheet_name=entity, index=True)
                else:
                    tables[entity].to_excel(writer, sheet_name=entity, index=False)

    # ················································································· #

    class Create:
        """
        General format:
        1. Input entries
        2. Check for overwriting (Handle with event)
        3. Check for dependents
        3. Add/Delete dependents
        4. Link dependents
        5. Submit
        """

        @staticmethod
        def Antigens(entries: pd.DataFrame):
            ses.Campaign.Data.Antigen = pd.concat([
                ses.Campaign.Data.Antigen,
                entries
            ]).drop_duplicates()

        @staticmethod
        def Library(entries: pd.DataFrame):
            ses.Campaign.Data.Library = pd.concat([
                ses.Campaign.Data.Library,
                entries
            ]).drop_duplicates()

        @staticmethod
        def Clone(entries: pd.DataFrame):
            ses.Campaign.Data.Clone = pd.concat([
                ses.Campaign.Data.Clone,
                entries
            ]).drop_duplicates()

        @staticmethod
        def Hit(entries: pd.DataFrame):
            ses.Campaign.Data.Hit = pd.concat([
                ses.Campaign.Data.Hit,
                entries
            ]).drop_duplicates()

        @staticmethod
        def Sanger(entries: pd.DataFrame):
            ses.Campaign.Data.Sanger = pd.concat([
                ses.Campaign.Data.Sanger,
                entries
            ]).drop_duplicates()


    # ················································································· #

    class Delete:

        @staticmethod
        def Antigens(entries: pd.DataFrame):
            ses.Campaign.Data.Antigen = (
                ses.Campaign.Data.Antigen
                .drop(entries.index, axis=0))

    # ················································································· #

    class Cleanup:

        @staticmethod
        def Clone():
            clones = ses.Campaign.Data.Clone
            sanger_clones = ses.Campaign.Data.Sanger.Clone
            elisa_clones = ses.Campaign.Data.ELISA.Clone
            active_clones = pd.concat([sanger_clones, elisa_clones]).drop_duplicates()
            deprecated_clones = clones[~clones.index.isin(active_clones.index)]
            ses.Campaign.Data.Clone = clones[clones.index.isin(active_clones.index)]
            return deprecated_clones

    # ················································································· #

    class Exists:

        @staticmethod
        def Clone(entries):
            return entries.index.isin(ses.Campaign.Data.Clone.index)

        @staticmethod
        def Hit(entries):
            return (entries.apply(lambda row: row[cdr_cols].isin(ses.Campaign.Data.Hit[cdr_cols]).all(), axis=1))

# ················································································· #