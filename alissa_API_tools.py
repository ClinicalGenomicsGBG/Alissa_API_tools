#This script imports functions and classes and uses them to perform the essential steps of the interaction with the Alissa API: obtain an 
# authentification token; create a patient; split a VCF if it larger than a given size; load a VCF file; and link a patient and a VCF 
# (creating a "lab result").
# Usage (to print the help message): module load anaconda2/4.1.0; source activate wopr_alissa; python Alissa_API_tools.python --help

import chunk_vcf
import click
import os

from tools.classes import OAuth2Client
from tools.helpers import create_patient, create_datafile, create_lab_result, \
    setup_logger, get_alissa_credentials

#TODO think about the order of the arguments! E.g. put first all the arguments that have no default.
@click.command()
@click.option('-a', '--accession', required=True,
             help='Patient accession number')
@click.option('-s', '--sex', default='UNKNOWN', type=click.Choice(['FEMALE', 'MALE', 'UNKNOWN']),
             help='Sex of the sample')
@click.option('-f', '--alissa_folder', default='Default',
             type=click.Choice(['BCF demo', 'CRC pipeline validation', 'CRE2 Reference set files', 'Default', 'ExomeValidation', 'Klinisk Genetik', 'Klinisk Genetik - Forskning', 'Klinisk kemi', 'Validation WGS']),
             help='Patient folder in Alissa, for example "Klinisk kemi" or "Klinisk Genetik"')
@click.option('-v', '--vcf_path', required=True, type=click.Path(exists=True),
              help='Path to input VCF file')
@click.option('-o', '--output_folder', default='/tmp',
              help='Path to a folder where the VCF will be written if the input VCF is larger than the size argument. In that case, files will be loaded to Alissa from that folder')
@click.option('-s', '--size', required=True, type=int,
              help='Size in bp. If the VCF exceed this size, it will be split into 2, 3 or 4 VCFs')
@click.option('-n', '--name_in_vcf', required=True,
             help='Sample ID in the VCF header row')
@click.option('-i', '--production-instance', type=click.Choice(['production', 'test']) , default="test",
             help='What Alissa instance should be used. Production or test.') #TODO invert the logic once testing is finished.
@click.option('--logpath', help='Path to log file to which logging is performed.')
def main(accession, sex, alissa_folder, vcf_path, output_folder, size, name_in_vcf, production_instance, logpath):
    ## Set up the logfile and start logging
    logger = setup_logger('alissa_upload', logpath)

    ## Get the credentials set up
    logger.info(f'Starting upload of {os.path.basename(vcf_path)} to Alissa {production_instance} instance.')
    token_url, bench_url, username, password = get_alissa_credentials(production_instance)

    try:
        oauth2_client = OAuth2Client(username, password, token_url)
        token = oauth2_client.fetch_token()
    except:
        logger.error(f'Was not able to generate an API token.')
        raise PermissionError

    ## Create the patient. If the patient already exists in Alissa, fetch the internal ID.
    logger.info(f'Starting creation of patient {accession} in Alissa.')	
    patient_id, patient_exists = create_patient(token, bench_url, accession, sex, alissa_folder)
    if patient_exists == True:
        logger.info(f'A patient already exists with patient ID: {patient_id}')
    else:
        logger.info(f'A patient has been created with patient ID: {patient_id}')

    ## Prepare the VCF for upload. If the VCF is larger than the limit for Alissa API: split it.
    logger.info(f'Prepare the VCF(s) for upload to Alissa.')
    vcfs = chunk_vcf.prepare_and_split_vcf(vcf_path, output_folder, size, logpath)
    
    for path in vcfs:
        ## Upload the VCF to Alissa. If a datafile with the same name already exists in Alissa, fetch the internal ID.
        logger.info(f'Starting upload of VCF to Alissa.')
        datafile_id, datafile_exists = create_datafile(token, bench_url, path)
        if datafile_exists == True:
            logger.info(f'A datafile already exists with datafile ID: {datafile_id}. If you want to replace with a datafile with the same name, you need to delete it from Alissa.')
        else:
            logger.info(f'A datafile has been created with datafile ID: {datafile_id}')

        ## Create the lab result in Alissa.
        logger.info(f'Starting creation of lab result.')
        labresult_id, labresult_exists = create_lab_result(token, bench_url,  patient_id, datafile_id, name_in_vcf)
        if labresult_exists == True:
            logger.info(f'A lab result already exists with lab result ID: {labresult_id}')
        else:
            logger.info(f'A lab result has been created with lab result ID: {labresult_id}')

   
if __name__ == '__main__':
    main()
