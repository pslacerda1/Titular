import numpy as np
import polars as pl
import plotly.express as px
import streamlit as st

from titular.logic import titurate_a, smiles_to_svg, validate_smiles


st.title("Olá, estudante! 👋")
st.markdown(
    """
    Bem vindo ao Titular.

    Aqui você pode avaliar a formação de microestados
    decorrentes da protonação/desprotonação de sítios
    ionizáveis presentes em moléculas quaisquer.

    No entanto, a ferramenta que possibilita este cálculo
    de ionização, a ***[Dimorphite-DL](https://durrantlab.github.io/dimorphite_dl/)***,
    alerta para dificuldades com aminas terciárias e com
    os heterociclos indóis e pirróis.
    """
)

with st.container(border=True):
    #
    # Área de digitação de molécula
    #
    input_smiles = st.text_input(
        "Molécula SMILES:",
        persist_state='page',
        key='key_smiles',
        value="N[C@@H](Cc1c[nH]cn1)C(=O)O",
    )

    #
    # Opção por tipo de gráfico
    #
    chart_option = st.selectbox(
        "Gráfico:",
        ['Tipo A', 'Tipo B']
    )
    try:
        validate_smiles(input_smiles)
    except Exception as exc:
        st.error("Falha ao validar o SMILES")
        st.stop()

if chart_option == 'Tipo A':
    df = titurate_a(input_smiles)
    df_plot = (
        df
        .with_columns(
            zero = pl.lit(0),
            ph = pl.struct(['begin', 'end'])
                .map_elements(
                    lambda row: np.linspace(row['begin'], row['end']),
                    return_dtype=pl.List(pl.Float64),
                    returns_scalar=True,
                )
        )
        .explode('ph')
        .rename({
            'ph': 'x',
            'label': 'pH',
        })
    )

    #
    # Barra de pH
    #

    fig = px.line(
        df_plot,
        x='x', y='zero', color='pH',
        markers=True,
        custom_data=['pH', 'begin', 'end']
    )
    fig.update_traces(
        line=dict(width=40),
        hovertemplate=(
            "pH ∈ %{customdata[0]}"
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


    st.text("Barra de Titulação:")
    event = st.plotly_chart(
        fig,
        key='key_ph_bar',
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
        label, begin, end = points[0]['customdata']

        smiles_set = (
            df
            .filter(
                pl.col('begin') == begin,
                pl.col('end') == end
            )
            .get_column('smiles')
            .first()
        )

        st.header(f"pH ∈ {label}")
        for column in st.columns(len(smiles_set)):
            with column:
                smiles = smiles_set.pop()
                st.text(smiles)
                st.image(smiles_to_svg(smiles))

elif chart_option == 'Tipo B':
    pass