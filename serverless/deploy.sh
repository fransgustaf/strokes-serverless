cp ../../strokes_django/strokes/models.py shared_files/strokes/
cp requirements.txt input/requirements.txt; cp requirements.txt recogniser/requirements.txt

sam build
sam package --output-template-file packaged.yaml --s3-bucket fs-deploy-lambda-functions
sam deploy --template-file packaged.yaml --stack-name serverless --capabilities CAPABILITY_IAM
aws cloudformation describe-stack-events --stack-name serverless | grep -i error
