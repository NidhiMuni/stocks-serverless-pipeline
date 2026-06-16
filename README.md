# Stocks Serverless Pipeline


### dailyTableUpdate lambda function creation from AWS CLI
```
aws configure
```

```
aws iam create-role \
    --role-name dailyTableUpdate-exec \
    --assume-role-policy-document \
    file://policy.json

aws iam attach-role-policy \
  --role-name dailyTableUpdate-exec \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

```
zip dailyTableUpdate_function.zip dailyTableUpdate_lambda.py

aws lambda create-function \
  --function-name dailyTableUpdate \
  --runtime python3.11 \
  --role arn:aws:iam::<ACCOUNT_ID>:role/dailyTableUpdate-exec \
  --handler dailyTableUpdate_lambda.dailyTableUpdate_handler \
  --zip-file fileb://dailyTableUpdate_function.zip
```

Test
``` 
aws lambda invoke \
  --function-name dailyTableUpdate \
  output.json
```

#### Update 2: Add business logic to calculate highest stock percentage
To update Lambda function with new code:
```
zip dailyTableUpdate_function.zip dailyTableUpdate_lambda.py

aws lambda update-function-code \
  --function-name dailyTableUpdate \
  --zip-file fileb://dailyTableUpdate_function.zip

```

Test:
Update payload.json with a business day date in the format yyyy-mm-dd.
```
aws lambda invoke \
  --function-name dailyTableUpdate \
  --payload file://payload.json \
  --cli-binary-format raw-in-base64-out \
  response.json
```

Massive API key was added to AWS Secret Manager like this:
```
aws secretsmanager create-secret \
  --name massive-api-key \
  --secret-string "<API KEY>"

aws iam attach-role-policy \      
  --role-name dailyTableUpdate-exec \
  --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite
```
