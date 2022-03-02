#Usage: python3 chunk_vcf.py /path/to/input/file.vcf.gz /path/to/output/folder
#Example: python3 chunk_vcf.py /home/xbregw/Alissa_upload/VCFs/NA24143_191108_AHVWHGDSXX_SNV_CNV_germline.vcf.gz /home/xbregw/Alissa_upload/VCFs/chunks
#TODO Use e.g. /tmp on working node as the output folder
#TODO package all/most of the logic into a class and make it non-Alissa specific to allow for reuse.

import sys
import os
import subprocess

class FileInfo:
    """Create object with basic information to be used in VCF upload to Alissa via the API."""
    def __init__(self,originalPath,originalName):
        self.originalPath = originalPath
        self.originalName = originalName

args = sys.argv
path_to_original_vcf = str(args[1]).strip()
output_folder = str(args[2]).strip()

original_name = os.path.basename(path_to_original_vcf)
#original_size = os.path.getsize(path_to_original_vcf)
original_folder = os.path.dirname(path_to_original_vcf)

def vcf_larger_than(vcf,size):
    """Return True if the size of the VCF is larger than a given size."""
    vcf_size = os.path.getsize(vcf)
    return bool(vcf_size > size)

def bgzip(vcf,outfolder):
    """Bgzip a VCF."""
    basename = os.path.basename(vcf)
    bgzipped_vcf = os.path.join(outfolder, basename + ".gz")
    command_bgzip = ["bcftools", "view", "--output-type", "z", "--output", bgzipped_vcf, vcf]
    subprocess.run(command_bgzip)
    return bgzipped_vcf

def index(vcf):
    """Index a bgzipped VCF if the index cannot be found."""
    command_index = ["bcftools", "index", vcf]
    if os.path.isfile(os.path.join(vcf+".csi")):
        print('Index exists already, skipping indexing.')
    else:
        subprocess.run(command_index)
    #TODO what should the function return?

def split(vcf):
    """Split a VCF into two based on pre-defined sets of contigs."""
    basename = vcf.replace('vcf.gz','')
    vcf1 = os.path.join(basename+"_chr1-8.vcf.gz")
    vcf2 = os.path.join(basename+"_chr9-hs37d5.vcf.gz")

    #Split the VCF.
    command_split_vcf1 = ["bcftools", "view", "--output-type", "z", "--output", vcf1, "-r", "1,2,3,4,5,6,7,8", vcf]
    command_split_vcf2 = ["bcftools", "view", "--output-type", "z", "--output", vcf2, "-r", "9,10,11,12,13,14,15,16,17,18,19,20,21,22,X,Y,MT,GL000207.1,GL000226.1,GL000229.1,GL000231.1,GL000210.1,GL000239.1,GL000235.1,GL000201.1,GL000247.1,GL000245.1,GL000197.1,GL000203.1,GL000246.1,GL000249.1,GL000196.1,GL000248.1,GL000244.1,GL000238.1,GL000202.1,GL000234.1,GL000232.1,GL000206.1,GL000240.1,GL000236.1,GL000241.1,GL000243.1,GL000242.1,GL000230.1,GL000237.1,GL000233.1,GL000204.1,GL000198.1,GL000208.1,GL000191.1,GL000227.1,GL000228.1,GL000214.1,GL000221.1,GL000209.1,GL000218.1,GL000220.1,GL000213.1,GL000211.1,GL000199.1,GL000217.1,GL000216.1,GL000215.1,GL000205.1,GL000219.1,GL000224.1,GL000223.1,GL000195.1,GL000212.1,GL000222.1,GL000200.1,GL000193.1,GL000194.1,GL000225.1,GL000192.1,NC_007605,hs37d5", vcf]

    if os.path.isfile(vcf1):
        print(f'File {vcf1} already exists, moving on.')
    else:
        subprocess.run(command_split_vcf1)

    if os.path.isfile(vcf2):
        print(f'File {vcf2} already exists, moving on.')
    else:
        subprocess.run(command_split_vcf2)


