# AbDapp
AbDapp (will be) an open-source analysis app for curating, merging, analysing, and engineering Antibody Discovery data.

AbDapp is based on the [Streamlit](https://streamlit.io) framework.

This app is designed to prioritize direct data access for users with little to no experience in data science and programming.
As such, the app initialises a database as a local Excel-file that can be created and loaded by the user via the app.

**Note** ``AbDapp`` is a work in progress. Initially, data upload and handling functions are prioritized.

## Contents

* ``abdapp.py``: Main ``AbDapp`` module
* ``app.py``: Streamlit App [``streamlit run app.py``]
* ``abdapp.yaml``: Conda environment configuration file [``conda env create -f abdapp.yml``].
* **``src/``**: Source code used for the App. See "Development" below.
* **``stpages/``**: Streamlit pages.
* **``doc/``**: Graphics for documentation.

## Getting started

### 1. Clone repository
```sh
git clone https://github.com/frederikespersen/AbDapp.git
cd AbDapp
```

### 2. Setup environment
```sh
conda env create -f abdapp.yml
conda activate abdapp
```

### 3. Run AbDapp locally
```sh
streamlit run app.py
```

As by Streamlit's default, you can find the app hosted on [localhost port 8501](http://localhost:8501).


## Development

The ``src`` for the App is build around the following design:

![](doc/src.png)