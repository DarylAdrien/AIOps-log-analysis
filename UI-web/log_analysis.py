import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import io

def analyze_logs(log_file_content):
    """
    Analyzes log file content for anomalies using Isolation Forest.

    Args:
        log_file_content (str): The content of the log file as a string.

    Returns:
        tuple: A tuple containing:
            - list: A list of dictionaries, where each dictionary represents an anomaly.
            - str: A string representation of the full DataFrame with anomaly flags.
    """
    # Read log file content from string
    log_stream = io.StringIO(log_file_content)
    logs = log_stream.readlines()

    # Parse logs into a structured DataFrame
    data = []
    for log in logs:
        parts = log.strip().split(" ", 3)  # Ensure the message part is captured fully
        if len(parts) < 4:
            continue  # Skip malformed lines
        timestamp = parts[0] + " " + parts[1]
        level = parts[2]
        message = parts[3]
        data.append([timestamp, level, message])

    df = pd.DataFrame(data, columns=["timestamp", "level", "message"])

    # Convert timestamp to datetime format for sorting
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Assign numeric scores to log levels
    level_mapping = {"INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
    df["level_score"] = df["level"].map(level_mapping)

    # Add message length as a new feature
    df["message_length"] = df["message"].apply(len)

    # AI Model for Anomaly Detection (Isolation Forest)
    model = IsolationForest(contamination=0.1, random_state=42) # Changed from 0 to 0.0001
    df["anomaly"] = model.fit_predict(df[["level_score", "message_length"]])

    # Mark anomalies in a readable format
    df["is_anomaly"] = df["anomaly"].apply(lambda x: "❌ Anomaly" if x == -1 else "")

    anomalies = []
    for index, row in df[df["is_anomaly"] == "❌ Anomaly"].iterrows():
        anomalies.append({
            "timestamp": str(row["timestamp"]), # Convert to string for JSON serialization
            "level": row["level"],
            "message": row["message"]
        })

    full_analysis_str = df.to_string() # Convert DataFrame to string for display

    return anomalies, full_analysis_str

# Example of how to use it if you want to test locally (this part won't be in the final web app)
if __name__ == "__main__":
    # For testing, you can read from a dummy file or provide a string
    try:
        with open("system_logs.txt", "r") as f:
            test_log_content = f.read()
        anomalies, full_log_output = analyze_logs(test_log_content)
        print("\n--- Detected Anomalies ---")
        if anomalies:
            for anomaly in anomalies:
                print(f"Timestamp: {anomaly['timestamp']}, Level: {anomaly['level']}, Message: {anomaly['message']}")
        else:
            print("No anomalies detected.")

        print("\n--- Full Log Analysis ---")
        print(full_log_output)

    except FileNotFoundError:
        print("system_logs.txt not found. Please create it for local testing.")
    except Exception as e:
        print(f"An error occurred during local testing: {e}")