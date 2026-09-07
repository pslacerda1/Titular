import numpy as np
import polars as pl
import plotly.express as px
import streamlit as st

from titular.logic import titurate, smiles_to_svg, validate_smiles


st.title("Olá, estudante! 👋")
st.markdown(
    """
    Bem vindo ao Titular.

    Aqui você pode avaliar a formação de microestados
    decorrentes da protonação/desprotonação de sítios
    ionizáveis presentes em moléculas quaisquer.

    No entanto, a ferramenta que possibilita este cálculo
    de ionização, a ***Dimorphite-DL***, alerta para
    dificuldades com aminas terciárias e com os heterociclos
    indóis e pirróis.
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

    try:
        validate_smiles(input_smiles)
    except Exception as exc:
        st.error("Falha ao validar o SMILES")
        st.stop()

    smiles_dict = titurate(input_smiles)
    ph_list = list(smiles_dict.keys())


    #
    # Barra de pH
    #

    segment_list = []
    begin_list = []
    end_list = []
    name_list = []

    for i, ph in enumerate(range(len(ph_list) - 1)):
        begin = ph_list[i]
        end = ph_list[i+1]

        line_segment = np.linspace(begin, end-0.1)

        name = f"[{begin:.1f},{end:.1f}"
        if end >= 14.0:
            name += "]"
        else:
            name += ")"

        segment_list.extend(line_segment)
        begin_list.extend([begin] * len(line_segment))
        end_list.extend([end] * len(line_segment))
        name_list.extend([name] * len(line_segment))

    if end < 14.0:
        begin = end - 0.1
        end = 14.0
        line_segment = np.linspace(begin, end)
        end = 14.0
        name = f"[{begin:.1f},{end:.1f}]"

        segment_list.extend(line_segment)
        begin_list.extend([begin] * len(line_segment))
        end_list.extend([end] * len(line_segment))
        name_list.extend([name] * len(line_segment))

    df = pl.DataFrame({
        'x': segment_list,
        'zero': [0] * len(segment_list),
        'pH': name_list,
        'begin': begin_list,
        'end': end_list,
    })
    fig = px.line(
        df,
        x='x', y='zero', color='pH',
        markers=True,
        hover_data={
            'pH': True,
            'x': False,
            'zero': False
        },
        custom_data=['begin', 'end']
    )
    fig.update_traces(line=dict(width=40))
    fig.update_layout(
        xaxis=dict(visible=True, showgrid=True, zeroline=False, fixedrange=True, ),
        yaxis=dict(visible=False, showgrid=False, zeroline=False, fixedrange=True),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=100,
        xaxis_title=None,
        hoverlabel=dict(font_size=16, font_family="sans-serif")
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
    clicked_ph = points[0]['x']
    begin, end, ph_range = points[0]['customdata']
    for ph_ref, smiles_set in smiles_dict.items():
        if begin <= ph_ref < end:
            st.header(f"pH ∈ {ph_range}")
            for i in range(max(len(smiles_set) // 3, 1)):
                for column in st.columns(3):
                    with column:
                        if smiles_set:
                            smiles = smiles_set.pop()
                            st.text(smiles)
                            st.image(smiles_to_svg(smiles))