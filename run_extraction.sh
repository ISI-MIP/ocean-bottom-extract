#!/bin/bash

#SBATCH --qos=short
#SBATCH --partition=standard
#SBATCH --account=isimip
#SBATCH --job-name=ISIMIPIO
#SBATCH --time=02:00:00
#SBATCH --output=slurm.logs/extract-bottom._GCM_._EXP_._VAR_.%j.out
#SBATCH --error=slurm.logs/extract-bottom._GCM_._EXP_._VAR_.%j.err

module load anaconda/5.0.0_py3
. /p/system/packages/anaconda/5.0.0_py3/etc/profile.d/conda.sh
conda activate ocean-bottom-env

# debug single combination
#python3 -u extract_bottom_values.py -g UKESM1-0-LL -e piControl -v ph

# invoke from wrapper script
python3 -u extract_bottom_values.py -g _GCM_ -e _EXP_ -v _VAR_
