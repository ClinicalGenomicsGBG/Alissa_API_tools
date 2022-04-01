# Alissa API tools

This repository contains tools to interact with Alissa API, for example to create a patient, load a data file (VCF) or create a lab result (see `alissa_API_tools.py`). It also contains a program to split a VCF into smaller VCF (`chunk_vcf.py`); this is necessary to upload VCF larger than circa 240 MiB to the Alissa API (the files need to be smaller than 240 MiB).

The code to interact with the API is partially based on code that we received from Agilent support and that is stored in the feature branch "agilent_scripts_backup".

The two main programs, `alissa_API_tools.py` and `chunk_vcf.py` can be used as standalone scripts. They will also be integrated in WOPR. It is possible to use the classes and functions in `alissa_API_tools.py` to do only some of the actions, e.g. creation of a patient.

## Requirements

The scripts in this repository should run in the same environment like WOPR. I made a clone of the `wopr` environment for developing and testing purposes. To that environment we added environment variables for Alissa (username, password and urls, for the production and the test instances) by modifying the file `/apps/bio/software/anaconda2/envs/wopr_alissa/etc/conda/activate.d/env_vars.sh`. The file `/apps/bio/software/anaconda2/envs/wopr_alissa/etc/conda/deactivate.d/env_vars.sh` was also modified.

To activate this new environment:

```
module load anaconda2
source activate wopr_alissa
```

## Test the code

You can see which parameters are necessary to run the programs with:

```
python alissa_API_tools.py --help #API tools, currently does patient creation, data file upload, and lab result creation
python chunk_vcf.py --help #Create chunks of VCF file
```

## Which Alissa instance should one use?

We have two Alissa instances: one for testing and one for production. The credentials for both are included in the conda environment. Currently the default in `alissa_API_tools.py` is to use the test instance. If one wants to use the production instance, include the flag `--production-instance`.
