import csv
import random
import datetime

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
    now = datetime.datetime.now()
    random_seconds = random.randint(0, 14 * 24 * 60 * 60)  # Number of seconds in two weeks
    random_time = now - datetime.timedelta(seconds=random_seconds)
    return random_time.strftime('%Y-%m-%d %H:%M:%S')

# Function to generate synthetic EC2 logs
def generate_ec2_logs(num_records=10000):
    ec2_logs = []
    hostname_base = 'ip-172-31-0-'
    
    processes = ['CRON', 'systemd', 'sshd', 'kernel', 'auditd', 'dhclient', 'docker', 'cloud-init']
    
    for _ in range(num_records):
        timestamp = random_time_within_last_two_weeks()
        process = random.choice(processes)
        pid = random.randint(1000, 99999)
        hostname = hostname_base + str(random.randint(1, 255))

        # Use the same user for EC2 activity
        user = get_random_user()

        log_message = random.choice([
            f"(root) CMD (/usr/sbin/logrotate /etc/logrotate.conf) by {user['userName']}",
            "Accepted publickey for ec2-user from 203.0.113.{} port {} ssh2: RSA SHA256:abc123".format(random.randint(1, 255), random.randint(10000, 65535)),
            "Failed password attempt for user ec2-user from 203.0.113.{}.".format(random.randint(1, 255)),
            "Disk space warning on /dev/sda1: {}% full.".format(random.randint(80, 99)),
            "Warning: High CPU usage detected on instance i-{}.".format(random.randint(1000000000, 9999999999)),
            "SSH connection closed for ec2-user from 203.0.113.{}.".format(random.randint(1, 255)),
            "System reboot initiated by ec2-user.",
            f"Unusual login attempt detected from IP 198.51.100.{random.randint(1, 255)} by {user['userName']}.",
            "Unauthorized attempt to access restricted file /etc/passwd.",
            "Security patch applied. Reboot required to complete installation.",
            "Instance i-{} terminated by user ec2-user.".format(random.randint(1000000000, 9999999999))
        ])

        ec2_logs.append({
            'timestamp': timestamp,
            'hostname': hostname,
            'process': process,
            'pid': pid,
            'user': user['userName'],
            'log_message': log_message
        })
    
    return ec2_logs

# Function to write the generated logs to a CSV file
def write_ec2_logs_to_csv(filename, logs):
    fieldnames = ['timestamp', 'hostname', 'process', 'pid', 'user', 'log_message']
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(logs)

# Generate 10,000 synthetic EC2 Instance Logs and write to a CSV file
ec2_logs = generate_ec2_logs(10000)
write_ec2_logs_to_csv('/Users/davidstroud/cloud_logs/data/ec2_logs.csv', ec2_logs)