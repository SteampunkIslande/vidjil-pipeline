#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script is a rename of rna_seq_contig.py.
Use this one instead of previous.
V.0.01: first version of script; work well
v 0.2: 2023/06; improve parameters of minia to get better result on contigs size
"""

############################################################
### imports

from __future__ import division, print_function

import argparse
import json
import os
import sys
import tempfile
import time

############################################################
sys.path.insert(1, os.path.join(sys.path[0], ".."))
############################################################
### constants
PREPROCESS = "rnaseqLongerReads"
version = "v0.2"
MINIA_PATH = "/binaries/minia"
COMPLEMENT = {"A": "T", "C": "G", "G": "C", "T": "A"}

MINIA_ABUNDANCE_MIN = 5
MINIA_ABUNDANCE_THRESHOLD = 3


def reverse_complement(seq):
    return "".join(COMPLEMENT.get(base, base) for base in reversed(seq))


def analyse(data, directory, adaptater_length):
    """
    Take the top X of clone and apply the analyze (grep/minia/vidjil)
    Put updated informations into the clone and return modified data
    """
    origin_file = data["samples"]["original_names"][0]
    origin_cmd = data["samples"]["commandline"][0].split(" ")

    print("\n\n# ===================")
    print(f"\n{origin_file=}")
    print(f"\n{origin_cmd=}")

    clones = data["clones"]
    for top in range(1, 6):
        print("\n=============\nclone %s ****\n=============\n" % top)
        for clone in clones:
            if clone["top"] == top:
                clone, files_to_del = get_longer_reads(
                    clone, origin_file, origin_cmd, directory, adaptater_length
                )
                cleanDirectory(files_to_del)

    print(data["samples"]["original_names"])

    print("\n\n# ===================")
    return data


def get_longer_reads(clone, origin_file, origin_cmd, directory, adaptater_length):
    """
    Apply the various step of the analysis
    (grep, minia, vidjil, update content)
    """
    list_file_to_del = []

    sequence = clone["id"]
    seq_revcomp = reverse_complement(clone["id"])
    print("\n=== Grep reads in files %s..." % (clone["top"]))
    print("Origin file: %s" % origin_file)

    # Modify options depending of the format
    if origin_file.endswith(".fasta") or origin_file.endswith(".fa"):
        type_seq = {
            "type": "fasta",
            "grep": "grep",
            "suffix": ".fasta",
            "grep_option": "-B1",
            "divider": 2,
        }
    elif origin_file.endswith(".fastq"):
        type_seq = {
            "type": "fastq",
            "grep": "zgrep",
            "suffix": ".fq",
            "grep_option": "-B1 -A2",
            "divider": 4,
        }
    elif origin_file.endswith(".gz"):
        type_seq = {
            "type": "fastq.gz",
            "grep": "zgrep",
            "suffix": ".fq",
            "grep_option": "-B1 -A2",
            "divider": 4,
        }
    print("... file type: %s" % type_seq["type"])

    file_grep_r1 = tempfile.NamedTemporaryFile(suffix=type_seq["suffix"], delete=False)
    file_grep_r2 = tempfile.NamedTemporaryFile(suffix=type_seq["suffix"], delete=False)
    file_trim_r1 = tempfile.NamedTemporaryFile(suffix=type_seq["suffix"], delete=False)
    file_trim_r2 = tempfile.NamedTemporaryFile(suffix=type_seq["suffix"], delete=False)
    file_cat = tempfile.NamedTemporaryFile(suffix=type_seq["suffix"], delete=False)
    files_to_del = [
        file_grep_r1.name,
        file_grep_r2.name,
        file_trim_r1.name,
        file_trim_r2.name,
        file_cat.name,
    ]
    files_minia = []
    # make a grep of clonotype window on sequences files, reverse R2, and do a trimming of X nt (adaptater_length), cat data together
    cmd_grep_r1 = "%s  %s --no-group-separator %s %s > %s" % (
        type_seq["grep"],
        type_seq["grep_option"],
        sequence,
        origin_file,
        file_grep_r1.name,
    )
    cmd_grep_r2 = "%s  %s --no-group-separator %s %s > %s" % (
        type_seq["grep"],
        type_seq["grep_option"],
        reverse_complement(sequence),
        origin_file,
        file_grep_r2.name,
    )
    cmd_trim_r1 = (
        "cat %s | while read L; do echo $L && read L && echo $L | sed -r 's/^.{%s}//' | sed -r 's/.{%s}$//' && read L && echo $L && read L && echo $L | sed -r 's/^.{%s}//'| sed -r 's/.{%s}$//'  ;done > %s"
        % (
            file_grep_r1.name,
            adaptater_length,
            adaptater_length,
            adaptater_length,
            adaptater_length,
            file_trim_r1.name,
        )
    )
    cmd_trim_r2 = (
        "cat %s | while read L; do echo $L && read L && echo $L | rev  |  tr \"ATGCN\" \"TACGN\" | sed -r 's/^.{%s}//' | sed -r 's/.{%s}$//' && read L && echo $L && read L && echo $L | rev | sed -r 's/^.{%s}//'| sed -r 's/.{%s}$//'  ;done > %s"
        % (
            file_grep_r2.name,
            adaptater_length,
            adaptater_length,
            adaptater_length,
            adaptater_length,
            file_trim_r2.name,
        )
    )
    cmd_cat = "cat %s %s > %s" % (file_trim_r1.name, file_trim_r2.name, file_cat.name)

    print(cmd_grep_r1)
    os.system(cmd_grep_r1)
    print(cmd_grep_r2)
    os.system(cmd_grep_r2)
    print(cmd_trim_r1)
    os.system(cmd_trim_r1)
    print(cmd_trim_r2)
    os.system(cmd_trim_r2)
    print(cmd_cat)
    os.system(cmd_cat)

    ## Show number of lines of grep files (as fastq)
    with open(file_trim_r1.name, "r") as fp:
        x_r1 = len(fp.readlines())
        print(
            "Lines in grep forward: %s (%s seq)"
            % (x_r1, int(x_r1 / type_seq["divider"]))
        )
    with open(file_trim_r2.name, "r") as fp:
        x_r2 = len(fp.readlines())
        print(
            "Lines in grep reverse: %s (%s seq)"
            % (x_r2, int(x_r2 / type_seq["divider"]))
        )
    with open(file_cat.name, "r") as fp:
        x_cat = len(fp.readlines())
        print("Total lines: %s (%s seq)" % (x_cat, int(x_cat / type_seq["divider"])))

    if not x_cat:  # bypass, no reads available
        print("... No reads found. continue...")
        return clone, files_to_del

    # Create temporary directory for results
    res_vdj_path = tempfile.TemporaryDirectory()
    files_to_del.append(res_vdj_path.name)

    ## minia
    print("\n=== Assemblages minia %s..." % (clone["top"]))
    if not os.path.exists(MINIA_PATH):
        print("ERROR - Minia is not available. Verify availability and path.")
        return clone, files_to_del
    kmersizes = [62, 52, 42, 32, 22]
    sizes = []
    for kmersize in kmersizes:
        res_minia = tempfile.NamedTemporaryFile(
            suffix="-%s.minia" % kmersize, delete=False
        )
        cmd_minia = (
            "%s -in %s -out %s -kmer-size %s -abundance-min %s -abundance-min-threshold %s   > %s.log  2>&1"
            % (
                MINIA_PATH,
                file_cat.name,
                res_minia.name,
                kmersize,
                MINIA_ABUNDANCE_MIN,
                MINIA_ABUNDANCE_THRESHOLD,
                res_minia.name,
            )
        )
        print(cmd_minia)
        os.system(cmd_minia)

        # Sometimes, minia don't work if few reads is available (small dataset for example)
        if not os.path.exists(res_minia.name + ".contigs.fa"):
            sizes.append(0)
            print("Minia don't work for size %s" % kmersize)
        else:
            # get contig size; format: >0 LN:i:728 KC:i:168762 km:f:238.703
            with open(res_minia.name + ".contigs.fa") as f:
                first_line = f.readline()
                second_line = f.readline()
                print(first_line)
                print(second_line)
                if "len__" in first_line:
                    sizes.append(int(first_line.split("__")[2]))
                else:
                    sizes.append(len(second_line))
        files_minia.append(res_minia)
        files_to_del.append(res_minia.name)

    # get better result
    maxi = max(sizes)
    if maxi == 0:
        print("No correct size values")
        return clone, files_to_del
    better_index = sizes.index(maxi)
    better_file = files_minia[better_index]
    print(
        "Assemblage minia %s...done, better size %s with kmer of %s"
        % (clone["top"], maxi, kmersizes[better_index])
    )
    nb_contigs = getNumberOfContigs(better_file.name + ".contigs.fa")
    print("Assemblage minia %s...nb lines in contigs: %s" % (clone["top"], nb_contigs))

    ## vidjil
    print("\n=== Vidjil %s... > %s" % (clone["top"], better_file.name))

    index_output = (
        origin_cmd.index("-o") if "-o" in origin_cmd else origin_cmd.index("--output")
    )
    index_basename = (
        origin_cmd.index("-b") if "-b" in origin_cmd else origin_cmd.index("--base")
    )
    origin_cmd[index_output + 1] = res_vdj_path.name
    origin_cmd[index_basename + 1] = "result_%s" % clone["top"]

    cmd_vidjil = "  ".join(origin_cmd)
    cmd_vidjil = cmd_vidjil.replace(origin_file, better_file.name + ".contigs.fa")

    print(f"{cmd_vidjil=}")
    os.system(cmd_vidjil + " > " + res_vdj_path.name + ".log  2>&1")
    print("Vidjil %s...done" % (clone["top"]))

    os.listdir(res_vdj_path.name)
    print("os.listdir(%s):" % res_vdj_path.name)
    print(os.listdir(res_vdj_path.name))
    vidjil_file_name = "%s/result_%s.vidjil" % (res_vdj_path.name, clone["top"])
    print(
        "Does file '%s' exist: %s"
        % (vidjil_file_name, os.path.exists(vidjil_file_name))
    )
    if os.path.exists(vidjil_file_name):
        size = os.path.getsize(vidjil_file_name)
        print("Size of file is", size, "bytes")

    # Update clone with new content
    no_clone = False
    with open(vidjil_file_name) as nfile:
        ndata = json.load(nfile)
        if ndata["clones"] == None or len(ndata["clones"]) == 0:
            warn = "No clone found (top %s)" % clone["top"]
            putWarningInClone(clone, warn, "contigs_no_clone", "alert")
            print("WARNING: %s" % warn)
            # return clone
            no_clone = True
        elif len(ndata["clones"]) > 1:
            warn = "More than once clone are found (top %s)" % clone["top"]
            putWarningInClone(clone, warn, "contigs_multiple", "warn")
            print("WARNING: %s" % warn)

        rnaseqdata = {}
        nb_reads_grep = getNumberOfContigs(file_cat.name)
        rnaseqdata["phase 1;_grep"] = {
            "name": "number reads after grep",
            "info": "found %s sequences (vs %s; %s %%)"
            % (
                nb_reads_grep,
                clone["reads"][0],
                round((nb_reads_grep * 100) / clone["reads"][0], 2),
            ),
        }
        rnaseqdata["phase 2;_minia"] = {
            "name": "number of read after minia",
            "info": "found %s sequence(s)" % nb_contigs,
        }
        if not no_clone:
            nclone = ndata["clones"][0]
            nclone["seg"]["phase 1;_grep"] = {
                "name": "number reads after grep",
                "info": "found %s sequences (vs %s; %s %%)"
                % (
                    nb_reads_grep,
                    clone["reads"][0],
                    round((nb_reads_grep * 100) / clone["reads"][0], 2),
                ),
            }
            nclone["seg"]["phase 2;_minia"] = {
                "name": "number of read after minia",
                "info": "found %s sequence(s)" % nb_contigs,
            }
            clone = fusionClone(clone, nclone, rnaseqdata)

    return clone, files_to_del


def getNumberOfContigs(finame):
    fi = open(finame, "r")
    x_minia = 0
    for line in fi:
        if ">" in line:
            x_minia += 1
    return x_minia


def fusionClone(old, new, rnaseqdata):
    """
    old: old data of clonotype (as getted in the fisrt vidjil algo call)
    new: new data of clonotype (as getted after contig)
    rnaseqData: dict
    """
    print("fusionClone(old, new)")
    # with same parameters, both clone should have the same id
    if old["id"] != new["id"]:
        warn = "Clones don't share the same id"
        putWarningInClone(old, warn, "contigs_id", "warn")
        print("WARNING: %s" % warn)
        return old
    if len(new["sequence"]) <= len(old["sequence"]):
        warn = "new clone have shorter sequence than previous"
        putWarningInClone(old, warn, "contigs_shorter", "alert")
        print("WARNING: %s" % warn)
        return old
    # Add a warning message
    putWarningInClone(
        old,
        "clone have been manipulate by preprocessing (rnaseq_longer_reads)",
        "contigs_process",
        "",
    )

    # save old data
    old["previous_seg"] = old["seg"]
    old["previous_name"] = old["name"]
    # change to new data
    old["seg"] = new["seg"]
    old["name"] = new["name"]
    rnaseqdata["length sequence"] = {
        "info": "from %s to %snt (+%s)"
        % (
            len(old["sequence"]),
            len(new["sequence"]),
            len(new["sequence"]) - len(old["sequence"]),
        )
    }
    rnaseqdata["previous sequence"] = {"info": old["sequence"]}
    rnaseqdata["old evalue"] = old["previous_seg"]["evalue"]
    rnaseqdata["old evalue_right"] = old["previous_seg"]["evalue_right"]
    rnaseqdata["old evalue_left"] = old["previous_seg"]["evalue_left"]

    old["seg"]["length sequence"] = {
        "info": "from %s to %snt (+%s)"
        % (
            len(old["sequence"]),
            len(new["sequence"]),
            len(new["sequence"]) - len(old["sequence"]),
        )
    }
    old["seg"]["previous sequence"] = {"info": old["sequence"]}

    if not "5" in old["previous_seg"] or not "5" in old["seg"]:
        warn = "Clone without segmentation"
        putWarningInClone(old, warn, "contigs_no_seg", "alert")
    else:
        if old["previous_seg"]["5"]["name"] == old["seg"]["5"]["name"]:
            rnaseqdata["old V gene (or 5')"] = {"info": "---"}
        else:
            rnaseqdata["old V gene (or 5')"] = old["previous_seg"]["5"]
            warn = "new clone have different Vgene (previous/%s vs current/%s)" % (
                old["previous_seg"]["5"]["name"],
                old["seg"]["5"]["name"],
            )
            putWarningInClone(old, warn, "contigs_gene_V", "warn")
        if old["previous_seg"]["3"]["name"] == old["seg"]["3"]["name"]:
            rnaseqdata["old J gene (or 3')"] = {"info": "---"}
        else:
            rnaseqdata["old J gene (or 3')"] = old["previous_seg"]["3"]
            warn = "new clone have  different Jgene (previous/%s vs current/%s)" % (
                old["previous_seg"]["3"]["name"],
                old["seg"]["3"]["name"],
            )
            putWarningInClone(old, warn, "contigs_gene_J", "warn")

    old["seg_rnaseq_contig"] = rnaseqdata
    old["sequence"] = new["sequence"]
    return old


def putWarningInClone(clone, msg, code, level):
    """
    Put a new warning into the clone
    """
    if not "warn" in clone.keys():
        clone["warn"] = []
    clone["warn"].append(
        {"msg": "%s; %s" % (PREPROCESS, msg), "code": code, "level": level}
    )
    return clone


def cleanDirectory(files):
    """
    Remove a list of temporary files from the tmp directory
    """
    print("=== list files to delete:")
    if args.clean:
        print(files)
        for file in files:
            print("... delete file: %s" % file)
            try:
                file.close()
            except:
                pass
            try:
                os.system("rm -r %s*" % file)
            except:
                print("error while deleting '%s' file" % file)
    else:
        print("... keep temp files asked: %s" % files)
    return


############################################################
### command line, initial msg

if __name__ == "__main__":

    print("#", " ".join(sys.argv))

    DESCRIPTION = "This script is experimental. It allow to build a longer contigs from top clone of a vidjil file."
    DESCRIPTION += "Work with various step (grep on reads with correct id, contigs creation with minia (de novo assembler) and new vidjil analysis with longer read"

    #### Argument parser (argparse)

    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        epilog="""Example:
  python %(prog)s --input filein.vidjil --ouput fileout.vidjil""",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    group_options = parser.add_argument_group()  # title='Options and parameters')
    group_options.add_argument("-i", "--input", help="Vidjil input file")
    group_options.add_argument(
        "-o", "--output", help="Vidjil output file with longer reads for RNAseq"
    )
    group_options.add_argument(
        "-d", "--directory", default="/tmp/", help="Vidjil output directory"
    )
    group_options.add_argument(
        "--silent",
        action="store_false",
        default=True,
        help="run script in silent verbose mode",
    )
    group_options.add_argument(
        "--clean",
        action="store_false",
        default=True,
        help="Clean directory of temporary file after running",
    )
    group_options.add_argument(
        "--adaptater-length",
        type=int,
        default=0,
        help="Length of UMI marker that need to be deleted before analysis by minia",
    )

    args = parser.parse_args()

    inf = args.input
    outf = args.output
    msgs = args.silent
    adaptater = args.adaptater_length
    directory = args.directory
    print("silent: %s" % msgs)

    ## read input file
    #! input can be a concateantion as "pathpreprocess,pathfile" (see issue #4904)
    if "," in inf:
        inf = inf.split(",")[0]
    if msgs:
        print("Reading input file: %s" % inf)

    with open(inf) as inp:
        data = json.load(inp)

    start = time.time()

    # process data
    data = analyse(data, directory, adaptater)

    # write output file
    # print( outf )
    with open(outf, "w") as of:
        print(json.dumps(data, sort_keys=True, indent=2), file=of)
    print("time taken: %s" % (time.time() - start))
