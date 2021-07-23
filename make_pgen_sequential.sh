#!/bin/bash

#PBS -N bgen2pgen
#PBS -S /bin/bash
#PBS -l walltime=36:00:00
#PBS -l nodes=1:ppn=28
#PBS -l mem=16gb
#PBS -o $HOME/plink_pgen.out
#PBS -e $HOME/plink_pgen.err


IN_FILE="/gpfs/data/ukb-share/genotypes/v3/ukb_imp_chr${chr_num}_v3.bgen"
SAMPLE_FILE="/gpfs/data/ukb-share/genotypes/ukb19526_imp_chr1_v3_s487395.sample"
OUT_DIR="/scratch/t.cri.jfreudenberg/genotypes/"

module load gcc/6.2.0 parallel/20170122

cd $OUT_DIR

mkdir plink_genotypes

cd plink_genotypes

env_parallel -j 3 ~/plink2 --bgen /gpfs/data/ukb-share/genotypes/v3/ukb_imp_chr{1}_v3.bgen \
	 --sample $SAMPLE_FILE \
	 --export bcf \
	 --out ukb_imp_chr{1}_v3 \
	 --memory 15000 \
	 --threads 9 ::: {1..22}

: > merge.txt
for i in $(seq 1 22); do
    echo 'ukb_imp_chr${i}_v3.bcf' >> merge.txt
done

~/bin/bcftools concat -f merge.txt -o ukb_imp_v3.bcf -O b --threads 27

rm ukb_imp_chr*_v3.bcf
rm merge.txt

~/plink2 --bcf ukb_imp_v3.bcf \
	 --make-pgen \
	 --out ukb_imp_v3 \
	 --memory 15000 \
	 --threads 27

rm ukb_imp_v3.bcf
