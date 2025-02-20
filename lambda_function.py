# import boto3
import json

def lambda_handler(event, context):
    # s3 = boto3.client('s3')
    # listObjSummary = s3.list_buckets()
    # lista=[]
    # for objSum in listObjSummary['Buckets']:
    #     lista.append(objSum['Name'])
    #     print(objSum)

    return {
        'statusCode': 200,
        'body': json.dumps('Hola mundo')
    }
# import boto3
import json

def lambda_handler(event, context):
    # s3 = boto3.client('s3')
    # listObjSummary = s3.list_buckets()
    # lista=[]
    # for objSum in listObjSummary['Buckets']:
    #     lista.append(objSum['Name'])
    #     print(objSum)

    return {
        'statusCode': 200,
        'body': json.dumps('Hola mundo 6')
    }
