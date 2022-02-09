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
    vcf1 = original_folder+"/"+basename+"_chr1-8.vcf.gz"
    vcf2 = original_folder+"/"+basename+"_chr9-hs37d5.vcf.gz"

    #Split the VCF.
    command_compress = ["bgzip", "-c"]

    command_split_vcf1 = ["vcftools", "--gzvcf", path_to_original_vcf,
                          "--chr", "1", "--chr", "2", "--chr", "3", "--chr", "4", "--chr", "5", "--chr", "6", "--chr", "7", "--chr", "8", "--recode", "--recode-INFO-all", "--stdout"]
    if os.path.isfile(vcf1):
        print(f'File {vcf1} already exists, moving on.')
    else:
        f1 = open(vcf1, "w")
        split = subprocess.Popen(command_split_vcf1, stdout = subprocess.PIPE)
        subprocess.run(command_compress, stdin = split.stdout, stdout = f1)
        f1.close()

    if os.path.isfile(vcf2):
        print(f'File {vcf2} already exists, moving on.')
    else:
        command_split_vcf2 = ["vcftools", "--gzvcf", path_to_original_vcf,
                              "--chr", "9", "--chr", "10", "--chr", "11", "--chr", "12", "--chr", "13", "--chr", "14", "--chr", "15", "--chr", "16",
                              "--chr", "17", "--chr", "18", "--chr", "19", "--chr", "20", "--chr", "21", "--chr", "22", "--chr", "X", "--chr", "Y", "--chr", "MT",
                              "--chr", "GL000207.1", "--chr", "GL000226.1", "--chr", "GL000229.1", "--chr", "GL000231.1", "--chr", "GL000210.1", "--chr", "GL000239.1",
                              "--chr", "GL000235.1", "--chr", "GL000201.1", "--chr", "GL000247.1", "--chr", "GL000245.1", "--chr", "GL000197.1", "--chr", "GL000203.1",
                              "--chr", "GL000246.1", "--chr", "GL000249.1", "--chr", "GL000196.1", "--chr", "GL000248.1", "--chr", "GL000244.1", "--chr", "GL000238.1",
                              "--chr", "GL000202.1", "--chr", "GL000234.1", "--chr", "GL000232.1", "--chr", "GL000206.1", "--chr", "GL000240.1", "--chr", "GL000236.1",
                              "--chr", "GL000241.1", "--chr", "GL000243.1", "--chr", "GL000242.1", "--chr", "GL000230.1", "--chr", "GL000237.1", "--chr", "GL000233.1",
                              "--chr", "GL000204.1", "--chr", "GL000198.1", "--chr", "GL000208.1", "--chr", "GL000191.1", "--chr", "GL000227.1", "--chr", "GL000228.1",
                              "--chr", "GL000214.1", "--chr", "GL000221.1", "--chr", "GL000209.1", "--chr", "GL000218.1", "--chr", "GL000220.1", "--chr", "GL000213.1",
                              "--chr", "GL000211.1", "--chr", "GL000199.1", "--chr", "GL000217.1", "--chr", "GL000216.1", "--chr", "GL000215.1", "--chr", "GL000205.1",
                              "--chr", "GL000219.1", "--chr", "GL000224.1", "--chr", "GL000223.1", "--chr", "GL000195.1", "--chr", "GL000212.1", "--chr", "GL000222.1",
                              "--chr", "GL000200.1", "--chr", "GL000193.1", "--chr", "GL000194.1", "--chr", "GL000225.1", "--chr", "GL000192.1", "--chr", "NC_007605", "--chr", "hs37d5",
                              "--recode", "--recode-INFO-all", "--stdout"]
        f2 = open(vcf2, "w")
        split = subprocess.Popen(command_split_vcf2, stdout = subprocess.PIPE)
        subprocess.run(command_compress, stdin = split.stdout, stdout = f2)
        f2.close()

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

