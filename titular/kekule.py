from pathlib import Path
import streamlit as st
from streamlit.components.v2 import component as st_v2_component


JS_CONTENT = (Path(__file__).parent / 'kekule-bundle.js').read_text()

CSS_CONTENT = (Path(__file__).parent / 'kekule-bundle.css').read_text()
CSS_CONTENT = "/*\n*/" + CSS_CONTENT

_kekule_editor_component = st_v2_component(
    'Titular.kekule_editor',
    js=JS_CONTENT,
    css=CSS_CONTENT,
    isolate_styles=False
)


def kekule_editor(key):
    key_last_smiles = f'{key}@last_smiles'

    def _on_change():
        editor_state = st.session_state.get(key, {'smiles': None})
        new_smiles = editor_state['smiles']
        old_smiles = st.session_state.get(key_last_smiles, None)
        if new_smiles is not None and new_smiles != old_smiles:
            st.session_state[key_last_smiles] = new_smiles

    _kekule_editor_component(
        key=key,
        on_smiles_change=_on_change,
    )

    return st.session_state.get(key_last_smiles)
