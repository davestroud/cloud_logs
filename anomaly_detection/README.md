# Feature Engineering for Anomaly Detection in AWS Logs

This project performs feature engineering on a dataset of structured AWS logs to prepare it for anomaly detection or other analysis. The logs include data from various AWS services like EC2, CloudTrail, etc. The features engineered in this project aim to enhance the detection of unusual patterns, security breaches, or system issues.

## Data

The dataset used in this project is a collection of AWS logs with the following columns:
- `event_type`: The type of event logged.
- `timestamp`: The date and time when the event occurred.
- `user_role`: The role of the user who triggered the event.
- `user`: The identifier of the user.
- `source_IP`: The IP address from which the event was triggered.
- `region`: The AWS region where the event occurred.
- `response_code`: The HTTP response code resulting from the event.
- `resource_type`: The type of AWS resource involved.
- `action`: The action performed by the user on the resource.

### Sample Data

| index | event_type | timestamp           | user_role | user      | source_IP        | region   | response_code | resource_type | action            | hour | unusual_hour | geo_anomaly | failed_action | failed_actions_count | action_count |
|-------|------------|---------------------|-----------|-----------|------------------|----------|---------------|----------------|--------------------|------|--------------|-------------|---------------|----------------------|--------------|
| 0     | EC2 Log    | 2024-09-02 04:32:24 | IAMUser   | dev-user  | ip-172-31-0-142  | us-east-1| NaN           | EC2            | CPU Warning        | 4    | 1            | 0           | 0             | 0                    | NaN          |
| 1     | EC2 Log    | 2024-09-09 07:40:08 | IAMUser   | test-user | ip-172-31-0-194  | us-east-1| NaN           | EC2            | SecurityPatch      | 7    | 1            | 0           | 0             | 0                    | NaN          |
| 2     | EC2 Log    | 2024-09-07 14:49:30 | IAMUser   | test-user | ip-172-31-0-141  | us-east-1| NaN           | EC2            | TerminateInstance  | 14   | 0            | 0           | 0             | 0                    | NaN          |
| 3     | EC2 Log    | 2024-09-05 10:34:27 | IAMUser   | dev-user  | ip-172-31-0-18   | us-east-1| NaN           | EC2            | Unknown            | 10   | 0            | 0           | 0             | 0                    | NaN          |
| 4     | EC2 Log    | 2024-09-08 21:16:15 | IAMUser   | test-user | ip-172-31-0-225  | us-east-1| NaN           | EC2            | CPU Warning        | 21   | 1            | 0           | 0             | 0                    | NaN          |

## Feature Engineering Process

### 1. Time-based Features

Extracts the hour from the timestamp to identify if the event occurred during unusual hours (outside 9 AM to 5 PM).

- **`hour`**: The hour of the event.
- **`unusual_hour`**: A binary feature where `1` indicates the event happened outside of standard working hours.

### 2. Geographical Anomalies

Identifies events that occurred in regions outside the normal operating regions.

- **`geo_anomaly`**: A binary feature where `1` indicates the event occurred in an unexpected region.

### 3. Failed Actions

Counts failed actions for each user based on response codes (e.g., `403` for forbidden actions).

- **`failed_action`**: A binary feature where `1` indicates a failed action.
- **`failed_actions_count`**: The count of failed actions aggregated per user.

### 4. Session-based Features

Aggregates the number of actions per user within a 1-hour window to detect bursts in activity.

- **`action_count`**: The count of actions performed by the user within a 1-hour window.

## Code Explanation

The code performs the following steps:
1. **Data Loading and Parsing**: Reads the CSV file and converts the timestamp to a datetime object.
2. **Feature Engineering**:
   - Extracts the hour from the timestamp.
   - Identifies events outside the usual working hours.
   - Detects geographical anomalies based on regions.
   - Identifies and counts failed actions.
   - Aggregates actions within 1-hour sessions.
3. **Output**: Displays the DataFrame with the newly engineered features.

## Usage

1. **Requirements**: Make sure to have pandas installed. If not, install it using:
   ```bash
   pip install pandas
