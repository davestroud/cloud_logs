import csv
import random
from datetime import datetime, timedelta, timezone

# Define the UTC timezone object
UTC = timezone.utc

# Define a consistent set of users
users = [
    {
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

# Define possible HTTP methods and corresponding response codes
http_methods = [("GET", "200"), ("PUT", "201"), ("DELETE", "204"), ("POST", "200"), ("HEAD", "200")]

# Function to get a random user
def get_random_user():
    return random.choice(users)["userIdentity"]

# Function to generate a random time within the last two weeks
def random_time_within_last_two_weeks():
    now = datetime.now(UTC)
    random_seconds = random.randint(0, 14 * 24 * 60 * 60)  # Number of seconds in two weeks
    random_time = now - timedelta(seconds=random_seconds)
    return random_time.strftime("[%d/%b/%Y:%H:%M:%S +0000]")

# Function to generate a synthetic S3 access log entry
def generate_s3_access_log():
    bucket_name = random.choice(["my-bucket", "logs-bucket", "data-bucket", "archive-bucket"])
    ip_address = f"203.0.113.{random.randint(0, 255)}"
    file_name = f"file{random.randint(1, 1000)}.txt"
    timestamp = random_time_within_last_two_weeks()
    request_id = f"{random.randint(1000000000000000, 9999999999999999)}"
    
    # Select HTTP method and corresponding status code
    http_method, status_code = random.choice(http_methods)
    
    bytes_sent = random.randint(1000, 50000)
    request_time = random.randint(10, 500)
    user_agent = random.choice([
        "Mozilla/5.0", 
        "curl/7.68.0", 
        "aws-sdk-go/1.32.5 (go1.13; linux; amd64)",
        "aws-sdk-java/1.11.1"
    ])

    # Get a consistent user for this S3 access event
    user = get_random_user()

    log_entry = {
        'request_id': request_id,
        'ip_address': ip_address,
        'timestamp': timestamp,
        'bucket_name': bucket_name,
        'file_name': file_name,
        'http_method': http_method,
        'status_code': status_code,
        'bytes_sent': bytes_sent,
        'request_time': request_time,
        'user_agent': user_agent,
        'user': user['userName']
    }
    
    return log_entry

# Function to write S3 access logs to a CSV file
def write_s3_access_logs_to_csv(filename, num_records=10000):
    fieldnames = ['request_id', 'ip_address', 'timestamp', 'bucket_name', 'file_name', 'http_method', 'status_code', 'bytes_sent', 'request_time', 'user_agent', 'user']
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for _ in range(num_records):
            log = generate_s3_access_log()
            writer.writerow(log)

# Generate and write 10,000 S3 Access logs with consistent user identities to a CSV file
write_s3_access_logs_to_csv('/Users/davidstroud/cloud_logs/data/s3_logs.csv', 10000)
