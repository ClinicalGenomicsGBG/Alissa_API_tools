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
    return vcf_size > size

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

#TODO this is a draft - once I have written it out more or less, see which arguments are needed etc. Would a class be better? "basename" is defined several times I think. Etc.
def split_vcf(vcf, root, suffix, regions):
#    output = os.path.join(root, suffix + '.vcf.gz')
    output = root + suffix + '.vcf.gz' #TODO replace by something nicer. os.path.join does not give the expected result (removes the file name from root).
    command_split = ["bcftools", "view", "--output-type", "z", "--output", output, "-r", regions, vcf]
    if os.path.exists(output):
        print(f'File {output} already exists, moving on.')
        #What should happen then? "pass"?
    else:
        subprocess.run(command_split)
    return output

def prepare_chunk(vcf, outfolder, size):
    """Return a list of paths to compressed VCF files smaller than a given size.

    If the input is smaller than the given size, there is a single vcf.
    If the input is larger than the given size, the function will in a first instance return two chunks, according to a pre-defined list of contigs resulting in two files of similar size (assuming the initial file contains the entire genome). If these chunks are still larger than the given size, the input will be splitted in three. If these chunks are larger than the given size, the input will be splitted in four.
    Return an exception if one of the four chunks is larger than the given size. 
    """
    
    if not vcf_larger_than(vcf, size):
        print(f'The file is smaller than {size} bytes. It will not be splitted.')
        splitted = [vcf]

    else:
        print(f'The file is larger than {size} bytes and will be splitted into two VCFs.')
        
        basename = os.path.basename(vcf).replace('.vcf.gz', '')
        root = os.path.join(outfolder, basename)

        #TODO decide where the "split_in_2/3/4" lists should be. Here in the function, or in a config file?
        split_in_2 = [["_chr1-8","1,2,3,4,5,6,7,8"], ["_chr9-hs37d5","9,10,11,12,13,14,15,16,17,18,19,20,21,22,X,Y,MT,GL000207.1,GL000226.1,GL000229.1,GL000231.1,GL000210.1,GL000239.1,GL000235.1,GL000201.1,GL000247.1,GL000245.1,GL000197.1,GL000203.1,GL000246.1,GL000249.1,GL000196.1,GL000248.1,GL000244.1,GL000238.1,GL000202.1,GL000234.1,GL000232.1,GL000206.1,GL000240.1,GL000236.1,GL000241.1,GL000243.1,GL000242.1,GL000230.1,GL000237.1,GL000233.1,GL000204.1,GL000198.1,GL000208.1,GL000191.1,GL000227.1,GL000228.1,GL000214.1,GL000221.1,GL000209.1,GL000218.1,GL000220.1,GL000213.1,GL000211.1,GL000199.1,GL000217.1,GL000216.1,GL000215.1,GL000205.1,GL000219.1,GL000224.1,GL000223.1,GL000195.1,GL000212.1,GL000222.1,GL000200.1,GL000193.1,GL000194.1,GL000225.1,GL000192.1,NC_007605,hs37d5"]]
        split_in_3 = [["_chr1-5","1,2,3,4,5"], ["_chr6-12","6,7,8,9,10,11,12"], ["_chr13-hs37d5","13,14,15,16,17,18,19,20,21,22,X,Y,MT,GL000207.1,GL000226.1,GL000229.1,GL000231.1,GL000210.1,GL000239.1,GL000235.1,GL000201.1,GL000247.1,GL000245.1,GL000197.1,GL000203.1,GL000246.1,GL000249.1,GL000196.1,GL000248.1,GL000244.1,GL000238.1,GL000202.1,GL000234.1,GL000232.1,GL000206.1,GL000240.1,GL000236.1,GL000241.1,GL000243.1,GL000242.1,GL000230.1,GL000237.1,GL000233.1,GL000204.1,GL000198.1,GL000208.1,GL000191.1,GL000227.1,GL000228.1,GL000214.1,GL000221.1,GL000209.1,GL000218.1,GL000220.1,GL000213.1,GL000211.1,GL000199.1,GL000217.1,GL000216.1,GL000215.1,GL000205.1,GL000219.1,GL000224.1,GL000223.1,GL000195.1,GL000212.1,GL000222.1,GL000200.1,GL000193.1,GL000194.1,GL000225.1,GL000192.1,NC_007605,hs37d5"]]
        split_in_4 = [["_chr1-4","1,2,3,4"], ["_chr5-8","5,6,7,8"], ["_chr9-14","9,10,11,12,13,14"], ["_chr15-hs37d5","15,16,17,18,19,20,21,22,X,Y,MT,GL000207.1,GL000226.1,GL000229.1,GL000231.1,GL000210.1,GL000239.1,GL000235.1,GL000201.1,GL000247.1,GL000245.1,GL000197.1,GL000203.1,GL000246.1,GL000249.1,GL000196.1,GL000248.1,GL000244.1,GL000238.1,GL000202.1,GL000234.1,GL000232.1,GL000206.1,GL000240.1,GL000236.1,GL000241.1,GL000243.1,GL000242.1,GL000230.1,GL000237.1,GL000233.1,GL000204.1,GL000198.1,GL000208.1,GL000191.1,GL000227.1,GL000228.1,GL000214.1,GL000221.1,GL000209.1,GL000218.1,GL000220.1,GL000213.1,GL000211.1,GL000199.1,GL000217.1,GL000216.1,GL000215.1,GL000205.1,GL000219.1,GL000224.1,GL000223.1,GL000195.1,GL000212.1,GL000222.1,GL000200.1,GL000193.1,GL000194.1,GL000225.1,GL000192.1,NC_007605,hs37d5"]]

        #Split in two.
        splitted = []
        for partition in split_in_2:
            chunk = split_vcf(vcf, root, partition[0], partition[1])
            splitted.append(chunk)

        if any([vcf_larger_than(newvcf, size) for newvcf in splitted ]):       
            print(f'At least on of the files is larger than {size} bytes. The input will be splitted into three VCFs.')
            #Split in three.
            splitted = []
            for partition in split_in_3:
                chunk = split_vcf(vcf, root, partition[0], partition[1])
                splitted.append(chunk)

            if any([vcf_larger_than(newvcf, size) for newvcf in splitted ]):
                print(f'At least one of the files is larger than {size} bytes. The input will be splitted into four VCFs.')
                #Split in four.
                splitted = []
                for partition in split_in_4:
                    chunk = split_vcf(vcf, root, partition[0], partition[1])
                    splitted.append(chunk)

                if any([vcf_larger_than(newvcf, size) for newvcf in splitted ]):
                    raise Exception(f'One of the files is still larger than {size} bytes. Please investigate.')
                
    return splitted
        
def prepare_and_split_vcf(vcf, outfolder, size):
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

