# Alissa_upload

We want to automatize again the uploads of VCFs to Alissa in WOPR. For this we have received a series of scripts from Agilent support. We need to integrate this to WOPR and to add a step of splitting VCFs into two smaller files as the size of the final VCFs is larger than what can be uploaded to Alissa via the API. Moreover the scripts from Agilent were written a version of Python that is higher than the one currently used in WOPR.

The goal of this repository is to test Alissa upload. Once it is running properly, this will be integrated to WOPR.

## Requirements

The scripts in this repository should run in the same environment like WOPR. To that environment we added environment variables for Alissa (username, password and url).

```
module load anaconda2
source activate wopr
```

For testing purposes, I created a clone of the WOPR conda environment that comprises additional environmental variables (done as sudo).

```
sudo su
module load anaconda2
conda create --name wopr_alissa --clone wopr
source activate wopr_alissa
python
import os
os.environ['ALISSA_USERNAME'] = 'xx' #replace xx by username
os.environ['ALISSA_PASSWORD'] = 'xx' #replace xx by password
os.environ['ALISSA_TOKEN_URL'] = 'xx' #replace xx by url
```
