import { Kekule } from 'kekule';
import 'kekule/theme/default';


const COMPOSER_WIDGETS = new WeakMap();

const KekuleEditor = (component) => {

    const { data, parentElement, setTriggerValue } = component;

    let composer = COMPOSER_WIDGETS.get(parentElement.firstChild);
    if (composer)
        return;

    composer = new Kekule.Editor.Composer(parentElement.firstChild);
    COMPOSER_WIDGETS.set(parentElement.firstChild, composer);

    let lastSmiles = null;
    composer.on('operChange', function (evt) {
        const mols = composer.exportObjs(Kekule.Molecule);
        const smiles = Kekule.IO.saveFormatData(mols[0], 'smi');
        if (smiles != lastSmiles) {
            setTriggerValue('smiles', smiles);
            lastSmiles = smiles;
        }
    });
}

export default KekuleEditor;
