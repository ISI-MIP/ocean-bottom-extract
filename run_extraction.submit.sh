#!/bin/bash

OVERWRITE="-O" # or:
#OVERWRITE=""

# all ISIMIP3b tier 1 models with MGC module
GCMS="UKESM1-0-LL MPI-ESM1-2-HR GFDL-ESM4 IPSL-CM6A-LR"
EXPS="piControl historical ssp126 ssp370 ssp585"
VARS="o2 ph so thetao"

# single combination
#GCMS="UKESM1-0-LL"
#EXPS="piControl"
#VARS="ph"

for GCM in $GCMS;do
  for EXP in $EXPS;do
    for VAR in $VARS;do
      # since GFDL did not deliver tob, we ectract ocean bottom temperatures from thetao
      [ $GCM != "GFDL-ESM4" ] && [ $VAR == "thetao" ] && continue
      echo "submitting $GCM $EXP $VAR"

      sed \
        -e "s/_GCM_/$GCM/g" \
        -e "s/_EXP_/$EXP/g" \
        -e "s/_VAR_/$VAR/g" \
	-e "s/_OVERWRITE_/$OVERWRITE/g" \
        run_extraction.sh > \
        run_extraction.sh.job
      
      sbatch run_extraction.sh.job && rm run_extraction.sh.job
      #exit
    done
  done
done
