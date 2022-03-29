# Alissa API tools

This repository contains tools to interact with Alissa API, for example to create a patient, load a data file (VCF) or create a lab result (see `cgg.py`). It also contains a program to split a VCF into smaller VCF (`chunk_vcf.py`); this is necessary to upload VCF larger than circa 240 MiB to the Alissa API (the files need to be smaller than 240 MiB).

The code to interact with the API is partially based on code that we received from Agilent support and that is stored in the feature branch "agilent_scripts_backup".

The two main programs, `cgg.py` and `chunk_vcf.py` can be used as standalone scripts. They will also be integrated in WOPR. It is possible to use the classes and functions in `cgg.py` to do only some of the actions, e.g. creation of a patient.

Caution! The current active feature branch is "refactor_chunk_vcf".

## Requirements

The scripts in this repository should run in the same environment like WOPR. I made a clone of the `wopr` environment for developing and testing purposes. To that environment we added environment variables for Alissa (username, password and url) by modifying the file `/apps/bio/software/anaconda2/envs/wopr_alissa/etc/conda/activate.d/env_vars.sh`. The file `/apps/bio/software/anaconda2/envs/wopr_alissa/etc/conda/deactivate.d/env_vars.sh` was also modified. Currently the interaction is with the Alissa test instance.

To activate this new environment:

```
module load anaconda2
source activate wopr_alissa
```

## Test the code

You can see which parameters are necessary to run the programs with:

```
python cgg.py --help #API tools, currently does patient creation, data file upload, and lab result creation
python chunk_vcf.py --help #Create chunks of VCF file
```

## Which Alissa instance should one use?

We have two Alissa instances: one for testing and one for production. The credentials for both are included in the conda environment. If one wants to use the test instance, the following line should be included in `cgg.py`:

```
import passwords_test_instance as passwords
```

To use the production instance, replace the line by: 
```
import passwords as passwords
```
