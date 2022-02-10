#The main (and perhaps only) argument for this script should be the path to the original VCF file.

import sys
import os
import subprocess

class FileInfo:
    def __init__(self,originalPath,originalName):
        self.originalPath = originalPath
        self.originalName = originalName

args = sys.argv
path_to_original_vcf = str(args[1]).strip()

original_name = os.path.basename(path_to_original_vcf)
original_size = os.path.getsize(path_to_original_vcf)
basename = original_name.replace('.vcf.gz','')
original_folder = os.path.dirname(path_to_original_vcf)

#TODO possibly later: instead of printing error messages, exit the process.
if original_size == 0:
    print(f'Please check this VCF: {path_to_original_vcf}, the size is 0.')

elif original_size >= 250_000_000:
    print("The VCF file needs to be splitted into smaller VCFs.")
    
    #Preliminary step: index the VCF.
    #TODO possibly: add a clause to check whether the index already exists.
    command_index = ["bcftools", "index", path_to_original_vcf]
    subprocess.run(command_index)
    
    vcf1 = original_folder+"/"+basename+"_chr1-8.vcf.gz"
    vcf2 = original_folder+"/"+basename+"_chr9-hs37d5.vcf.gz"

    #Split the VCF.
    command_split_vcf1 = ["bcftools", "view", "--output-type", "z", "--output", vcf1, "-r", "1,2,3,4,5,6,7,8", path_to_original_vcf]
    command_split_vcf2 = ["bcftools", "view", "--output-type", "z", "--output", vcf2, "-r", "9,10,11,12,13,14,15,16,17,18,19,20,21,22,X,Y,MT,GL000207.1,GL000226.1,GL000229.1,GL000231.1,GL000210.1,GL000239.1,GL000235.1,GL000201.1,GL000247.1,GL000245.1,GL000197.1,GL000203.1,GL000246.1,GL000249.1,GL000196.1,GL000248.1,GL000244.1,GL000238.1,GL000202.1,GL000234.1,GL000232.1,GL000206.1,GL000240.1,GL000236.1,GL000241.1,GL000243.1,GL000242.1,GL000230.1,GL000237.1,GL000233.1,GL000204.1,GL000198.1,GL000208.1,GL000191.1,GL000227.1,GL000228.1,GL000214.1,GL000221.1,GL000209.1,GL000218.1,GL000220.1,GL000213.1,GL000211.1,GL000199.1,GL000217.1,GL000216.1,GL000215.1,GL000205.1,GL000219.1,GL000224.1,GL000223.1,GL000195.1,GL000212.1,GL000222.1,GL000200.1,GL000193.1,GL000194.1,GL000225.1,GL000192.1,NC_007605,hs37d5", path_to_original_vcf]

    if os.path.isfile(vcf1):
        print(f'File {vcf1} already exists, moving on.')
    else:
        subprocess.run(command_split_vcf1)

    if os.path.isfile(vcf2):
        print(f'File {vcf2} already exists, moving on.')
    else:
        subprocess.run(command_split_vcf2)

    #Check that the new sizes are less than 250000000.
    #At the moment, manual intervention will be needed if the new files are still larger than the limit (e.g. to decide how to split the VCFs).
    size_vcf1 = os.path.getsize(vcf1)
    size_vcf2 = os.path.getsize(vcf2)
    if size_vcf1 >= 250_000_000 or size_vcf2 >= 250_000_000:
        print(f'One of the files is still larger than 250M. Investigate. Files to control: {vcf1} and {vcf2}.')
    else:
        VCF1 = FileInfo(vcf1,os.path.basename(vcf1))
        VCF2 = FileInfo(vcf2,os.path.basename(vcf2))
    
else:
    VCF = FileInfo(path_to_original_vcf, original_name)

