import csv
from datetime import datetime, timezone

def parse_ec2_logs(log_entry):
    timestamp, hostname, process, pid, user, log_message = log_entry
    
    action = "Unknown"
    resource_type = "EC2"
    if "High CPU" in log_message:
        action = "CPU Warning"
    elif "terminated" in log_message:
        action = "TerminateInstance"
    elif "patch" in log_message:
        action = "SecurityPatch"
    
    return [
        timestamp, "EC2 Log", "IAMUser", user, hostname, "us-east-1", None, resource_type, action
    ]

def parse_lambda_logs(log_entry):
    timestamp, request_id, log_type, message = log_entry
    
    action = log_type
    resource_type = "Lambda"
    
    if log_type == "ERROR":
        response_code = "403"
    elif log_type == "START":
        response_code = "200"
    else:
        response_code = None
    
    return [
        timestamp, "Lambda Log", "IAMUser", message.split(' ')[-1], None, "us-east-1", response_code, resource_type, action
    ]

def parse_s3_logs(log_entry):
    request_id, ip_address, timestamp, bucket_name, file_name, http_method, status_code, bytes_sent, request_time, user_agent, user = log_entry
    
    action = f"S3 {http_method}"
    resource_type = "S3"
    
    return [
        timestamp, "S3 Log", "IAMUser", user, ip_address, "us-east-1", status_code, resource_type, action
    ]

def parse_vpc_logs(log_entry):
    Version, AccountId, InterfaceId, SrcAddr, DstAddr, SrcPort, DstPort, Protocol, Packets, Bytes, StartTime, EndTime, Action, LogStatus, User = log_entry
    
    action = "VPC Flow"
    resource_type = "VPC"
    
    return [
        datetime.fromtimestamp(int(StartTime), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'), "VPC Flow Log", "IAMUser", User, SrcAddr, "us-east-1", LogStatus, resource_type, action
    ]

def parse_logs_to_csv():
    structured_logs = []
    header = ["timestamp", "event_type", "user_role", "user", "source_IP", "region", "response_code", "resource_type", "action"]

    # Parse EC2 logs
    with open('/Users/davidstroud/cloud_logs/data/ec2_logs.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            structured_logs.append(parse_ec2_logs(row))

    # Parse Lambda logs
    with open('/Users/davidstroud/cloud_logs/data/lambda_logs.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            structured_logs.append(parse_lambda_logs(row))

    # Parse S3 logs
    with open('/Users/davidstroud/cloud_logs/data/s3_logs.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            structured_logs.append(parse_s3_logs(row))

    # Parse VPC logs
    with open('/Users/davidstroud/cloud_logs/data/vpc_flow_logs.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            structured_logs.append(parse_vpc_logs(row))
    
    # Write to CSV file
    with open('/Users/davidstroud/cloud_logs/anomaly_detection/structured_logs.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(structured_logs)

    print("Log parsing complete. Data saved to '/Users/davidstroud/cloud_logs/anomaly_detection/structured_logs.csv'")

# Run the log parsing and save to CSV
parse_logs_to_csv()
