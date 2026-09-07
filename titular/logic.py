import numpy as np
import polars as pl
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
) -> dict[float, set[str]]:
    """Titurate a molecule originating protomeric species

    It works by sampling microstates at each pH interval.
    """

    ph_list = np.arange(ph_min, ph_max + precision * 0.5, precision)
    #
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
    return curve


def titurate_a(smi: str):
    """Titurate a molecule but keep only transitions."""

    curve = titurate(smi)

    curve_keys = list(curve)
    new_curve = {}
    for i in range(len(curve)):
        ph_curr = curve_keys[i]
        if i == 0:
            new_curve[ph_curr] = curve[ph_curr]
            continue
        ph_prev = curve_keys[i - 1]
        if curve[ph_curr] != curve[ph_prev]:
            new_curve[ph_curr] = curve[ph_curr]

    begin_list = []
    end_list = []
    label_list = []
    smiles_list = []

    ph_list = list(new_curve.keys())

    for i in range(len(ph_list) - 1):
        begin = ph_list[i]
        end = ph_list[i+1]
        smi = new_curve[begin]

        label = f"[{begin:.1f},{end:.1f}"
        if end >= 14.0:
            label += "]"
        else:
            label += ")"

        begin_list.append(begin)
        end_list.append(end)
        smiles_list.append(smi)
        label_list.append(label)

    if end < 14.0:
        begin = end
        end = 14.0
        smi = new_curve[begin]
        label = f"[{begin:.1f},{end:.1f}]"

        begin_list.append(begin)
        end_list.append(end)
        smiles_list.append(smi)
        label_list.append(label)

    return pl.DataFrame({
        'begin': begin_list,
        'end': end_list,
        'smiles': smiles_list,
        'label': label_list,
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


def validate_smiles(smi: str) -> bool:
    return bool(rdMolStandardize.ValidateSmiles(smi))
