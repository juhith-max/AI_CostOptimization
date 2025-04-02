import boto3
from datetime import datetime, timedelta

def fetch_aws_cost():
    client = boto3.client('ce')
    
    # Get dates for last 30 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Format dates for AWS API
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    print(f"Fetching cost data from {start_date_str} to {end_date_str}")
    
    response = client.get_cost_and_usage(
        TimePeriod={'Start': start_date_str, 'End': end_date_str},
        Granularity='DAILY',
        Metrics=['BlendedCost']
    )

    return response['ResultsByTime']

if __name__ == "__main__":
    cost_data = fetch_aws_cost()
    print("\nFirst 5 days of cost data:")
    for day in cost_data[:5]:
        print(f"Date: {day['TimePeriod']['Start']}, Cost: ${float(day['Total']['BlendedCost']['Amount']):.4f}")
