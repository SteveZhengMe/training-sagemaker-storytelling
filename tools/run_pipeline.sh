#! /bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <pipeline Scenario #>"
    echo "Ex. use "1" to run DWAPipeline-Scenario-1"
    exit 1
fi

# run the pipeline with the processed JSON file
aws sagemaker start-pipeline-execution \
    --pipeline-name "DWAPipeline-Scenario-$1" \
    --pipeline-execution-display-name "DWAPipeline-Scenario-$1-$(date +%Y%m%d-%H%M%S)" \
    --pipeline-execution-description "See code at "playground_dwa" branch in https://github.com/SteveZhengMe/training-sagemaker-storytelling" \
