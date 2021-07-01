from typing import DefaultDict
import numpy as np
import argparse
import re
from pandas import read_csv
from glob import glob
from os import stat, getenv, path, makedirs
from dotenv import load_dotenv
from sys import argv, stderr, exit

load_dotenv()

def get_header(filename, combine):
    """Gets header from csv file"""
    header_df = read_csv(filename, index_col=False, nrows=0)
    if combine:
        header_df.columns = header_df.columns.str.replace(r'(-\d\.\d)', '')
    return header_df.columns


def get_dataset_id(filename):
    """Get dataset ID from filename /path/ukb[datasetID].csv"""
    base = path.basename(filename)
    return path.splitext(base)[0].replace("ukb", "")

def dir_path(string):
    """Checks existence of directory"""
    if path.isdir(string):
        return string
    else:
        raise argparse.ArgumentTypeError(f"directory: {string} is not a valid directory path")

def extract_phenotypes(ID_list, output_fname, combine=False, combine_op="last", chunksize=10000, pheno_dir=None, target_dir=".", exclude_file=None, debug=False):
    """Extract phenotypes from ukb csv and write to plink friendly format

    Args:
        ID_list (str): list of UKB phenotype IDs. e.g. 50=height
        output_fname (str): filename of output
        combine (bool, optional): combines columns of the same phenotype measured at different times. If False, must specify full ID; if True, must specify only field ID. Defaults to True.

    Returns:
        bool: Returns True on success, False on failure
    """

    # grab files matching ukb*.csv for IDs in order of largest dataset ID to smallest e.g. ukb27702.csv is searched before ukb27701.csv
    pheno_dir = path.join(path.abspath(pheno_dir), '') + 'ukb*.csv' if pheno_dir else path.expanduser(getenv('PHENO_PATH') + 'ukb*.csv')
    file_list = sorted(glob(pheno_dir), key=lambda x: int(path.basename(x).split('.')[0].replace('ukb', '')), reverse=True)
    # grab list of UKB participants who have withdrawn and should be excluded
    exclude_file = exclude_file if exclude_file else getenv('EXCLUSION_FILE')
    exclusion_index = read_csv(exclude_file, header=None, index_col=0).index

    if debug:
        print("Pheno dir: ", pheno_dir)
        print("File list:", file_list)

    # map filename to included field IDs
    ID_list = set(ID_list)
    fname_index = 0
    # create output dir
    makedirs(path.join(path.abspath(target_dir), '') + output_fname, exist_ok=True)

    while ID_list and fname_index < len(file_list):
        filename = file_list[fname_index]
        header = get_header(filename, combine)
        header_names = set(header.unique())
        
        if debug:
            print("File being read: ", filename)
            print("File header: ", header)
            print("Unique header names: ", header_names)

        # if file contains any of the phenotypes, read that column and write to plink format pheno file
        included_cols = list(ID_list.intersection(header_names))
        if debug:
            print("Included cols: ", included_cols)
        
        if len(included_cols) > 0:
            usecols = lambda x: x == "eid" or any(field_id in x for field_id in included_cols)
            with read_csv(filename, usecols=usecols, chunksize=chunksize, dtype=str, index_col="eid") as reader:
                is_header = 1
                mode = 'w'
                for chunk in reader:
                    # combine columns with same field value by taking last (rightmost) non-NA value
                    if combine:
                        chunk.columns = chunk.columns.str.replace(r'(-\d\.\d)', '')
                        if combine_op == "first":
                            chunk = chunk.groupby(level=0, axis=1).first()
                        else:
                            chunk = chunk.groupby(level=0, axis=1).last()
                    
                    chunk = chunk[~chunk.index.isin(exclusion_index)] # drop excluded samples
                    # set FID = 0, IID = eid in first two columns, fill NA values with -9
                    chunk.insert(loc=0, column="IID", value=chunk.index)
                    chunk.insert(loc=0, column="FID", value=0)
                    chunk.fillna(value=-9, inplace=True)
                    if debug:
                        print("Chunk to be written:\n", chunk)
                    target_file = path.join(path.abspath(target_dir), '') + output_fname + "/" + output_fname + get_dataset_id(filename) + ".pheno"
                    chunk.to_csv(target_file, header=is_header, index=False, sep=' ', mode=mode)
                    print("Wrote ", output_fname + get_dataset_id(filename) + ".pheno")
                    is_header = 0
                    mode = 'a'

        ID_list = ID_list.difference(header_names)
        fname_index += 1

    if ID_list:
        print("The following IDs were not found in the UKB csv files: ", ID_list)
        return False
    return True


if __name__ == "__main__":
    # parse arguments
    class CustomFormatter(argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass
    example_text = " "

    parser = argparse.ArgumentParser(description="Extract phenotypes from directory holding ukb csv files. Change this directory in the .env file", formatter_class=CustomFormatter)
    if len(argv)==1:
        parser.print_help(stderr)
        exit(1)
    
    parser.add_argument("fields", nargs="+", help="""UKB field IDs or full column IDs to be extracted e.g.
    "31-?.? 31-?.? 50-0.0 50-1.0 50-2.0 1299-0.0" if you want to keep instance/arrays separate
    "31 50 1299" if you want to take the latest measured instance. Requires combine flag.""")
    parser.add_argument("-n", "--name", help="Output directory name e.g. 'foo'. This will create directory foo/ with files foo[datasetID1].pheno, foo[datasetID2].pheno etc", 
                        required=True)
    parser.add_argument("-c", "--combine", nargs="?", help="Flag to combine columns with same field ids. Options are 'none', 'last', 'first'. Default is to take most recent non-empty value (rightmost in the csv).", 
                        default="none", const="last")
    # TODO: Better help for combine flag
    parser.add_argument("-r", "--rows", help="Number of rows to read in at a time when parsing the csv. Default is 10000.", type=int, default=10000)
    parser.add_argument("-d", "--dir", help="Directory to look for ukb files. Defaults to path in .env file", type=dir_path, action="store")
    parser.add_argument("-t", "--target", help="Directory to place extracted phenotypes folder. Default is current directory.", type=dir_path, action="store", default=".")
    parser.add_argument("-e", "--exclude", help="CSV where first column is list of IDs to exclude in the output phenotype files")
    parser.add_argument("-v", "--verbose", help="Print intermediate outputs for debugging", action="store_true", default=False)

    args = vars(parser.parse_args())
    ID_list = args["fields"]
    output_fname = args["name"]
    combine_op = args["combine"]
    combine = False if combine_op == "none" else True
    chunksize = int(args["rows"])
    debug = args["verbose"]
    pheno_dir = args["dir"]
    target_dir = args["target"]
    exclude_file = args["exclude"]

    print("Extracting phenotypes...")
    extract_phenotypes(ID_list, output_fname, combine, combine_op, chunksize, pheno_dir, target_dir, exclude_file, debug)

    # test commands (reads ukb*.csv in test directory)
    # python3 extract_pheno.py 21 31 34 44 45 50 72 -n comb -c -r 100 -d tests -e tests/test_exclude.csv -v
    # python3 extract_pheno.py 31-0.0 34-0.0 44-0.0 50-0.0 50-1.0 50-2.0 -n nocom -r 100 -d tests -e tests/test_exclude.csv -v


