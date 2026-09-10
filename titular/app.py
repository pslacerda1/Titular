import plotly.express as px
import streamlit as st

from titular.logic import (
    titurate,
    validate_smiles
)
from titular.kekule import kekule_editor

st.title("Olá, estudante! 👋")
st.markdown(
    """
    Bem vindo ao Titular.

    Aqui você pode avaliar a formação de microestados
    decorrentes da protonação/desprotonação de sítios
    ionizáveis presentes em moléculas quaisquer.

    A concentração de hidrogênio no meio (o pH mede
    isso de um jeito engraçado, pelo inverso), quando
    está baixa, puxa os hidrogênios da molécula para
    o meio/solução, fazendo a molécula ficar faltando
    tal átomo e deixando a carga da moléucla negativa.
    Se a concentração estiver alta, fará grudar os hidrgênios
    na molécula tornando-a um íon positivo. O valor de
    pH que essas transformações ocorrem é conhecido
    como pKa.

    Se houver mais de um ponto/átomo sujeito a alteração
    de carga pela adição/remoção de hidrogênio, então
    haverá mais de um pkA.

    **Atenção**: a ferramenta que possibilita este cálculo
    de ionização, a *[Dimorphite-DL](https://durrantlab.github.io/dimorphite_dl/)*,
    alerta para dificuldades com aminas terciárias e com
    os heterociclos indol e pirrol.
    """
)


with st.container(border=True):

    smiles = kekule_editor(
        key='key_kekule_editor',
    )

    if not smiles:
        st.stop()
    try:
        validate_smiles(smiles)
    except Exception as exc:
        st.error("Falha ao validar o SMILES")
        st.stop()


@st.fragment
def main_area():
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
        xaxis=dict(visible=True, showgrid=True, zeroline=False, fixedrange=True, ),
        yaxis=dict(visible=False, showgrid=False, zeroline=False, fixedrange=True),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=100,
        xaxis_title=None,
        hoverlabel=dict(font_size=16, font_family="sans-serif"),
    )

    event = st.plotly_chart(
        fig,
        key='key_ph_bar_type_b',
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