import csv
import random
import time
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

# Function to get a random user
def get_random_user():
    return random.choice(users)["userIdentity"]

# Function to generate a random time within the last two weeks (in seconds since epoch)
def random_time_within_last_two_weeks():
    now = time.time()
    random_seconds = random.randint(0, 14 * 24 * 60 * 60)  # Number of seconds in two weeks
    return int(now - random_seconds)

# Function to generate synthetic VPC Flow Logs
def generate_vpc_flow_logs(num_records=10000):
    flow_logs = []

    for _ in range(num_records):
        start_time = random_time_within_last_two_weeks()
        end_time = start_time + random.randint(10, 100)  # End time is shortly after start time

        # Use the same user for VPC flow log activity
        user = get_random_user()

        log = {
            'Version': 2,
            'AccountId': user["accountId"],
            'InterfaceId': f'eni-{random.randint(10000, 99999)}',
            'SrcAddr': f'192.168.{random.randint(0, 255)}.{random.randint(0, 255)}',
            'DstAddr': f'172.31.{random.randint(0, 255)}.{random.randint(0, 255)}',
            'SrcPort': random.randint(1, 65535),
            'DstPort': random.randint(1, 65535),
            'Protocol': random.choice([6, 17]),  # 6 for TCP, 17 for UDP
            'Packets': random.randint(1, 100),
            'Bytes': random.randint(500, 10000),
            'StartTime': start_time,
            'EndTime': end_time,
            'Action': random.choice(['ACCEPT', 'REJECT']),
            'LogStatus': 'OK',
            'User': user["userName"]  # Adding consistent user identity
        }
        flow_logs.append(log)

    return flow_logs

# Function to write VPC Flow Logs to a CSV file
def write_vpc_flow_logs_to_csv(filename, logs):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=logs[0].keys())
        writer.writeheader()
        writer.writerows(logs)

# Generate 10,000 synthetic VPC Flow Logs with consistent user identities and write to CSV
vpc_logs = generate_vpc_flow_logs(10000)
write_vpc_flow_logs_to_csv('data/vpc_flow_logs.csv', vpc_logs)