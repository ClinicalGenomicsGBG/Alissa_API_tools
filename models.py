from typing import Text

#The class PatientRequest is not used elsewhere (as far as I can see!).
class PatientRequest(object):
    def __init__(self,accession,sex,family_id,comments,sample):
        self.accession = accession
        self.sex = sex
        self.family_id = family_id
        self.comments = comments
        self.sample = sample
    def __str__(self):
        return "{0} {1} {2} {3} {4}".format(self.accession, self.sex, self.family_id,self.comments, self.sample)

class OrderRequest(object):
    def __init__(self,file_path,alissa_file_name,file_type,patient_folder,patient):
        self.file_path = file_path
        self.alissa_file_name = alissa_file_name
        self.file_type = file_type
        self.patient_folder = patient_folder
        self.patient = PatientRequest(**patient)

class FileInfo:
    def __init__(self,originalPath,originalName,currentPath,currentName,originalSize,currentSize):
        self.originalPath = originalPath
        self.originalName = originalName
        self.originalSize = originalSize #not used in Agilent scripts - might be useful for us though (check size and chunk VCF)
        self.currentPath = currentPath #not used in Agilent scripts
        self.currentName = currentName #not used in Agilent scripts
        self.currentSize = currentSize

class Patient:
    def __init__(self,accessionNumber,comments,familyIdentifier,folderName,gender):
        self.accessionNumber = accessionNumber
        self.comments = comments #not used by us
        self.familyIdentifier = familyIdentifier #not used by us
        self.folderName = folderName
        self.gender = gender

class LabResult:
    def __init__(self,dataFileId,sampleIdentifier):
        self.dataFileId = dataFileId
        self.sampleIdentifier = sampleIdentifier

class Response(object):
    def __init__(self,username,status_code,status_message : Text,accession=None,lab_result_id = None):
        self.username = username
        self.status_code = status_code
        self.status_message = status_message
        self.accession = accession
        self.lab_result_id = lab_result_id
        
