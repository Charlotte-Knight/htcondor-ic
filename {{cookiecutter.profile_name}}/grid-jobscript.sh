#!/bin/bash
# properties = {properties}

set -e
set -x
set +u

echo "hostname:"
hostname -f

{exec_job}
