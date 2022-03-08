#Usage: python3 chunk_vcf.py
# The arguments are hardcoded (path_to_original_vcf, output_folder and max_size).
# TODO Use e.g. /tmp on working node as the output folder

import sys
import os
import subprocess

#args = sys.argv
#path_to_original_vcf = str(args[1]).strip()
#output_folder = str(args[2]).strip()
path_to_original_vcf = '/home/xbregw/Alissa_upload/VCFs/NA24143_191108_AHVWHGDSXX_SNV_CNV_germline.vcf.gz'
output_folder = '/home/xbregw/Alissa_upload/VCFs/chunks'
max_size = 100_000_000

def vcf_larger_than(vcf, size):
    """Return True if the size of the VCF is larger than a given size."""
    vcf_size = os.path.getsize(vcf)
    return bool(vcf_size > size)

def bgzip(vcf, outfolder):
    """Bgzip VCF file."""
    basename = os.path.basename(vcf)
    bgzipped_vcf = os.path.join(outfolder, basename + ".gz")
    command_bgzip = ["bcftools", "view", "--output-type", "z", "--output", bgzipped_vcf, vcf]
    subprocess.run(command_bgzip)
    return bgzipped_vcf

def index(vcf):
    """Index a bgzipped VCF if the index cannot be found."""
    command_index = ["bcftools", "index", vcf]
    if os.path.isfile(os.path.join(vcf + ".csi")):
        print('Index exists already, skipping indexing.')
    else:
        subprocess.run(command_index)

