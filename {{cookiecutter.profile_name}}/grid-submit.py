#!/usr/bin/env python3

import sys
import htcondor
from os import makedirs
from os.path import join
from uuid import uuid4

from snakemake.utils import read_job_properties

def fix_apptainer_args(jobscript):
  with open(jobscript, "r") as f:
    js = f.read()

  js = js.replace('--writable-tmpfs', '"--writable-tmpfs "')

  with open(jobscript, "w") as f:
    f.write(js)

jobscript = sys.argv[1]
fix_apptainer_args(jobscript)
job_properties = read_job_properties(jobscript)

UUID = uuid4()  # random UUID
jobDir = "/home/hep/mdk16/PhD/EFT2Obs-Workflow/.condor_jobs/{}_{}".format(job_properties["jobid"], UUID)
makedirs(jobDir, exist_ok=True)

sub = htcondor.Submit(
    {
        "executable": "/bin/bash",
        "arguments": jobscript,
        "max_retries": "1",
        "log": join(jobDir, "condor.log"),
        "output": join(jobDir, "condor.out"),
        "error": join(jobDir, "condor.err"),
        "getenv": "True",
        "request_cpus": str(job_properties["threads"]),
    }
)

request_memory = job_properties["resources"].get("mem_mb", None)
if request_memory is not None:
    sub["request_memory"] = str(request_memory)

request_disk = job_properties["resources"].get("disk_mb", None)
if request_disk is not None:
    sub["request_disk"] = str(request_disk)

runtime = job_properties["resources"].get("runtime", None)
if runtime is not None:
   sub["+MaxRuntime"] = str(runtime*60) # convert minutes to seconds

schedd = htcondor.Schedd()
clusterID = schedd.submit(sub)

# print jobid for use in Snakemake
print("{}_{}_{}".format(job_properties["jobid"], UUID, clusterID))
