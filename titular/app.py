import plotly.express as px
import streamlit as st

from titular.logic import (
    titurate,
    validate_smiles
)
from titular.kekule import kekule_editor

st.set_page_config(
    page_title="Titular: (des)protonação ilustrada",
    layout="centered",
)

st.title("Olá, estudante! 👋")
st.markdown(
    """
    Seja bem vindo ao Titular.

    Aqui você pode avaliar a formação de microestados
    decorrentes da protonação/desprotonação de sítios
    presentes em moléculas quaisquer.

    A concentração de íons hidrogênio no meio (o pH mede
    isso de um jeito engraçado, pelo inverso e com log)
    explica esse comportamento. Quando está baixa (pH alto),
    os prótons/íons H "desgrudam" da molécula e vão para
    o meio/solução (desprotonação), fazendo a molécula
    ficar "faltando" tal átomo e deixando a carga da
    molécula menos positiva, ou até mesmo negativa. Se a
    concentração de hidrogênio estiver alta (pH baixo), fará
    "grudá-los" na molécula tornando-a mais positiva (protonação).

    Se uma molécula tem apenas um sítio ionizável, o valor de
    pH que os microestados protonado/desprotonado ocorrem a
    50%/50% é o pKa. Se houver mais de um ponto/átomo (sítio)
    sujeito a alteração do estado de ionização pela adição/remoção
    de hidrogênio, então haverá pKa, pKb, pKc...

    **Atenção**: a ferramenta que possibilita este cálculo
    de ionização, a *[Dimorphite-DL](https://durrantlab.github.io/dimorphite_dl/)*,
    alerta para dificuldades com aminas terciárias e com
    os heterociclos indol e pirrol.
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

fig = px.bar(
    df,
    x='span',
    base='begin',
    y='smiles',
    color='smiles',
    orientation='h',
    custom_data=['label', 'img', 'begin']
)
fig.update_traces(
    unselected=dict(marker=dict(opacity=1.0)),
    selected=dict(marker=dict(opacity=1.0)),
    hovertemplate=(
        "pH ∈ %{customdata[0]}</br>"
        "<extra></extra>"
    )
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
    showlegend=False,
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
        key='key_titruration_bar',
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
        label, img, begin = points[0]['customdata']
        st.header(f"pH ∈ {label}")
        st.image(img)
main_area()