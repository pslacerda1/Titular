import base64
import itertools
import numpy as np
import polars as pl
from ordered_set import OrderedSet
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem.MolStandardize import rdMolStandardize
from dimorphite_dl import protonate_smiles


def titurate(
    smi: str,
    ph_min: float = 0.0,
    ph_max: float = 14.0,
    precision: float = 0.1,
) -> pl.DataFrame:
    """
    Titurate a molecule returning protomeric microstates.

    It works by sampling microstates at each pH interval.
    """

    ph_list = np.arange(ph_min, ph_max + precision * 0.5, precision)

    curve = {}
    for ph in ph_list:
        ph = round(ph, 1)
        smiles_list = protonate_smiles(
            smi,
            ph_min=ph-precision*0.5,
            ph_max=ph+precision*0.5,
            precision=precision,
        )
        curve[ph] = set(smiles_list)

    new_curve: dict[str, set[tuple[float, float]]] = {}
    all_smiles = OrderedSet(itertools.chain.from_iterable(curve.values()))

    for smi in all_smiles:
        begin, end = None, None
        i = 0
        if smi not in new_curve:
            new_curve[smi] = set()
        for ph, smiles_set in curve.items():
            if begin is None and smi in smiles_set:
                begin = ph
            if begin is not None and ((smi not in smiles_set) != (ph == 14.0)):
                end = ph
                if i > 0:
                    raise RuntimeError(f"Unexpected additional range for '{smi}'.")
                new_curve[smi].add((begin, end))
                i += 1
                begin, end = None, None

    smiles_list = []
    begin_list = []
    span_list = []
    label_list = []
    img_list = []

    for smi, spans_set in new_curve.items():
        begin, end = spans_set.pop()
        smiles_list.append(smi)
        begin_list.append(begin)
        span_list.append(end - begin)
        label = f"[{begin:.1f}, {end:.1f}"
        if end >= 14.0:
            label += "]"
        else:
            label += ")"
        label_list.append(label)
        img_list.append(svg_to_imgdata(smiles_to_svg(smi)))

    return pl.DataFrame({
        'smiles': smiles_list,
        'begin': begin_list,
        'span': span_list,
        'label': label_list,
        'img': img_list,
    })


def smiles_to_svg(
    smi: str,
    legend: str = "",
    size: tuple[int, int] = (400, 400)
) -> str:
    """Convert a SMILES to SVG file."""
    mol = Chem.MolFromSmiles(smi)
    AllChem.Compute2DCoords(mol)
    d2d = rdMolDraw2D.MolDraw2DSVG(size[0], size[1])
    d2d.DrawMolecule(mol, legend=legend)
    d2d.FinishDrawing()
    svg = d2d.GetDrawingText()
    return svg


def svg_to_imgdata(svg: str) -> str:
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f'data:image/svg+xml;base64,{b64}'

def validate_smiles(smi: str) -> bool:
    return bool(rdMolStandardize.ValidateSmiles(smi))
