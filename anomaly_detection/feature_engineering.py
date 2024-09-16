import pandas as pd
import random
from datetime import datetime, timedelta

# Create a DataFrame with 100,000 rows
num_rows = 100000

# Create a date range for timestamps
start_date = datetime.now() - timedelta(days=365)
date_range = [start_date + timedelta(seconds=random.randint(0, 31536000)) for _ in range(num_rows)]

# Step 1: Create a list of 10 unique users
user_list = ['user1', 'user2', 'user3', 'user4', 'user5', 'user6', 'user7', 'user8', 'user9', 'user10']

# Step 2: Randomly assign users to each log entry
users = random.choices(user_list, k=num_rows)

# Step 3: Create an uneven distribution of resource types
resource_types = ['EC2', 'Lambda', 'S3', 'VPC']
resource_type_distribution = {'EC2': 0.5, 'Lambda': 0.2, 'S3': 0.2, 'VPC': 0.1}
resource_type_counts = {rtype: int(num_rows * proportion) for rtype, proportion in resource_type_distribution.items()}

random_resource_types = []
for resource_type, count in resource_type_counts.items():
    random_resource_types.extend([resource_type] * count)

remaining_count = num_rows - len(random_resource_types)
if remaining_count > 0:
    random_resource_types.extend([max(resource_type_distribution, key=resource_type_distribution.get)] * remaining_count)

random.shuffle(random_resource_types)

# Ensure that the length of random_resource_types matches num_rows
random_resource_types = random_resource_types[:num_rows]

# Step 4: Create event types based on resource types
def assign_event_type(resource_type):
    if resource_type == 'EC2':
        return 'EC2 Log'
    elif resource_type == 'VPC':
        return 'VPC Flow Log'
    elif resource_type == 'S3':
        return 'S3 Log'
    elif resource_type == 'Lambda':
        return 'Lambda Log'

event_types = [assign_event_type(rt) for rt in random_resource_types]

# Step 5: Define possible actions for each resource type
action_options = {
    'EC2': ['StartInstance', 'StopInstance', 'RebootInstance', 'TerminateInstance', 'AttachVolume'],
    'Lambda': ['InvokeFunction', 'FunctionError', 'FunctionTimeout', 'FunctionSuccess', 'CreateFunction'],
    'S3': ['PutObject', 'GetObject', 'DeleteObject', 'ListBucket', 'CopyObject'],
    'VPC': ['CreateVPC', 'DeleteVPC', 'ModifyVPC', 'CreateSubnet', 'RouteTableChange']
}

# Assign random actions based on resource type
actions = [random.choice(action_options[rt]) for rt in random_resource_types]

# Randomly generate regions with a bias towards 'us-east-1'
num_us_east_1 = int(num_rows * 0.9)
num_other_regions = num_rows - num_us_east_1

regions = ['us-east-1'] * num_us_east_1
regions += random.choices(['us-west-2', 'eu-central-1', 'ap-southeast-2'], k=num_other_regions)

# Ensure regions list matches num_rows
random.shuffle(regions)
regions = regions[:num_rows]

# Randomly generate response codes
response_codes = []
for rt in random_resource_types:
    if rt == 'Lambda':
        response_codes.append(random.choice(["200", "403", "404", "500"]))
    elif rt == 'S3':
        response_codes.append(random.choice(["200", "201", "204", "403", "404"]))
    elif rt == 'VPC':
        response_codes.append(random.choice(["100", "200", "400", "403"]))
    elif rt == 'EC2':
        response_codes.append(random.choice(["200", "400", "403", "500"]))

# Step 6: Create the DataFrame
logs_df = pd.DataFrame({
    'timestamp': date_range,
    'user': users,
    'resource_type': random_resource_types,
    'event_type': event_types,
    'action': actions,
    'region': regions,
    'response_code': response_codes
})

# 1. Time-based Features
logs_df['hour'] = logs_df['timestamp'].dt.hour

def is_unusual_hour(hour):
    return int(hour < 9 or hour > 17)

logs_df['unusual_hour'] = logs_df['hour'].apply(is_unusual_hour)

# 2. Geographical Anomalies
normal_regions = ['us-east-1']
logs_df['geo_anomaly'] = logs_df['region'].apply(lambda x: 1 if x not in normal_regions else 0)

# Calculate the number of anomalies needed (15% of the total rows)
num_anomalies = int(num_rows * 0.15)
non_anomaly_indices = logs_df[logs_df['geo_anomaly'] == 0].index.tolist()
random_anomaly_indices = random.sample(non_anomaly_indices, num_anomalies)
logs_df.loc[random_anomaly_indices, 'geo_anomaly'] = 1

# 3. Failed Actions
# Set 24% of the failed_action column to 1
num_failures = int(num_rows * 0.24)

# Initialize the failed_action column to 0
logs_df['failed_action'] = 0

# Randomly select indices to set as failed actions
failure_indices = random.sample(logs_df.index.tolist(), num_failures)

# Set the selected indices to 1
logs_df.loc[failure_indices, 'failed_action'] = 1

# Aggregate the count of failed actions per user
failed_actions_count = logs_df.groupby('user')['failed_action'].sum().reset_index()
failed_actions_count.columns = ['user', 'failed_actions_count']

# Merge the count back into the main DataFrame
logs_df = logs_df.merge(failed_actions_count, on='user', how='left')

# 4. Session-based Features
logs_df.set_index('timestamp', inplace=True)

def aggregate_session_features(df, window='1h'):
    session_features = df.groupby('user').resample(window).size().reset_index(name='action_count')
    df = df.merge(session_features, on=['user', 'timestamp'], how='left')
    return df

logs_df = aggregate_session_features(logs_df)
logs_df.reset_index(inplace=True)

# Update action_count based on the total number of actions per user
logs_df['action_count'] = logs_df.groupby('user')['action'].transform('count')

# Save the modified DataFrame to a new CSV file
logs_df.to_csv("/Users/davidstroud/cloud_logs/anomaly_detection/engineered_logs_100k.csv", index=False)

# Display the DataFrame with the new features
print(logs_df.head())
