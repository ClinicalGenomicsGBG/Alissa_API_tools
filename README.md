# Alissa_upload

We want to automatize again the uploads of VCFs to Alissa in WOPR. For this we have received a series of scripts from Agilent support. We need to integrate this to WOPR and to add a step of splitting VCFs into two smaller files as the size of the final VCFs is larger than what can be uploaded to Alissa via the API. Moreover the scripts from Agilent were written a version of Python that is higher than the one currently used in WOPR.

The goal of this repository is to test Alissa upload. Once it is running properly, this will be integrated to WOPR.

## Requirements

The scripts in this repository should run in the same environment like WOPR. I made a clone of the `wopr` environment for developing and testing purposes. To that environment we added environment variables for Alissa (username, password and url) by modifying the file `/apps/bio/software/anaconda2/envs/wopr_alissa/etc/conda/activate.d/env_vars.sh`. The file `/apps/bio/software/anaconda2/envs/wopr_alissa/etc/conda/deactivate.d/env_vars.sh` was also modified.

To activate this new environment:

```
module load anaconda2
source activate wopr_alissa
```
