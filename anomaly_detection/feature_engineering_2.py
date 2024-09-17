import pandas as pd
import numpy as np
from scipy.stats import entropy

# Load the dataset
logs_df = pd.read_csv("/Users/davidstroud/cloud_logs/anomaly_detection/engineered_logs_100k.csv")

# 1. Time-Based Features

# Hour Binning: Define bins for different times of the day
def bin_hours(hour):
    if 0 <= hour < 6:
        return 'Night'
    elif 6 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 18:
        return 'Afternoon'
    else:
        return 'Evening'

logs_df['time_of_day'] = logs_df['hour'].apply(bin_hours)

# Extract day of the week
logs_df['day_of_week'] = pd.to_datetime(logs_df['timestamp']).dt.dayofweek

# Weekday vs. Weekend
logs_df['is_weekend'] = logs_df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)

# 2. Action and Resource Interaction

# Action Frequency per User
action_freq = logs_df.groupby(['user', 'action']).size().reset_index(name='action_frequency')
logs_df = logs_df.merge(action_freq, on=['user', 'action'], how='left')

# Resource Type Frequency per User
resource_freq = logs_df.groupby(['user', 'resource_type']).size().reset_index(name='resource_frequency')
logs_df = logs_df.merge(resource_freq, on=['user', 'resource_type'], how='left')

# Action-Resource Combination
logs_df['action_resource_combo'] = logs_df['action'] + '_' + logs_df['resource_type']

# 3. Anomaly Indicators

# High Response Code Indicator (4xx or 5xx)
logs_df['is_high_response_code'] = logs_df['response_code'].apply(lambda x: 1 if int(x) >= 400 else 0)

# Consecutive Failed Actions per User
logs_df['failed_action_shift'] = logs_df.groupby('user')['failed_action'].shift(1, fill_value=0)
logs_df['consecutive_failed_actions'] = logs_df.apply(lambda row: row['failed_action_shift'] + row['failed_action'] if row['failed_action_shift'] == 1 else row['failed_action'], axis=1)

# Drop the temporary column
logs_df.drop('failed_action_shift', axis=1, inplace=True)

# Aggregate Features

# Mean response code per user
logs_df['mean_response_code'] = logs_df.groupby('user')['response_code'].transform(lambda x: x.astype(int).mean())

# Mean hour per user
logs_df['mean_hour'] = logs_df.groupby('user')['hour'].transform('mean')

# Advanced Features

# 1. User Entropy: Measure unpredictability of user actions
def calculate_user_entropy(df):
    user_action_counts = df.groupby('user')['action'].value_counts()
    user_entropy = user_action_counts.groupby('user').apply(lambda x: entropy(x))
    return user_entropy

logs_df['user_entropy'] = logs_df['user'].map(calculate_user_entropy(logs_df))

# 2. System Usage

# Usage Rate: Number of actions per hour
logs_df['usage_rate'] = logs_df.groupby('user')['timestamp'].transform(lambda x: x.count() / ((pd.to_datetime(x.max()) - pd.to_datetime(x.min())).total_seconds() / 3600))

# Action Diversity: Unique actions performed by user
logs_df['action_diversity'] = logs_df.groupby('user')['action'].transform('nunique')

# 3. Error Analysis

# Response Code Distribution: Measure how user's response code distribution differs from normal
response_code_distribution = logs_df.groupby('user')['response_code'].value_counts(normalize=True).unstack(fill_value=0)
average_distribution = response_code_distribution.mean()
logs_df['response_code_divergence'] = logs_df['user'].map(lambda user: np.linalg.norm(response_code_distribution.loc[user] - average_distribution))

# Consecutive High-Response Codes: Count of consecutive high response codes
logs_df['consecutive_high_response'] = logs_df['response_code'].apply(lambda x: 1 if int(x) >= 400 else 0)
logs_df['consecutive_high_response'] = logs_df.groupby('user')['consecutive_high_response'].transform(lambda x: x.rolling(window=2).sum())

# 4. Temporal Features

# Time Since Last Action
logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])
logs_df = logs_df.sort_values(by=['user', 'timestamp'])
logs_df['time_since_last_action'] = logs_df.groupby('user')['timestamp'].diff().dt.total_seconds().fillna(0)

# Session Length: Define sessions and measure their lengths
session_threshold = 1800  # 30 minutes threshold for a session break

# Fix the incompatible index issue by resetting the index
session_df = logs_df.groupby('user')['time_since_last_action'].apply(lambda x: (x > session_threshold).cumsum())
session_df = session_df.reset_index(level=0, drop=True)
logs_df['session'] = session_df

session_lengths = logs_df.groupby(['user', 'session']).size()
logs_df['avg_session_length'] = logs_df['user'].map(session_lengths.groupby('user').mean())

# 5. Geographical and Resource Interaction

# Region-Resource Interaction: Encode the interaction between regions and resource types
logs_df['region_resource_interaction'] = logs_df['region'] + '_' + logs_df['resource_type']

# Cross-Region Access: Count distinct regions accessed by a user
logs_df['cross_region_access'] = logs_df.groupby('user')['region'].transform('nunique')

# Check the dataset with the new features
print(logs_df.head())

# Save the enhanced dataset with new features
logs_df.to_csv("/Users/davidstroud/cloud_logs/anomaly_detection/engineered_logs_with_advanced_features_combined.csv", index=False)
