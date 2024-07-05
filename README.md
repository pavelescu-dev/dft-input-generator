# dft-input-generator

Generate Quantum ESPRESSO and VASP input files from a `.cif` + a YAML config.

Written because I got tired of writing the same boilerplate over and over when
testing a new structure at different k-point grids.

## Usage

```
python gen.py --cif structures/TiO2_rutile.cif --code qe --config configs/scf_basic.yaml
python gen.py --cif structures/TiO2_rutile.cif --code vasp --config configs/relax.yaml
```

Outputs go into `out/<structure>_<code>_<jobname>/`.

## Config format

```yaml
jobname: scf_basic
functional: PBE
ecut: 60
kpoints: [6, 6, 6]
smearing: gaussian
smearing_width: 0.01
```

## Caveats

- Pseudopotentials path expected in `$PSEUDO_DIR` (or override via config).
- VASP path for POTCAR assumes PBE set under `$VASP_PP_PATH`.
- No magnetic collinear/noncol handling yet (TODO).

## References

- [Quantum ESPRESSO input file reference](https://www.quantum-espresso.org/Doc/INPUT_PW.html)
- [VASP wiki - INCAR tags](https://www.vasp.at/wiki/index.php/Category:INCAR)
