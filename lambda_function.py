import json
import boto3
from botocore.exceptions import ClientError
import constants as cnst
from boto3.dynamodb.conditions import Key, Attr
from PIL import image
import PIL
from io import BytesIO
from os import path
#Steps:
#   Trigger on put into s3 upload buffer 
#   Transform down to smaller
#   Upload to new s3 directory
#   Put metadata into table

def lambda_handler(event, context):

    for key in event.get('Records'):
        object_key = key['s3']['object']['key']
        extension = path.splitext(object_key)[1].lower()

        # Grabs the source file
        obj = s3.Object(
            bucket_name=origin_bucket,
            key=object_key,
        )
        obj_body = obj.get()['Body'].read()
    
        # Checking the extension and
        # Defining the buffer format
        if extension in ['.jpeg', '.jpg']:
            format = 'JPEG'
        if extension in ['.png']:
            format = 'PNG'

        # Resizing the image
        img = Image.open(BytesIO(obj_body))
        wpercent = (width_size / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((width_size, hsize), PIL.Image.ANTIALIAS)
        buffer = BytesIO()
        img.save(buffer, format)
        buffer.seek(0)

        # Uploading the image
        obj = s3.Object(
            bucket_name=destination_bucket,
            key=object_key,
        )
        obj.put(Body=buffer)

        # Printing to CloudWatch
        print('File saved at {}/{}'.format(
            destination_bucket,
            object_key,
        ))



    dynamo = boto3.resource('dynamodb')
    
    s3 = boto3.client('s3')
    bucket = cnst.user_images_bucket_name
    table_name = cnst.users_table_name
    file_name = event['file_name']

    #Check if image exists on S3 Buffer Directory
    file_key = cnst.s3_images_buffer_key + "/"+file_name
    try:
        #Amazon S3/artifyc-user-images-qa/upload-buffer/logo.png

        s3.head_object(Bucket=cnst.user_images_bucket_name, Key=file_key)
    except ClientError as e:
        # Not found
        print(e)
        return "Error Occurred Queryimg for image in buffer"
    
    
    #Get user path from dynamodb for s3. Also Check if user exists
    user_id = event['user_id']
    table = dynamo.Table('Users')

    try:
        user_object = table.query(
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
        print(user_object)
        user_image_s3_path = user_object['Items'][0]['s3_images_path']
    except ClientError as e:
        print(e)
        return e
        #Error Occurred

    #Get s3 key from user_info
    #user_image_s3_path = user_object['s3_images_path']
    
    #Download Image
    try:
        image = s3.get_object(Bucket=cnst.user_images_bucket_name, Key=file_key)
    except ClientError:
        return "Error occurred downloading image"
    print(image)
    
    #Transform Image using PILLOW
    
    #Move image from buffer directory to user's image directory if it doesn't go over size limit
    try:
        s3.upload_file(image, bucket, user_image_s3_path)
    except ClientError:
        pass
    return "early cut off test"
    #Upload image metadata
    image_id = "test" 
    
    #Generate UUID for image

    dynamo.put_item(
        Table_Name='',
        Item = {
            'user_id' : {'S': user_id},
            'image_id' : {'S': image_id},
            'uploaded_timestamp' : {'S': current_timestamp},
            'tags' : {'S': tags_list},
        }
    )
    
    #Might need to query user to get timestamp from user db before updating.
    #Or redo user with no sort key
 
    #Update user metadata if needed
    dynamo.update_item(
        Table_Name='',
        Key = {
            'user_id':'',
        },
        AttributeUpdates={
        'yeet': '123',
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Image Successfully Uploaded!')
    }