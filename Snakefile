
configfile: "config.json"


rule all:
    input:
        expand(
            f"{config['outdir']}/{config['result_output_template']}",
            sample=glob_wildcards(
                f"{config['indir']}/Fastq/{{sample}}_R1_001.fastq.gz"
            ).sample,
        ),


rule preprocess_merge:
    input:
        f"{config['indir']}/Fastq/{{sample}}_R1_001.fastq.gz",
        f"{config['indir']}/Fastq/{{sample}}_R2_001.fastq.gz",
    output:
        "{outdir}/preprocess-flash/{sample}.fastq.gz",
    threads: 8
    params:
        total_read_size=config.get("total_read_size", 300),
        outdir=lambda wildcards: f"{wildcards.outdir}/preprocess-flash",
    shell:
        """
        flash2 {input} -d {params.outdir} -o {wildcards.sample} -t {threads} --compress -M {params.total_read_size} &&
        cat {params.outdir}/{wildcards.sample}.extendedFrags.fastq.gz {params.outdir}/{wildcards.sample}.notCombined_2.fastq.gz {params.outdir}/{wildcards.sample}.notCombined_1.fastq.gz > {params.outdir}/{wildcards.sample}.fastq.gz &&
        rm {params.outdir}/{wildcards.sample}.extendedFrags.fastq.gz {params.outdir}/{wildcards.sample}.notCombined_1.fastq.gz {params.outdir}/{wildcards.sample}.notCombined_2.fastq.gz
        """


rule preprocess_prefilter:
    input:
        "{outdir}/preprocess-flash/{sample}.fastq.gz",
    output:
        "{outdir}/preprocess-prefilter/{sample}.detected.vdj.fastq.gz",
    params:
        germline_path=config.get("germline_path", "germline"),
        outdir=lambda wildcards: f"{wildcards.outdir}/preprocess-prefilter",
    shell:
        """
        vidjil-algo-2025.02 -g {params.germline_path}/vdj_filter.g --filter-reads --gz --dir {params.outdir} --base {wildcards.sample} {input}
        """


rule vidjil:
    input:
        "{outdir}/preprocess-prefilter/{sample}.detected.vdj.fastq.gz",
    output:
        "{outdir}/vidjil-results/{sample}.vidjil",
    params:
        germline_path=config.get("germline_path", "germline"),
    shell:
        "vidjil-algo-2024.02 -g {params.germline_path}/homo-sapiens.g --base {wildcards.sample} -o {wildcards.outdir}/vidjil-results {input}"


rule vidjil_igh:
    input:
        fq="{outdir}/preprocess-prefilter/{sample}.detected.vdj.fastq.gz",
        vd="{outdir}/vidjil-results/{sample}.vidjil",
    output:
        "{outdir}/vidjil-igh/{sample}.vidjil",
    params:
        tmpdir=lambda wildcards: f"{wildcards.outdir}/vidjil-igh/{wildcards.sample}-tmp",
    shell:
        """
        mkdir -p {params.tmpdir} && python /opt/capture_contigs.py -i {input.vd} -o {output} --clean --adaptater-length 5 -d {params.tmpdir} && rm -R {params.tmpdir}
        """
