import json
import decimalencoder
import todoList
import boto3
from botocore.exceptions import ClientError


def translate(event, context):

    item = todoList.get_item(event['pathParameters']['id'])
    if item:
        targetLanguage = event['pathParameters']['language']
        
        # detect language
        try:
            comprehend_client = boto3.client(service_name='comprehend', region_name='us-east-1', use_ssl=True)
            responseComprehend = comprehend_client.detect_dominant_language(Text=item['text'])
            languages = responseComprehend['Languages']
        except ClientError:
            print("Couldn't detect languages.")
            sourceLanguage = 'es'
        else:
            sourceLanguage = languages[0]['LanguageCode']

            #translate item
            translate = boto3.client(service_name='translate', region_name='us-east-1', use_ssl=True)
            result = translate.translate_text(Text=item['text'], SourceLanguageCode=sourceLanguage, TargetLanguageCode=targetLanguage)
            
            print('TranslatedText: ' + result.get('TranslatedText'))
            print('SourceLanguageCode: ' + result.get('SourceLanguageCode'))
            print('TargetLanguageCode: ' + result.get('TargetLanguageCode'))
            
            item['text'] = result.get('TranslatedText')
            
        response = {
            "statusCode": 200,
            "body": json.dumps(item,
                               cls=decimalencoder.DecimalEncoder)
        }
        
    else:
        response = {
            "statusCode": 404,
            "body": ""
        }
    
    return response