def split_vcf(vcf, outfolder, size):
    """Return a list of paths to compressed VCF files smaller than a given size.

    If the input is smaller than the given size, there is a single chunk.
    If the input is larger than the given size, the function will in a first instance return two chunks, according to a pre-defined list of contigs resulting in two files of similar size (assuming the initial file contains the entire genome). If these chunks are still larger than the given size, each will be splitted once more, returning a total of four chunks.
    Return an exception if one of the four chunks is larger than the given size. 
    """
    
    if not vcf_larger_than(vcf, size):
        print(f'The file is smaller than {size} bytes. It will not be splitted.')
        return [vcf]

    else:
        print(f'The file is larger than {size} bytes and will be splitted into two VCFs.')
        
        basename = os.path.basename(vcf).replace('.vcf.gz', '')
        vcf1 = os.path.join(outfolder, basename + "_chr1-8.vcf.gz")
        vcf2 = os.path.join(outfolder, basename + "_chr9-hs37d5.vcf.gz")
    
        #The "-r" or "--regions" argument of "bcftools view" allows to subset a VCF file according to a list of regions. In this case we use contigs. The lists of contigs in command_split_vcf1 and command_split_vcf2 cover all the contigs in the VCF outputted by WOPR and result in two VCF of equivalent size.
        # The output format is a compressed VCF.
        command_split_vcf1 = ["bcftools", "view", "--output-type", "z", "--output", vcf1, "-r", "1,2,3,4,5,6,7,8", vcf]
        command_split_vcf2 = ["bcftools",  "view", "--output-type", "z", "--output", vcf2, "-r", "9,10,11,12,13,14,15,16,17,18,19,20,21,22,X,Y,MT,GL000207.1,GL000226.1,GL000229.1,GL000231.1,GL000210.1,GL000239.1,GL000235.1,GL000201.1,GL000247.1,GL000245.1,GL000197.1,GL000203.1,GL000246.1,GL000249.1,GL000196.1,GL000248.1,GL000244.1,GL000238.1,GL000202.1,GL000234.1,GL000232.1,GL000206.1,GL000240.1,GL000236.1,GL000241.1,GL000243.1,GL000242.1,GL000230.1,GL000237.1,GL000233.1,GL000204.1,GL000198.1,GL000208.1,GL000191.1,GL000227.1,GL000228.1,GL000214.1,GL000221.1,GL000209.1,GL000218.1,GL000220.1,GL000213.1,GL000211.1,GL000199.1,GL000217.1,GL000216.1,GL000215.1,GL000205.1,GL000219.1,GL000224.1,GL000223.1,GL000195.1,GL000212.1,GL000222.1,GL000200.1,GL000193.1,GL000194.1,GL000225.1,GL000192.1,NC_007605,hs37d5", vcf]
    
        if os.path.exists(vcf1):
            print(f'File {vcf1} already exists, moving on.')
        else:
            subprocess.run(command_split_vcf1)
    
        if os.path.exists(vcf2):
            print(f'File {vcf2} already exists, moving on.')
        else:
            subprocess.run(command_split_vcf2)
      
        #Check the size of the two chunks. If one is larger than the given size: split again both files.
        if any([vcf_larger_than(newvcf, size) for newvcf in [vcf1, vcf2]]):
            vcf1A = os.path.join(outfolder, basename + "_chr1-4.vcf.gz")
            vcf1B = os.path.join(outfolder, basename + "_chr5-8.vcf.gz")
            vcf2A = os.path.join(outfolder, basename + "_chr9-14.vcf.gz")
            vcf2B = os.path.join(outfolder, basename + "_chr15-hs37d5.vcf.gz")            

            command_split_vcf1A = ["bcftools", "view", "--output-type", "z", "--output", vcf1A, "-r", "1,2,3,4", vcf]
            command_split_vcf1B = ["bcftools", "view", "--output-type", "z", "--output", vcf1B, "-r", "5,6,7,8", vcf]
            command_split_vcf2A = ["bcftools", "view", "--output-type", "z", "--output", vcf2A, "-r", "9,10,11,12,13,14", vcf]
            command_split_vcf2B = ["bcftools", "view", "--output-type", "z", "--output", vcf2B, "-r", "15,16,17,18,19,20,21,22,X,Y,MT,GL000207.1,GL000226.1,GL000229.1,GL000231.1,GL000210.1,GL000239.1,GL000235.1,GL000201.1,GL000247.1,GL000245.1,GL000197.1,GL000203.1,GL000246.1,GL000249.1,GL000196.1,GL000248.1,GL000244.1,GL000238.1,GL000202.1,GL000234.1,GL000232.1,GL000206.1,GL000240.1,GL000236.1,GL000241.1,GL000243.1,GL000242.1,GL000230.1,GL000237.1,GL000233.1,GL000204.1,GL000198.1,GL000208.1,GL000191.1,GL000227.1,GL000228.1,GL000214.1,GL000221.1,GL000209.1,GL000218.1,GL000220.1,GL000213.1,GL000211.1,GL000199.1,GL000217.1,GL000216.1,GL000215.1,GL000205.1,GL000219.1,GL000224.1,GL000223.1,GL000195.1,GL000212.1,GL000222.1,GL000200.1,GL000193.1,GL000194.1,GL000225.1,GL000192.1,NC_007605,hs37d5", vcf]
    
            subprocess.run(command_split_vcf1A)
            subprocess.run(command_split_vcf1B)
            subprocess.run(command_split_vcf2A)
            subprocess.run(command_split_vcf2B)

            if any([vcf_larger_than(newvcf, size) for newvcf in [vcf1A, vcf1B, vcf2A, vcf2B]]):
                raise Exception(f'One of the files is still larger than {size} bytes. Please investigate.')
                
            else:
                return [vcf1A, vcf1B, vcf2A, vcf2B]
        
        else:
            return [vcf1, vcf2]


def main():
    #Check whether the input is not empty.
    # TODO possibly later: instead of raising an exception, exit the process.
    if not (path_to_original_vcf.endswith('vcf.gz') or path_to_original_vcf.endswith('vcf')):
        raise Exception('The input file should be a VCF (.vcf or .vcf.gz).') 

    if not vcf_larger_than(path_to_original_vcf, 0):
        raise Exception(f'Please check this file: {path_to_original_vcf}, the size is 0.')

    else:
        if path_to_original_vcf.endswith('vcf'):
            print("The VCF will be bgzipped.")
            unindexed_vcf = bgzip(path_to_original_vcf, output_folder)

        else:
            unindexed_vcf = path_to_original_vcf
 
        #Index the VCF.
        index(unindexed_vcf)
            
        #Split the VCF.
        new_vcfs = split_vcf(unindexed_vcf, output_folder, max_size)
            
        return new_vcfs
    
if __name__ == '__main__':
    main()

