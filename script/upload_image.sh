#!/usr/bin/env bash

# Upload the image file from local storage to S3 and create an entry in DynamoDB 
# Usage: ./upload_image.sh <file path to image> <title>
# Note: titles with spaces need to be surrounded by double quotes

# A .env file is expected in the parent directory defining $S3_BUCKET_NAME and $DB_TABLE_NAME
source ../.env

FILEPATH=$1
TITLE=$2
OBJECTNAME=$(basename $FILEPATH)
TIME=$(date +%s)

echo $TITLE

# upload to S3
aws s3 cp $FILEPATH s3://$S3_BUCKET_NAME

# make entry in DynamoDB
aws dynamodb put-item --table-name $DB_TABLE_NAME --item "{\"id\": {\"S\": \""$OBJECTNAME"\"}, \"title\": {\"S\": \"$TITLE\"}, \"process_time\": {\"N\": \"$TIME\"}}"