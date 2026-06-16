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