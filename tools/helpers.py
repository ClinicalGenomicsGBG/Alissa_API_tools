import logging
from .classes import cggPatient, cggVCF, cggLabResult

def create_patient(token, bench_url, accession, sex, alissa_folder):
    """Create a patient in Alissa (unless the patient already exists, in which case a message is returned). Return the internal patient id."""
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
    """Create a datafile in Alissa (unless the data file already exists). Return the internal datafile id."""
    vcf = cggVCF(token, bench_url, path)
    data_file = vcf.get_data_file_by_name()
    if len(data_file) == 0:
        data_file_id = vcf.post_vcf_to_alissa()
    else:
        print('A VCF file with the same name already exists. Not attempting to upload it again.')
        data_file_id = data_file[0]['id']
    print(f'The data file ID is: {data_file_id}.')
    return(data_file_id)

def create_lab_result(token, bench_url, patient_id, datafile_id, name_in_vcf):
    """Create a lab result in Alissa (unless the lab result already exists)."""
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
            print(f'The lab result for patient {patient_id} and data file {datafile_id} already exists: {labresult_id}. Skipping creating a new one.')
        else:
            labresult_id = labresult.link_vcf_to_patient()
            print(f'The lab result ID for patient {patient_id} and data file {datafile_id} is: {labresult_id}.')
    else:
        labresult_id = labresult.link_vcf_to_patient()
        print(f'The lab result ID for patient {patient_id} and data file {datafile_id} is: {labresult_id}.')
    return labresult_id

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