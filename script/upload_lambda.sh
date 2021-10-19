#!/usr/bin/env bash

# Upload the code to Lambda
# Usage: ./upload_lambda.sh

# A .env file is expected in the parent directory defining $LAMBDA_NAME
source ../.env

ZIP_FILE="lambda_function.zip"

# archive the function
zip -j $ZIP_FILE ../src/lambda_function.py

# upload to AWS
aws lambda update-function-code --function-name $LAMBDA_NAME --zip-file fileb://$ZIP_FILE

# delete the archive
rm $ZIP_FILE