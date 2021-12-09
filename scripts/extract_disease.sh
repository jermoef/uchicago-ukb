#!/bin/bash

#PBS -N ukb_pheno
#PBS -S /bin/bash
#PBS -l walltime=01:00:00
#PBS -l mem=2gb
#PBS -o $HOME/pheno.out
#PBS -e $HOME/pheno.err

SCRIPT_PATH="uchicago-ukb/extract_pheno.py"
OUT_DIR="/gpfs/data/ukb-share/dahl/jerome/extracted_phenotypes"
rows=50000

# phenotypes
python3 $SCRIPT_PATH 20002-0.0 20002-0.1 20002-0.2 20002-0.3 20002-0.4 20002-0.5 20002-0.6 20002-0.7 20002-0.8 20002-0.9 20002-0.10 20002-0.11 20002-0.12 20002-0.13 20002-0.14 20002-0.15 20002-0.16 20002-0.17 20002-0.18 20002-0.19 20002-0.20 20002-0.21 20002-0.22 20002-0.23 20002-0.24 20002-0.25 20002-0.26 20002-0.27 20002-0.28 20002-0.29 20002-0.30 20002-0.31 20002-0.32 20002-0.33 -n 20002selfreport -r $rows -t $OUT_DIR

python3 $SCRIPT_PATH 41202-0.0 41202-0.1 41202-0.2 41202-0.3 41202-0.4 41202-0.5 41202-0.6 41202-0.7 41202-0.8 41202-0.9 41202-0.10 41202-0.11 41202-0.12 41202-0.13 41202-0.14 41202-0.15 41202-0.16 41202-0.17 41202-0.18 41202-0.19 41202-0.20 41202-0.21 41202-0.22 41202-0.23 41202-0.24 41202-0.25 41202-0.26 41202-0.27 41202-0.28 41202-0.29 41202-0.30 41202-0.31 41202-0.32 41202-0.33 41202-0.34 41202-0.35 41202-0.36 41202-0.37 41202-0.38 41202-0.39 41202-0.40 41202-0.41 41202-0.42 41202-0.43 41202-0.44 41202-0.45 41202-0.46 41202-0.47 41202-0.48 41202-0.49 41202-0.50 41202-0.51 41202-0.52 41202-0.53 41202-0.54 41202-0.55 41202-0.56 41202-0.57 41202-0.58 41202-0.59 41202-0.60 41202-0.61 41202-0.62 41202-0.63 41202-0.64 41202-0.65 -n 41202ICD -r $rows -t $OUT_DIR