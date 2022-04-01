#Usage (to print the help message): module load anaconda2; source activate wopr_alissa; python chunk_vcf.py --help

import sys
import os
import subprocess
import lists_of_contigs
import click

from tools.helpers import setup_logger

def bgzip(vcf, outfolder):
    """Bgzip VCF file."""
    basename = os.path.basename(vcf)
    bgzipped_vcf = os.path.join(outfolder, basename + ".gz")
    command_bgzip = ["bcftools", "view", "--output-type", "z", "--output", bgzipped_vcf, vcf]
    if os.path.isfile(bgzipped_vcf):
        bgzipped_exist = True
    else:
        subprocess.run(command_bgzip)
        bgzipped_exist = False

    return bgzipped_vcf, bgzipped_exist

def index(vcf):
    """Index a bgzipped VCF if the index cannot be found."""
    command_index = ["bcftools", "index", vcf]
    if os.path.isfile(os.path.join(vcf + ".csi")):
        index_exist = True
    else:
        subprocess.run(command_index)
        index_exist = False

    return index_exist

def split_vcf(vcf, outfolder, suffix, regions):
    """Return a VCF file that contains a subset of regions from the input VCF. Arguments outfolder and suffix are used to name the output file."""
    basename = os.path.basename(vcf).replace('.vcf.gz', '')
    output = os.path.join(outfolder, basename + suffix + '.vcf.gz')
    command_split = ["bcftools", "view", "--output-type", "z", "--output", output, "-r", regions, vcf]
    if os.path.exists(output):
        #TODO could the message below be included in logger as well?
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
        split_status = False
        n_chunks = 0
        return [vcf], split_status, n_chunks

    else:
        split_status = True
        for chunk_attempt in lists_of_contigs.contig_lists:
            chunks = []
            for chunk in chunk_attempt:
                chunk_path = split_vcf(vcf, outfolder, chunk[0], chunk[1])
                chunks.append(chunk_path)

            if not any([os.path.getsize(chunk) > size for chunk in chunks]):
                n_chunks = len(chunks)
                return chunks, split_status, n_chunks
        else:
            #TODO how should I deal with that for the logger? I do not fully understand the "else" logic here.
            n_chunks = 0
            return chunks, split_status, n_chunks
        
def prepare_and_split_vcf(vcf, outfolder, size):
    """Perform preliminary checks on input and return one to four VCF.GZ smaller than the given size."""
    ## Set up the logfile and start logging.
    # TODO is it weird that this is here and not in main() ? The point of having all the steps here was that one could import the function prepare_and_split_vcf (nicer than having to import main).
    logger = setup_logger('prepare_and_split_vcf')

    logger.info(f'Starting preparation of file {vcf}')

    ## Check input format.
    logger.info(f'Checking format of {vcf}')
    if not (vcf.endswith('vcf.gz') or vcf.endswith('vcf')):
        logger.error('The input file should be a VCF (.vcf or .vcf.gz).') 
        raise Exception

    ## Check that input is not empty.
    if os.path.getsize(vcf) == 0:
        logger.error(f'Please check this file: {vcf}, the size is 0.')
        raise Exception

    else:
        if vcf.endswith('vcf'):
            logger.info("The VCF will be bgzipped.")
            unindexed_vcf, bgzipped_exists = bgzip(vcf, outfolder)
            if bgzipped_exists == True:
                logger.info(f'A bgzipped version of the file exists already, using that instead.')
            else:
                logger.info('The file has been bgzipped.')

        else:
            unindexed_vcf = vcf
 
        ## Index the VCF.
        logger.info('Starting indexing of the input file.')
        index_exists = index(unindexed_vcf)
        if index_exists == True:
            logger.info(f'There is already an index for {unindexed_vcf}, skipping indexing.')
        else:
            logger.info(f'The file {unindexed_vcf} has been indexed.')
    
        ## Split the VCF.
        logger.info(f'Checking the size of the file and starting chunking if relevant.')
        new_vcfs, status, n_chunks = prepare_chunk(unindexed_vcf, outfolder, size)
        if status == False:
            logger.info(f'The input file is smaller than {size} and does not need to be split.')
        else:
            if n_chunks == 0:
                logger.error(f'We ran out of chunks and one of the files is still larger than {size} bytes. Please intervene manually.')
                raise Exception
            else:
                logger.info(f'The input file has been split in {n_chunks} chunks.')
    
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

