import csv
import random
import datetime

# Define the UTC timezone object
UTC = datetime.timezone.utc

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

# Function to generate a random time within the last two weeks
def random_time_within_last_two_weeks():
    now = datetime.datetime.now(UTC)
    random_seconds = random.randint(0, 14 * 24 * 60 * 60)  # Number of seconds in two weeks
    random_time = now - datetime.timedelta(seconds=random_seconds)
    return random_time.isoformat() + "Z"

# Function to generate Lambda logs
def generate_lambda_logs(num_records=10000):
    lambda_logs = []

    for _ in range(num_records):
        request_id = f"{random.randint(1000, 9999)}abcd-{random.randint(1000, 9999)}-efgh-ijkl-{random.randint(1000, 9999)}mnop"
        
        # Generate a start log with a random timestamp within the last two weeks
        start_time = random_time_within_last_two_weeks()
        
        # Use the same user for Lambda activity
        user = get_random_user()

        lambda_logs.append({
            'timestamp': start_time,
            'request_id': request_id,
            'log_type': 'START',
            'message': f"RequestId: {request_id} Version: $LATEST User: {user['userName']}"
        })
        
        # Generate log entries with random timestamps, types, and messages
        for _ in range(random.randint(1, 5)):  # Generate between 1 and 5 log entries per invocation
            timestamp = random_time_within_last_two_weeks()
            log_type = random.choice(['INFO', 'ERROR', 'DEBUG', 'WARN'])
            log_message = random.choice([
                "Processing event",
                "Fetching data from database",
                "Failed to fetch data from database: TimeoutError",
                "Data validation error: Invalid format",
                "Unauthorized access attempt detected",
                "Memory limit exceeded",
                "Rate limit exceeded: Too many requests",
                "Dependency service unavailable",
                "Failed to upload file: NetworkError",
                "Exceeded maximum retry attempts",
                f"User {user['userName']} failed to access restricted resource."
            ])
            lambda_logs.append({
                'timestamp': timestamp,
                'request_id': request_id,
                'log_type': log_type,
                'message': log_message
            })
        
        # Generate an end log and a report log with random values for durations and memory usage
        end_time = random_time_within_last_two_weeks()
        duration = random.randint(100, 5000)
        billed_duration = random.randint(duration, 5000)  # Billed duration is always equal to or greater than actual duration
        memory_size = random.choice([128, 256, 512])
        max_memory_used = random.randint(64, memory_size)
        
        lambda_logs.append({
            'timestamp': end_time,
            'request_id': request_id,
            'log_type': 'END',
            'message': f"RequestId: {request_id} User: {user['userName']}"
        })
        
        lambda_logs.append({
            'timestamp': end_time,
            'request_id': request_id,
            'log_type': 'REPORT',
            'message': f"Duration: {duration} ms Billed Duration: {billed_duration} ms Memory Size: {memory_size} MB Max Memory Used: {max_memory_used} MB User: {user['userName']}"
        })
    
    return lambda_logs

# Function to write Lambda logs to a CSV file
def write_lambda_logs_to_csv(filename, logs):
    fieldnames = ['timestamp', 'request_id', 'log_type', 'message']
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(logs)

# Generate 10,000 synthetic Lambda Logs and write to a CSV file
lambda_logs = generate_lambda_logs(10000)
write_lambda_logs_to_csv('data/lambda_logs.csv', lambda_logs)