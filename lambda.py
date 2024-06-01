#### LAMBDA 1

import json
import boto3
import base64

S3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    
    print(event)
    
    
    
    key = event['s3_key']
    bucket = event['s3_bucket']
    
    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    S3.download_file(bucket, key, '/tmp/image.png')
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }



#### LAMBDA 2 ######################################################

import json
import sagemaker
import base64
from sagemaker.serializers import IdentitySerializer

# Fill this in with the name of your deployed model
ENDPOINT = 'image-classification-2024-05-30-18-01-13-009'  # TODO: fill in

def lambda_handler(event, context):

    # Decode the image data
    
    event = event['body']
    image = base64.b64decode(event['image_data'])

    # Instantiate a Predictor
    session = sagemaker.Session()
    predictor = sagemaker.predictor.Predictor(ENDPOINT, sagemaker_session=session)

    # For this model, the IdentitySerializer needs to be "image/png"
    predictor.serializer = IdentitySerializer("image/png")
    
    # Make a prediction
    inferences = predictor.predict(image)
    
    # We return the data back to the Step Function
    event["inferences"] = inferences.decode('utf-8')
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }






#### LAMBDA 3 ###########################################################


import json


THRESHOLD = .93


def lambda_handler(event, context):
    
    # Grab the inferences from the event
    print(event)
    event = json.loads(event['body'])## TODO: fill in
    inferences =  json.loads(event['inferences'])
    print()
    print(inferences[0], inferences[1])
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = True if (float(inferences[0])>THRESHOLD or float(inferences[1])>THRESHOLD) else False ## TODO: fill in
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }