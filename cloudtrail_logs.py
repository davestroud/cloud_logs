import json
import random
import datetime
import pandas as pd
from pandas import json_normalize

#TODO: Add root user for user identity type
# Define a consistent set of users
users = [
    {+
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AID1234567890",
            "arn": "arn:aws:iam::123456789012:user/test-user",
            "accountId": "123456789012",
            "accessKeyId": "ASIA1234567890",
            "userName": "test-user"
        }
    },
    {
        "userIdentity": {
            "type": "AssumedRole",
            "principalId": "AID0987654321",
            "arn": "arn:aws:iam::123456789012:user/admin",
            "accountId": "123456789012",
            "accessKeyId": "ASIA0987654321",
            "userName": "admin"
        }
    },
    {
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AID5678901234",
            "arn": "arn:aws:iam::123456789012:user/dev-user",
            "accountId": "123456789012",
            "accessKeyId": "ASIA5678901234",
            "userName": "dev-user"
        }
    }
]

# Function to get a random user
def get_random_user():
    return random.choice(users)["userIdentity"]

# Function to generate a random time within the last two weeks
def random_time_within_last_two_weeks():
    now = datetime.datetime.now(datetime.timezone.utc)
    random_seconds = random.randint(0, 14 * 24 * 60 * 60)
    random_time = now - datetime.timedelta(seconds=random_seconds)
    return random_time.isoformat()

# Function to generate a random CloudTrail log
def generate_cloudtrail_log():
    # Generate a random event time within the last two weeks
    event_time = random_time_within_last_two_weeks()
    
    # Get a random user from the consistent set of users
    user = get_random_user()

    cloudtrail_log = {
        "eventVersion": "1.08",
        "userIdentity": user,
        "eventTime": event_time,
        "eventSource": random.choice(["ec2.amazonaws.com", "s3.amazonaws.com", "rds.amazonaws.com", "lambda.amazonaws.com"]),
        "eventName": random.choice(["StartInstances", "StopInstances", "RebootInstances", "CreateBucket", "DeleteBucket", "InvokeFunction", "UnauthorizedAccess", "FailedLogin"]),
        "awsRegion": random.choice(["us-east-1", "us-west-2", "eu-central-1", "ap-south-1"]),
        "sourceIPAddress": "{}.{}.{}.{}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
        "userAgent": random.choice([
            "aws-cli/2.0.0 Python/3.8.0 Linux/5.4.0-1031-aws",
            "aws-sdk-java/1.11.1 Mac_OS_X/10.14.6 Java_HotSpot(TM)_64-Bit_Server_VM/25.192-b12",
            "aws-sdk-go/1.32.5 (go1.13; linux; amd64)",
            "aws-cli/1.16.220 Python/3.7.3 Darwin/18.6.0 botocore/1.12.210"
        ]),
        "requestParameters": {
            "instancesSet": {
                "items": [{"instanceId": "i-{}".format(random.randint(1000000000, 9999999999))}]
            }
        },
        "responseElements": {
            "instancesSet": {
                "items": [
                    {
                        "instanceId": "i-{}".format(random.randint(1000000000, 9999999999)),
                        "currentState": {
                            "code": random.choice([0, 16, 32, 48, 64, 80]),
                            "name": random.choice(["pending", "running", "shutting-down", "terminated", "stopping", "stopped"])
                        },
                        "previousState": {
                            "code": random.choice([0, 16, 32, 48, 64, 80]),
                            "name": random.choice(["pending", "running", "shutting-down", "terminated", "stopping", "stopped"])
                        }
                    }
                ]
            }
        },
        "requestID": "{}-{}-{}-{}".format(random.randint(1000, 9999), random.randint(1000, 9999), random.randint(1000, 9999), random.randint(1000, 9999)),
        "eventID": "{}-{}-{}-{}".format(random.randint(1000000000, 9999999999), random.randint(1000000000, 9999999999), random.randint(1000000000, 9999999999), random.randint(1000000000, 9999999999))
    }
    
    return cloudtrail_log

# Function to flatten the CloudTrail log
def flatten_json(json_data):
    return json_normalize(json_data)

# Function to write CloudTrail logs to a CSV file
def write_cloudtrail_logs_to_csv(num_records, output_csv_file):
    # Generate CloudTrail logs
    logs = [generate_cloudtrail_log() for _ in range(num_records)]
    
    # Flatten the logs
    flattened_logs = flatten_json(logs)
    
    # Convert the flattened logs to a DataFrame
    df = pd.DataFrame(flattened_logs)
    
    # Write the DataFrame to a CSV file
    df.to_csv(output_csv_file, index=False)

# Generate and write 10,000 CloudTrail logs to a CSV file
write_cloudtrail_logs_to_csv(10000, 'data/cloudtrail_logs.csv')