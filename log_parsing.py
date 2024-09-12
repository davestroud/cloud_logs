import csv
import json
from datetime import datetime

def parse_ec2_logs(log_entry):
    timestamp, hostname, process, pid, user, log_message = log_entry
    
    # Extract action and resource type from log_message if applicable
    action = "Unknown"
    resource_type = "EC2"
    if "High CPU" in log_message:
        action = "CPU Warning"
    elif "terminated" in log_message:
        action = "TerminateInstance"
    elif "patch" in log_message:
        action = "SecurityPatch"
    
    return {
        "timestamp": timestamp,
        "event_type": "EC2 Log",
        "userIdentity": {"role": "IAMUser", "user": user},
        "source IP": hostname,  # Assuming hostname as the source IP for simplicity
        "region": "us-east-1",  # Can be inferred or left blank
        "response_code": None,  # Not available in EC2 logs
        "resource_type": resource_type,
        "action": action
    }

def parse_lambda_logs(log_entry):
    timestamp, request_id, log_type, message = log_entry
    
    # Extract action based on log_type and message
    action = log_type
    resource_type = "Lambda"
    
    if log_type == "ERROR":
        response_code = "403"
    elif log_type == "START":
        response_code = "200"
    else:
        response_code = None
    
    return {
        "timestamp": timestamp,
        "event_type": "Lambda Log",
        "userIdentity": {"role": "IAMUser", "user": message.split(' ')[-1]},
        "source IP": None,
        "region": "us-east-1",
        "response_code": response_code,
        "resource_type": resource_type,
        "action": action
    }

def parse_s3_logs(log_entry):
    request_id, ip_address, timestamp, bucket_name, file_name, http_method, status_code, bytes_sent, request_time, user_agent, user = log_entry
    
    action = f"S3 {http_method}"
    resource_type = "S3"
    
    return {
        "timestamp": timestamp,
        "event_type": "S3 Log",
        "userIdentity": {"role": "IAMUser", "user": user},
        "source IP": ip_address,
        "region": "us-east-1",  # Can be inferred or added manually
        "response_code": status_code,
        "resource_type": resource_type,
        "action": action
    }

def parse_vpc_logs(log_entry):
    Version, AccountId, InterfaceId, SrcAddr, DstAddr, SrcPort, DstPort, Protocol, Packets, Bytes, StartTime, EndTime, Action, LogStatus, User = log_entry
    
    action = "VPC Flow"
    resource_type = "VPC"
    
    return {
        "timestamp": datetime.utcfromtimestamp(int(StartTime)).strftime('%Y-%m-%d %H:%M:%S'),
        "event_type": "VPC Flow Log",
        "userIdentity": {"role": "IAMUser", "user": User},
        "source IP": SrcAddr,
        "region": "us-east-1",  # Can be inferred or added manually
        "response_code": LogStatus,
        "resource_type": resource_type,
        "action": action
    }

# Parse each log file
def parse_logs():
    structured_logs = []

    # Parse EC2 logs
    with open('data/_creation/ec2_logs.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            structured_logs.append(parse_ec2_logs(row))

    # Parse Lambda logs
    with open('data/_creation/lambda_logs.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            structured_logs.append(parse_lambda_logs(row))

    # Parse S3 logs
    with open('data/_creation/s3_logs.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            structured_logs.append(parse_s3_logs(row))

    # Parse VPC logs
    with open('data/_creation/vpc_flow_logs.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            structured_logs.append(parse_vpc_logs(row))
    
    return structured_logs

# Convert logs to JSON and save
parsed_logs = parse_logs()
with open('structured_logs.json', 'w') as json_file:
    json.dump(parsed_logs, json_file, indent=4)

print("Log parsing complete. Data saved to 'structured_logs.json'")
