import boto3
from botocore.exceptions import ClientError

bucket_name = "momi-rag-bucket-2026-12345"
region = "us-east-1"

s3 = boto3.client("s3", region_name=region)

try:
    s3.create_bucket(Bucket=bucket_name)

    print(f"Bucket created: {bucket_name}")

except ClientError as e:
    print(e)

# new service

polly = boto3.client("polly")

response = polly.synthesize_speech(
    Text="Hello! Welcome to our AI course.",
    OutputFormat="mp3",
    VoiceId="Joanna"
)

with open("welcome.mp3", "wb") as f:
    f.write(response["AudioStream"].read())

    # new service

translate = boto3.client("translate", region_name="us-east-1")

result = translate.translate_text(
    Text="Welcome to the AI engineering Course!",
    SourceLanguageCode="en",
    TargetLanguageCode="he"
)

print(result["TranslatedText"])