# uchicago-ukb
## Misc scripts/tools for working with UKB csv files
- [Phenotype Extraction](#phenotype-extraction)
  * [Command Line Arguments](#command-line-arguments)
  * [Sample Calls](#sample-calls)
  * [Possible Errors](#possible-errorsexceptions)


### Phenotype Extraction
Given a set of IDs, the script will search through a directory for files matching the pattern `ukb[datasetID].csv`, starting from the largest dataset ID, and extract the corresponding phenotypes.

It writes the output into a new directory containing plink formatted phenotype files, with each output file corresponding to one of the UKB dataset files.
For example, if half of the phenotypes were in `ukb27702.csv` and the other half in `ukb27701.csv`, it would output two corresponding .pheno files.

It will also automatically exclude the samples that have withdrawn from the study in the output file.

Run `python3 extract_pheno.py -h` to see options.

#### Command Line Arguments
##### Required:
- `<ID1> <ID2> etc`: list of space-delimited IDs corresponding to columns in the csv file (`[fieldID]-[instance index].[array index]`)
    - **if only field ID is provided and corresponding columns should be combined, then the `-c/--combine` flag is required (see below)**.
- `-n/--name <name>`: output directory name 
##### Optional:
- `-c/--combine (<none/first/last>)`: combine columns with the same field ID. If no argument is given to the flag, default behavior is to take the rightmost (last) non-missing value.
    - if the flag is not provided it will default to `none` and requires instance and array indices to be specified in the ID list.
- `-d/--dir <path/to/ukb/phenotypes>`: specify directory to search for the ukb phenotype CSVs. Defaults to the path in the consts file.
- `-e/--exclude <path/to/exclude.csv>`: specify csv that contains list of eids to exclude bc participants have withdrawn. Defaults to the path in the consts file.
- `-r/--rows <N>`: number of rows of a csv file to read in at a time (in cases where memory is limited). Defaults to 10000.
- `-t/--target <path/to/output/directory/>`: specify directory to create folder for extracted phenotype files. Defaults to current directory that the command is being issued in.
- `-v/--verbose`: print intermediate outputs for debugging purposes

#### Sample Calls
Looks for and outputs files in `./tests/` directory
- `python3 extract_pheno.py 21 31 34 44 45 50 72 -n comb -c -r 100 -d tests -e tests/test_exclude.csv -t tests`
- `python3 extract_pheno.py 31-0.0 34-0.0 44-0.0 50-0.0 50-1.0 50-2.0 -n nocomb -r 100 -d tests -e tests/test_exclude.csv -t tests`

#### Possible Errors/Exceptions
- ~~`AttributeError: __enter__` on `with read_csv...`. Check that your pandas installation is version >= 1.2 (script relies on read_csv w/ chunksize returning a context maanger)~~ this should be fixed
- `Exception ignored in: <_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'> OSError: [Errno 122] Disk quota exceeded`. Comes from using the `-v` flag on the cluster on large datasets; output files should still be fine.

### If running on CRI using Lmod (as of Dec 2021):
* install & run in home directory

#### To run as a submission script:
* load gcc and miniconda3 at the top of the script following the qsub options as follows$
* module load gcc/6.2.0
* module load miniconda3/4.7.10
* submit the script: qsub script.sh

#### To run in the shell (not advised outside of an interactive session):
* load gcc and miniconda as follows:
* module load gcc/6.2.0
* module load miniconda3/4.7.10
* run conda init bash
* restart the shell
* run the script: bash script.sh
