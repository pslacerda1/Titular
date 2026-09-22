import base64
import itertools
import numpy as np
import polars as pl
from ordered_set import OrderedSet
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem.MolStandardize import rdMolStandardize
from rdkit.Chem import Crippen
from dimorphite_dl import protonate_smiles
import numpy as np


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

    pka_list = []
    logp_list = []
    smi2img = {}

    for smi, spans_set in new_curve.items():
        begin, end = spans_set.pop()
        pka_list.append((begin + end) / 2)
        mol = Chem.MolFromSmiles(smi)
        logp = Crippen.MolLogP(mol)
        logp_list.append(logp)
        smi2img[smi] = svg_to_imgdata(smiles_to_svg(smi))

    alphas = calculate_polyprotic_fractions(pka_list, ph_list)
    num_species, num_ph = alphas.shape

    df = pl.DataFrame({
        'ph': np.tile(ph_list, num_species),
        'pKa': np.repeat(list(pka_list), num_ph),
        'logP': np.repeat(list(logp_list), num_ph),
        'smiles': np.repeat(list(smi2img.keys()), num_ph),
        'image': np.repeat(list(smi2img.values()), num_ph),
        'alpha': np.array(alphas).flatten().tolist(),
    })
    return df


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


def calculate_polyprotic_fractions(pKa_list, ph_range):
    """
    Calculates the fractional distribution (alpha) of species for a polyprotic system.

    Parameters:
        pKa_list (list): List of pKa values sorted in ascending order.
        ph_range (array): NumPy array of pH values to evaluate.

    Returns:
        alphas (list of arrays): List containing the fraction (0.0 to 1.0) for each species.
    """
    # Convert pKa to Ka values
    Ka = [10**(-pka) for pka in pKa_list]
    N = len(Ka)  # Number of protonation steps

    # Calculate [H+] for each pH value
    h = 10**(-ph_range)

    # Pre-allocate array for all terms in the denominator
    # Term 0: [H+]^N
    # Term 1: K1 * [H+]^(N-1)
    # Term 2: K1 * K2 * [H+]^(N-2) ... etc.
    terms = []

    # Intermediate product accumulator for Ka values (K1, K1*K2, K1*K2*K3...)
    ka_product = 1.0
    for i in range(0, N):
        ka_product *= Ka[i-1]
        terms.append(ka_product * (h**(N - i)))

    # Convert list of terms into a 2D numpy array for easy operations
    terms = np.array(terms)

    # The denominator D is the sum of all terms at each pH point
    D = np.sum(terms, axis=0)

    # Each alpha fraction is its respective term divided by D
    alphas = [term / D for term in terms]
    return np.array(alphas)
