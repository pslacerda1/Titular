import numpy as np
import logging
from base64 import b64encode
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem.MolStandardize import rdMolStandardize
from dimorphite_dl import protonate_smiles, enable_logging


enable_logging(logging.WARNING)


def titurate(
    smi: str,
    ph_min: float = 0.0,
    ph_max: float = 14.0,
    precision: float = 0.1,
) -> dict[float, set[str]]:
    """Titurate a molecule originating protomeric species."""

    ph_list = np.arange(ph_min, ph_max + precision * 0.5, precision)

    # sample microstates at each pH interval
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

    curve_keys = list(curve)

    # keep only transitions
    new_curve = {}
    for i in range(len(curve)):
        ph_curr = curve_keys[i]
        if i == 0:
            new_curve[ph_curr] = curve[ph_curr]
            continue
        ph_prev = curve_keys[i - 1]
        if curve[ph_curr] != curve[ph_prev]:
            new_curve[ph_curr] = curve[ph_curr]

    return new_curve


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