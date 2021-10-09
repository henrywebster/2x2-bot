# 2x2-bot
Repository for the backend code being used by the 2x2 Twitter bot.

## How to Use

### Set up an S3 bucket and DynamoDB database
The S3 bucket will store the image files that are posted to Twitter.
![image](https://user-images.githubusercontent.com/14267649/136667058-45db7e41-5089-488e-80c5-5924e0b1f20b.png)

The DynamoDB table will keep track of which images have been posted and what the corresponding S3 object name is.
The AWS Lambda function will pick an entry from this table and update the status as posted so there are no repeats.
![image](https://user-images.githubusercontent.com/14267649/136667132-10810edb-ad53-40c1-92a0-248acd1c986a.png)

### Create the AWS Lambda function
The code used is provided in the ```src/lambda_function.py``` file. The function can be created with default permissions and needed S3 and DynamoDB entries can be added later.

Because the code uses 3rd party libraries, they must be included as an AWS Lambda Layer. To create the layer, use the following command to include everything in the ```requirements.txt``` file (Docker is required):

```docker run -v "$PWD":/var/task "lambci/lambda:build-python3.8" /bin/sh -c "pip install -r requirements.txt -t python/lib/python3.8/site-packages/; exit"```

Next, zip up the directory:

```zip -r layer.zip python```

Create a new layer an upload the ```layer.zip``` file:
![image](https://user-images.githubusercontent.com/14267649/136667602-734349aa-64a5-4429-a10b-db52a4618ed7.png)

Add the layer to the function:
![image](https://user-images.githubusercontent.com/14267649/136667665-2c218578-1331-4145-b067-88937dc642ce.png)

Inside the ```src``` directory, create a zip archive of the code:

```zip ../lambda_function.zip * -x "__pycache__*"```

Upload the archive to AWS Lambda:
![image](https://user-images.githubusercontent.com/14267649/136667734-4cc3e9fe-fd03-4901-ae0e-d45e77413737.png)

Set up environment variables:
|ACCESS_TOKEN|Access token from the Twitter API|
|ACCESS_TOKEN_SECRET|Access token secret from the Twitter API|
|CONSUMER_KEY|API key from the Twitter API|
|CONUMER_SECRET|API key secret from the Twitter API|
|DB_TABLE_NAME|DynamoDB table name|
|S3_BUCKET_NAME|S3 bucket name|

![image](https://user-images.githubusercontent.com/14267649/136667879-617eee4f-b68c-4f5c-bce0-251fdb7871fc.png)

To add permissions for the S3 bucket and DynamoDB table, go to the permissions section and click on the role. Edit the policy and add additional permissions for DynamoDB and S3. Use the exact ARN from each and allow only minimum permissions.
*DynamoDB:* GetItem, Query, Scan, UpdateItem
*S3:*: GetObject

Now the function is ready to use. 


# TODO
* The function is taking a long time, mostly from downloading the photo from S3. I am not too concerned because the function runs very infrequently. I would still like to see if I can shorten execution time.
* I would like the triggering event to automatically pause the schedule if it detects there are no unposted entries in the database.
* Create scripts that upload the photo to S3 and add a corresponding entry to the database.
* Develop a web app front-end to view what is in the database quickly and upload new squares.
* Develop a mobile app that scans, crops, and uploads to the database.
* Create a CloudFormation template that can create all the resources.
