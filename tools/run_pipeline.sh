#! /bin/bash

# use AWS CLI to run the pipeline

# read the first argument as the pipeline name
if [ -z "$1" ]; then
    echo "Usage: $0 <pipeline-name>"
    echo "<pipeline-name> list:"
    echo "- DWAPipeline-Simple-Run"
    exit 1
fi

# get the folder of this file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

JSON_FILE="$SCRIPT_DIR/$1.json"
ENV_FILE="$SCRIPT_DIR/../.env"

# Check if the JSON file exists
if [ ! -f "$JSON_FILE" ]; then
    echo "Error: JSON file '$JSON_FILE' does not exist."
    exit 1
fi

# check if the .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file '$ENV_FILE' does not exist."
    exit 1
fi

# clean up the last run
rm "$SCRIPT_DIR/$1-processed.json"

TEMP_JSON=$(mktemp)
cp "$JSON_FILE" "$TEMP_JSON"

# loop .env file and replace the values in the JSON file
while IFS='=' read -r key value || [ -n "$key" ]; do
    # skip empty lines and comments
    if [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]]; then
        continue
    fi
    
    # remove leading and trailing whitespace
    key=$(echo "$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    value=$(echo "$value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    
    search_pattern="\\[$key\\]"
    
    if grep -q "$search_pattern" "$TEMP_JSON"; then
        escaped_value=$(echo "$value" | sed 's/[[\.*^$()+?{|]/\\&/g')
        sed -i "s/$search_pattern/$escaped_value/g" "$TEMP_JSON"
    fi
done < "$ENV_FILE"

mv "$TEMP_JSON" "$SCRIPT_DIR/$1-processed.json"

# run the pipeline with the processed JSON file
aws sagemaker start-pipeline-execution \
    --pipeline-name "$1" \
    --pipeline-execution-display-name "$1-$(date +%Y%m%d-%H%M%S)" \
    --pipeline-execution-description "See code at "playground_dwa" branch in https://github.com/SteveZhengMe/training-sagemaker-storytelling" \
    --pipeline-parameters file://$SCRIPT_DIR/$1-processed.json \