#TODO possibly later: instead of raising an exception, exit the process.
if not vcf_larger_than(path_to_original_vcf,0):
    raise Exception(f'Please check this file: {path_to_original_vcf}, the size is 0.')

elif vcf_larger_than(path_to_original_vcf,240_000_000):
    print("The file is larger than 240 MiB and needs to be splitted into smaller VCFs.")

    #Identify  whether the file is gzipped. If no, it first needs to be compressed.
    if original_name.endswith('vcf.gz'):
        basename = original_name.replace('.vcf.gz','')
        vcf_to_index = path_to_original_vcf

    elif original_name.endswith('vcf'):
        vcf_to_index = bgzip(path_to_original_vcf,output_folder)
        print(vcf_to_index)   
        #TODO if I want the rest to work: define basename. But I spend a lot of time in this script defining names, so perhaps there is a better way!
 
    else:
        raise Exception('The input file should be a VCF (gzipped or not).')

    #Index the VCF.
    command_index = ["bcftools", "index", vcf_to_index]
    if os.path.isfile(os.path.join(vcf_to_index+".csi")):
        print('Index exists already, skipping indexing step.')
    else:
        subprocess.run(command_index)

    vcf1 = os.path.join(output_folder,basename+"_chr1-8.vcf.gz")
    vcf2 = os.path.join(output_folder,basename+"_chr9-hs37d5.vcf.gz")

    #Split the VCF.
    command_split_vcf1 = ["bcftools", "view", "--output-type", "z", "--output", vcf1, "-r", "1,2,3,4,5,6,7,8", vcf_to_index]
    command_split_vcf2 = ["bcftools", "view", "--output-type", "z", "--output", vcf2, "-r", "9,10,11,12,13,14,15,16,17,18,19,20,21,22,X,Y,MT,GL000207.1,GL000226.1,GL000229.1,GL000231.1,GL000210.1,GL000239.1,GL000235.1,GL000201.1,GL000247.1,GL000245.1,GL000197.1,GL000203.1,GL000246.1,GL000249.1,GL000196.1,GL000248.1,GL000244.1,GL000238.1,GL000202.1,GL000234.1,GL000232.1,GL000206.1,GL000240.1,GL000236.1,GL000241.1,GL000243.1,GL000242.1,GL000230.1,GL000237.1,GL000233.1,GL000204.1,GL000198.1,GL000208.1,GL000191.1,GL000227.1,GL000228.1,GL000214.1,GL000221.1,GL000209.1,GL000218.1,GL000220.1,GL000213.1,GL000211.1,GL000199.1,GL000217.1,GL000216.1,GL000215.1,GL000205.1,GL000219.1,GL000224.1,GL000223.1,GL000195.1,GL000212.1,GL000222.1,GL000200.1,GL000193.1,GL000194.1,GL000225.1,GL000192.1,NC_007605,hs37d5", vcf_to_index]

    if os.path.isfile(vcf1):
        print(f'File {vcf1} already exists, moving on.')
    else:
        subprocess.run(command_split_vcf1)

    if os.path.isfile(vcf2):
        print(f'File {vcf2} already exists, moving on.')
    else:
        subprocess.run(command_split_vcf2)

    #Check the size after splitting.
    # At the moment, manual intervention will be needed if the new files are still larger than the limit (e.g. to decide how to split the VCFs).
    if vcf_larger_than(vcf1,240_000_000) or vcf_larger_than(vcf2,240_000_000):
        raise Exception(f'One of the files is still larger than 240 MiB. Investigate. Files to control: {vcf1} and {vcf2}.')
    else:
        VCF1 = FileInfo(vcf1,os.path.basename(vcf1))
        VCF2 = FileInfo(vcf2,os.path.basename(vcf2))
    
else:
    VCF = FileInfo(path_to_original_vcf, original_name)

