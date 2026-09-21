import plotly.express as px
import streamlit as st

from titular.logic import (
    titurate,
    validate_smiles
)
from titular.kekule import kekule_editor

st.set_page_config(
    page_title="Titular: (des)protonação interativa",
    layout="centered",
)

st.title("Olá, estudante! 👋")
st.markdown(
    """
    Seja bem vindo ao Titular!.

    Aqui você pode avaliar a formação de microestados
    decorrentes da protonação/desprotonação de sítios
    presentes em moléculas quaisquer.

    Esta calculadora emula uma titulação ácido/base, e exibe as
    respectivas curvas, amostrando a ferramenta
    *[Dimorphite-DL](https://durrantlab.github.io/dimorphite_dl/)*
    em intervalos de pH de 0,1 em 0,1. **Atenção**: a *Dimorphite-DL*
    alerta para dificuldades com aminas terciárias
    e com os heterociclos indol e pirrol.
    """
)


smiles = kekule_editor(
    key='key_kekule_editor',
)

if not smiles:
    st.stop()
try:
    validate_smiles(smiles)
except Exception as exc:
    st.error("Falha ao validar molécula.")
    st.stop()

st.text("Diagrama de Titulação:")
df = titurate(smiles)

fig = px.line(
    df,
    x='ph',
    y='alpha',
    color='smiles',
    markers=True,
    custom_data=['smiles', 'image']
)
fig.update_traces(
    unselected=dict(marker=dict(opacity=1.0)),
    selected=dict(marker=dict(opacity=0.8)),
)
fig.update_layout(
    yaxis=dict(visible=False, showgrid=False, zeroline=False, fixedrange=True),
    xaxis=dict(
        visible=True, showgrid=True, zeroline=False, fixedrange=True,
        tickfont=dict(size=15, color="#454545"),
        title=dict(text="pH"),
        tick0=0,
        dtick=2,
    ),
    showlegend=True,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=0, b=0),
    height=250,
    xaxis_title=None,
    hoverlabel=dict(font_size=16, font_family="sans-serif"),
)

@st.fragment
def main_area():
    event = st.plotly_chart(
        fig,
        key='key_titruration_lines',
        width='stretch',
        on_select='rerun',
        selection_mode='points',
        config={
            "displayModeBar": False,
            "scrollZoom": False,
        },
    )
    points = event['selection']['points']
    if points:
        smi, img = points[0]['customdata']
        st.header(smi)
        st.image(img)
main_area()