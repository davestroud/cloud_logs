import pandas as pd

# Load the structured logs data
logs_df = pd.read_csv('/Users/davidstroud/cloud_logs/data/structured_logs.csv', low_memory=False)
    
# Convert timestamp to datetime using more flexible parsing
logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce')

# Drop rows with NaT in the timestamp column
logs_df = logs_df.dropna(subset=['timestamp'])

# 1. Time-based Features
# Extract the hour from the timestamp
logs_df['hour'] = logs_df['timestamp'].dt.hour

# Define a function to mark unusual hours (outside 9 AM - 5 PM)
def is_unusual_hour(hour):
    return int(hour < 9 or hour > 17)

# Apply the function to create the unusual_hour feature
logs_df['unusual_hour'] = logs_df['hour'].apply(is_unusual_hour)

# 2. Geographical Anomalies
# Define the normal operating regions (e.g., only us-east-1 is considered normal)
normal_regions = ['us-east-1']

# Create a feature for geographical anomalies
logs_df['geo_anomaly'] = logs_df['region'].apply(lambda x: 1 if x not in normal_regions else 0)

# 3. Failed Actions
# Create a feature for failed actions based on response_code
# Since the dataset doesn't include explicit failure codes, we'll demonstrate the approach
# Marking actions as failed if response_code is not NaN and equals 403 (common failure code)
logs_df['failed_action'] = logs_df['response_code'].apply(lambda x: 1 if x == 403 else 0)

# Aggregate the count of failed actions per user (example aggregation)
failed_actions_count = logs_df.groupby('user')['failed_action'].sum().reset_index()
failed_actions_count.columns = ['user', 'failed_actions_count']

# Merge the count back into the main DataFrame
logs_df = logs_df.merge(failed_actions_count, on='user', how='left')

# 4. Session-based Features
# Set the timestamp as the index for resampling
logs_df.set_index('timestamp', inplace=True)

# Define a function to aggregate actions per user within a given time window (e.g., 1 hour)
def aggregate_session_features(df, window='1H'):
    # Resample to count actions in each window
    session_features = df.groupby('user').resample(window).size().reset_index(name='action_count')
    
    # Merge the session-based feature back into the main DataFrame
    df = df.merge(session_features, on=['user', 'timestamp'], how='left')
    return df

# Apply the aggregation function to get the action count within a 1-hour window
logs_df = aggregate_session_features(logs_df)

# Reset the index after aggregation
logs_df.reset_index(inplace=True)

logs_df.to_csv("/Users/davidstroud/cloud_logs/anomaly_detection/engineered_logs.csv", index=False)

# Display the DataFrame with the new features
print(logs_df.head())



