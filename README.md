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

### DynamoDB
Created table and access permissions. Because DynamoDB does not have a specific dateTime type, use a string in the format YYYY-MM-DD
```
aws dynamodb create-table \
  --table-name StockChangeDailyData \
  --attribute-definitions \
    AttributeName=date,AttributeType=S \
  --key-schema \
    AttributeName=date,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
  --table-class STANDARD


aws iam attach-role-policy \
  --role-name dailyTableUpdate-exec \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
```

Test: Same as before table update was added. Uses this code to backfill a few days of data, and to ensure that the table does not add dupicate rows on queries with a repeated date, or dummy rows for non-business days which have no data. 
```
aws lambda invoke \
  --function-name dailyTableUpdate \
  --payload file://payload.json \
  --cli-binary-format raw-in-base64-out \
  response.json
```

Changed the timeout from 3 to 10 seconds due to a Sandbox.Timedout error. (10 to be generous)
```
aws lambda update-function-configuration \
  --function-name dailyTableUpdate \
  --timeout 10 
```   

### getMoversData lambda function creation from AWS CLI
Same basic lambda creation and updates as above. 
Test:
```
aws lambda invoke \
  --function-name getMoversData \
  output.json
```

### Add API Gateway
```
aws apigatewayv2 create-api \
  --name movers-api \
  --protocol-type HTTP

aws apigatewayv2 create-integration \
  --api-id cbvbq2ei92 \
  --integration-type AWS_PROXY \
  --integration-uri arn:aws:lambda:us-west-2:<ACCOUNT_ID>:function:getMoversData \
  --payload-format-version 2.0

aws apigatewayv2 create-route \
  --api-id cbvbq2ei92 \
  --route-key "GET /movers" \
  --target integrations/<INTEGRATION ID>

aws apigatewayv2 create-stage \
  --api-id cbvbq2ei92 \
  --stage-name prod \
  --auto-deploy

aws lambda add-permission \
  --function-name getMoversData \
  --statement-id apigateway-access \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-west-2:<ACCOUNT_ID>:cbvbq2ei92/*/*"
```

Test:

```
aws apigatewayv2 get-api \
  --api-id cbvbq2ei92

curl https://cbvbq2ei92.execute-api.us-west-2.amazonaws.com/prod/movers
```

### Frontend with Amplify
After initializing Vite app and writing the code. 

Typically, I would put the frontend in its own repo, rather than in this one. Because I put it in this, I ran 
into some issues with the Github-connected CI/CD deployment I was originall planning. 
I worked around it by manually deploying it:

```
aws amplify create-app \
  --name stock-movers

aws amplify create-branch \
  --app-id dr1sswvxg7ibm \
  --branch-name main

aws amplify create-deployment \
  --app-id dr1sswvxg7ibm \
  --branch-name main

cd frontend/dist
zip -r ../dist.zip .

cd ..
curl -X PUT "<zip upload URL>" \
  --upload-file dist.zip
  
aws amplify start-deployment \
  --app-id dr1sswvxg7ibm \
  --branch-name main \
  --job-id 1

aws amplify get-app --app-id dr1sswvxg7ibm
```

App can be accessed at https://main.dr1sswvxg7ibm.amplifyapp.com/