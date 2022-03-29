#Usage (to print the help message): module load anaconda2; source activate wopr_alissa; python chunk_vcf.py --help

import sys
import os
import subprocess
import lists_of_contigs
import click

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
    If the input is larger than the given size, the function will loop over a list of lists of contigs until either all files are smaller than the given size, or it runs out of lists of contigs. At the moment there are three lists available, so it will return two, three or four chunks.
    Return an exception if one of the four chunks is larger than the given size. 
    """
    
    if os.path.getsize(vcf) < size:
        print('The VCF did not need to be split.')
        return [vcf]

    else:
        for chunk_attempt in lists_of_contigs.contig_lists:
            chunks = []
            for chunk in chunk_attempt:
                chunk_path = split_vcf(vcf, outfolder, chunk[0], chunk[1])
                chunks.append(chunk_path)

            if not any([os.path.getsize(chunk) > size for chunk in chunks]):
                l = len(chunks)
                print(f'The VCF has been split into {l} chunks.')
                return chunks
        else:
            raise Exception(f'We ran out of chunks and one of the files is still larger than {size} bytes. Please investigate.')
        
def prepare_and_split_vcf(vcf, outfolder, size):
    """Perform preliminary checks on input and return one to four VCF.GZ smaller than the given size."""
    #Check input format.
    if not (vcf.endswith('vcf.gz') or vcf.endswith('vcf')):
        raise Exception('The input file should be a VCF (.vcf or .vcf.gz).') 

    #Check that input is not empty.
    if os.path.getsize(vcf) == 0:
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

@click.command()
@click.option('-v', '--vcf_path', required=True,
              help='Path to input VCF file')
@click.option('-o', '--output_folder', default='/tmp',
              help='Path to a folder where VCF will be written if the input VCF is larger than the size argument')
@click.option('-s', '--size', required=True, type=int,
              help='Size in bp. If the VCF exceed this size, it will be split into 2, 3 or 4 VCFs')
def main(vcf_path, output_folder, size):
    chunks = prepare_and_split_vcf(vcf_path, output_folder, size)
    return chunks
    
if __name__ == '__main__':
    main()

