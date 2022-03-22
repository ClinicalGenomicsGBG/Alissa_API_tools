#Usage: python3 chunk_vcf.py
# The arguments are hardcoded (path_to_original_vcf, output_folder and max_size).
# TODO Use e.g. /tmp on working node as the output folder

import sys
import os
import subprocess
import lists_of_contigs

path_to_original_vcf = '/home/xbregw/Alissa_upload/VCFs/NA24143_191108_AHVWHGDSXX_SNV_CNV_germline.vcf.gz'
output_folder = '/home/xbregw/Alissa_upload/VCFs/chunks'
max_size = 240_000_000

def vcf_larger_than(vcf, size):
    """Return True if the size of the VCF is larger than a given size."""
    vcf_size = os.path.getsize(vcf)
    return vcf_size > size

def bgzip(vcf, outfolder):
    """Bgzip VCF file."""
    basename = os.path.basename(vcf)
    bgzipped_vcf = os.path.join(outfolder, basename + ".gz")
    command_bgzip = ["bcftools", "view", "--output-type", "z", "--output", bgzipped_vcf, vcf]
    if os.path.isfile(bgzipped_vcf):
        print('File exists already, skipping compression.')
    else:
        subprocess.run(command_bgzip)
    return bgzipped_vcf

def index(vcf):
    """Index a bgzipped VCF if the index cannot be found."""
    command_index = ["bcftools", "index", vcf]
    if os.path.isfile(os.path.join(vcf + ".csi")):
        print('Index exists already, skipping indexing.')
    else:
        subprocess.run(command_index)

def split_vcf(vcf, outfolder, suffix, regions):
    """Return a VCF file that contains a subset of regions from the input VCF. Arguments outfolder and suffix are used to name the output file."""
    basename = os.path.basename(vcf).replace('.vcf.gz', '')
    output = os.path.join(outfolder, basename + suffix + '.vcf.gz')
    command_split = ["bcftools", "view", "--output-type", "z", "--output", output, "-r", regions, vcf]
    if os.path.exists(output):
        print(f'File {output} already exists, moving on.')
    else:
        split = subprocess.run(command_split)
        split.check_returncode()
    return output

def prepare_chunk(vcf, outfolder, size):
    """Return a list of paths to compressed VCF files smaller than a given size.

    If the input is smaller than the given size, there is a single vcf.
    If the input is larger than the given size, the function will in a first instance return two chunks, according to a pre-defined list of contigs resulting in two files of similar size (assuming the initial file contains the entire genome). If these chunks are still larger than the given size, the input will be splitted in three. If these chunks are larger than the given size, the input will be splitted in four.
    Return an exception if one of the four chunks is larger than the given size. 
    """
    
    splitted = [vcf]
    toobig = any([vcf_larger_than(newvcf, size) for newvcf in splitted ]) #Initialize boolean that returns True if at least one of the files is too large.
    i = 0 #Initialize count variable for while loop

    while i < len(lists_of_contigs.contig_lists) and toobig :
        splitted = []
        for partition in lists_of_contigs.contig_lists[i] :
            chunk = split_vcf(vcf, outfolder, partition[0], partition[1])
            splitted.append(chunk)        
        i = i + 1
        toobig = any([vcf_larger_than(newvcf, size) for newvcf in splitted ])
        print(toobig)
        j = i + 1
        print(f'The VCF has been split into {j} chunks.')

    if toobig:
        raise Exception(f'We ran out of chunks and one of the files is still larger than {size} bytes. Please investigate.')
       
    return splitted
        
def prepare_and_split_vcf(vcf, outfolder, size):
    """Perform preliminary checks on input and return one to four VCF.GZ smaller than the given size."""
    #Check input format.
    if not (vcf.endswith('vcf.gz') or vcf.endswith('vcf')):
        raise Exception('The input file should be a VCF (.vcf or .vcf.gz).') 

    #Check that input is not empty.
    if not vcf_larger_than(vcf, 0):
        raise Exception(f'Please check this file: {vcf}, the size is 0.')

    else:
        if vcf.endswith('vcf'):
            print("The VCF will be bgzipped.")
            unindexed_vcf = bgzip(vcf, outfolder)

        else:
            unindexed_vcf = vcf
 
        #Index the VCF.
        index(unindexed_vcf)
            
        #Split the VCF.
        new_vcfs = prepare_chunk(unindexed_vcf, outfolder, size)
            
        return new_vcfs

    
def main():
    chunks = prepare_and_split_vcf(path_to_original_vcf, output_folder, max_size)
    return chunks
    
if __name__ == '__main__':
    main()

