import logging
from .. import passwords
from .classes import cggPatient, cggVCF, cggLabResult

def create_patient(token, bench_url, accession, sex, alissa_folder):
    """Create a patient in Alissa. Return the internal patient ID and a boolean saying whether the patient already existed in Alissa."""
    patient = cggPatient(token, bench_url, accession, alissa_folder, sex)
    if not patient.exists():
        patient_id = patient.create()
        patient_exist = False
    else:
        existing_patient = patient.get_existing_patient()
        patient_id = existing_patient['id']
        patient_exist = True

    return patient_id, patient_exist

def create_datafile(token, bench_url, path):
    """Create a datafile in Alissa (i.e. upload a VCF file). Return the internal datafile ID and a boolean saying whether the datafile already existed in Alissa."""
    vcf = cggVCF(token, bench_url, path)
    data_file = vcf.get_data_file_by_name()
    if len(data_file) == 0:
        data_file_id = vcf.post_vcf_to_alissa()
        data_file_exist = False
    else:
        data_file_id = data_file[0]['id']
        data_file_exist = True

    return data_file_id, data_file_exist

def create_lab_result(token, bench_url, patient_id, datafile_id, name_in_vcf):
    """Create a lab result in Alissa. Return the internal lab result ID and a boolean saying whether the lab result already existed in Alissa."""
    labresult = cggLabResult(token, bench_url, patient_id, datafile_id, name_in_vcf)
    prior_labresult = labresult.get_lab_result()
    if len(prior_labresult) > 0:
        exist_labresult = []
        exist_datafile = []
        for result in prior_labresult:
            exist_labresult.append(result['id'])
            exist_datafile.append(result['dataFileId'])
        if datafile_id in exist_datafile:
            i = exist_datafile.index(datafile_id)
            labresult_id = exist_labresult[i]
            labresult_exist = True
        else:
            labresult_id = labresult.link_vcf_to_patient()
            labresult_exist = False
    else:
        labresult_id = labresult.link_vcf_to_patient()
        labresult_exist = False

    return labresult_id, labresult_exist

def setup_logger(name, log_path=None):
    """Initialise a log file using the logging package"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    stream_handle = logging.StreamHandler()
    stream_handle.setLevel(logging.DEBUG)
    stream_handle.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s'))
    logger.addHandler(stream_handle)

    if log_path:
        file_handle = logging.FileHandler(log_path, 'a')
        file_handle.setLevel(logging.DEBUG)
        file_handle.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s'))
        logger.addHandler(file_handle)

    return logger

def get_alissa_credentials(production_instance):
    if production_instance == 'production':
        token_url = passwords.alissa_prod.token_url
        bench_url = passwords.alissa_prod.bench_url
        username = passwords.alissa_prod.username
        password = passwords.alissa_prod.password

    else:
        token_url = passwords.alissa_test.token_url
        bench_url = passwords.alissa_test.bench_url
        username = passwords.alissa_test.username
        password = passwords.alissa_test.password

    return token_url, bench_url, username, password
