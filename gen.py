#!/usr/bin/env python3
"""Generate DFT input files from CIF + config YAML."""
import argparse
import os
from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit("pip install pyyaml")

try:
    from ase.io import read
except ImportError:
    raise SystemExit("pip install ase")


QE_TEMPLATE = """&CONTROL
  calculation = 'scf',
  restart_mode = 'from_scratch',
  prefix = '{prefix}',
  outdir = './tmp/',
  pseudo_dir = '{pseudo_dir}',
  verbosity = 'high',
/
&SYSTEM
  ibrav = 0,
  nat = {nat},
  ntyp = {ntyp},
  ecutwfc = {ecut},
  occupations = 'smearing',
  smearing = '{smearing}',
  degauss = {degauss},
/
&ELECTRONS
  conv_thr = 1.0d-8,
  mixing_beta = 0.4,
/
CELL_PARAMETERS angstrom
{cell}
ATOMIC_SPECIES
{species}
ATOMIC_POSITIONS angstrom
{positions}
K_POINTS automatic
{kpts} 0 0 0
"""


def write_qe(atoms, cfg, outdir):
    species_lines = []
    pseudo_dir = cfg.get("pseudo_dir", "$PSEUDO_DIR")
    for sym in set(atoms.get_chemical_symbols()):
        species_lines.append(f"  {sym}  {atoms.get_masses()[atoms.get_chemical_symbols().index(sym)]:.4f}  {sym}.pbe-n-kjpaw.UPF")
    cell = "\n".join("  " + "  ".join(f"{v:.8f}" for v in row) for row in atoms.cell)
    pos = "\n".join(f"  {s}  " + "  ".join(f"{v:.8f}" for v in p)
                    for s, p in zip(atoms.get_chemical_symbols(), atoms.positions))
    kpts = " ".join(str(k) for k in cfg.get("kpoints", [4, 4, 4]))
    content = QE_TEMPLATE.format(
        prefix=cfg.get("jobname", "job"),
        pseudo_dir=pseudo_dir,
        nat=len(atoms),
        ntyp=len(set(atoms.get_chemical_symbols())),
        ecut=cfg.get("ecut", 60),
        smearing=cfg.get("smearing", "gaussian"),
        degauss=cfg.get("smearing_width", 0.01),
        cell=cell,
        species="\n".join(species_lines),
        positions=pos,
        kpts=kpts,
    )
    path = Path(outdir) / "scf.in"
    path.write_text(content)
    return path


def write_vasp(atoms, cfg, outdir):
    # Minimal POSCAR + INCAR + KPOINTS
    from ase.io import write as ase_write
    ase_write(Path(outdir) / "POSCAR", atoms, format="vasp", direct=True)
    incar = [
        f"SYSTEM = {cfg.get('jobname','job')}",
        f"ENCUT = {cfg.get('ecut', 500)}",
        f"GGA = {cfg.get('functional', 'PE')}",
        "ISMEAR = 0",
        f"SIGMA = {cfg.get('smearing_width', 0.05)}",
        "PREC = Accurate",
        "EDIFF = 1e-6",
    ]
    (Path(outdir) / "INCAR").write_text("\n".join(incar) + "\n")
    kp = cfg.get("kpoints", [4, 4, 4])
    kpoints = f"Auto\n0\nGamma\n{kp[0]} {kp[1]} {kp[2]}\n0 0 0\n"
    (Path(outdir) / "KPOINTS").write_text(kpoints)
    return Path(outdir)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cif", required=True)
    ap.add_argument("--code", choices=["qe", "vasp"], required=True)
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    atoms = read(args.cif)
    with open(args.config) as f:
        cfg = yaml.safe_load(f)

    stem = Path(args.cif).stem
    outdir = Path("out") / f"{stem}_{args.code}_{cfg.get('jobname','job')}"
    outdir.mkdir(parents=True, exist_ok=True)

    if args.code == "qe":
        out = write_qe(atoms, cfg, outdir)
    else:
        out = write_vasp(atoms, cfg, outdir)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
