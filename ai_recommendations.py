import json
from fetch_data_cost import fetch_aws_cost
from datetime import datetime
from slack_alerts import send_slack_alert

def format_date(date_str):
    """Format date string to a more readable format."""
    date = datetime.strptime(date_str, '%Y-%m-%d')
    return date.strftime('%B %d, %Y')

def analyze_cost(cost_data):
    """
    Analyze AWS cost data and provide optimization recommendations using rule-based analysis.
    
    Args:
        cost_data (list): List of daily cost data from AWS Cost Explorer
        
    Returns:
        str: Cost optimization recommendations
    """
    if not isinstance(cost_data, list):
        raise ValueError("cost_data must be a list of AWS cost data")
    
    # Calculate total cost and daily averages
    costs = [(day['TimePeriod']['Start'], float(day['Total']['BlendedCost']['Amount'])) 
             for day in cost_data]
    
    # Calculate statistics
    total_cost = sum(cost[1] for cost in costs)
    avg_daily_cost = total_cost / len(costs)
    highest_cost_day = max(costs, key=lambda x: x[1])
    lowest_cost_day = min(costs, key=lambda x: x[1])
    
    # Calculate cost trend
    first_half = sum(cost[1] for cost in costs[:len(costs)//2])
    second_half = sum(cost[1] for cost in costs[len(costs)//2:])
    cost_trend = "increasing" if second_half > first_half else "decreasing"
    
    # Calculate cost variance
    cost_variance = sum((cost[1] - avg_daily_cost) ** 2 for cost in costs) / len(costs)
    cost_volatility = "high" if cost_variance > (avg_daily_cost * 0.1) else "low"
    
    # Format dates for display
    start_date = format_date(cost_data[0]['TimePeriod']['Start'])
    end_date = format_date(cost_data[-1]['TimePeriod']['End'])
    highest_date = format_date(highest_cost_day[0])
    lowest_date = format_date(lowest_cost_day[0])
    
    # Generate recommendations
    recommendations = [
        f"Cost Analysis Summary",
        f"=====================",
        f"Period: {start_date} to {end_date}",
        f"Total Cost: ${total_cost:.4f}",
        f"Average Daily Cost: ${avg_daily_cost:.4f}",
        f"Cost Trend: {cost_trend}",
        f"Cost Volatility: {cost_volatility}",
        f"\nKey Findings:",
        f"1. Highest cost day: {highest_date} (${highest_cost_day[1]:.4f})",
        f"2. Lowest cost day: {lowest_date} (${lowest_cost_day[1]:.4f})",
        f"3. Cost variance: ${cost_variance:.4f}",
        f"\nDetailed Analysis:",
        f"1. Daily costs range from ${lowest_cost_day[1]:.4f} to ${highest_cost_day[1]:.4f}",
        f"2. Average daily spending is ${avg_daily_cost:.4f}",
        f"3. Total spending over the period: ${total_cost:.4f}",
        f"\nRecommendations:",
        f"1. Monitor resource usage on {highest_date} to identify cost spikes",
        f"2. Consider implementing auto-scaling to reduce costs during peak periods",
        f"3. Review and optimize resource allocation based on usage patterns",
        f"4. Set up AWS Budgets to track and control spending",
        f"5. Consider using AWS Cost Explorer's recommendations for specific service optimizations"
    ]
    
    return "\n".join(recommendations)

def save_recommendations(recommendations):
    """
    Save recommendations to a file with timestamp.
    
    Args:
        recommendations (str): The cost optimization recommendations
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cost_recommendations_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("AWS Cost Optimization Recommendations\n")
        f.write("=" * 40 + "\n\n")
        f.write(recommendations)
    
    return filename

if __name__ == "__main__":
    try:
        # Fetch the cost data
        cost_data = fetch_aws_cost()
        
        # Print raw data for debugging
        print("\nRaw Cost Data:")
        print("=" * 40)
        for day in cost_data[:5]:  # Show first 5 days for debugging
            date = format_date(day['TimePeriod']['Start'])
            print(f"Date: {date}, Cost: ${float(day['Total']['BlendedCost']['Amount']):.4f}")
        
        # Get recommendations
        recommendations = analyze_cost(cost_data)
        
        # Print recommendations
        print("\nCost Optimization Recommendations:")
        print("=" * 40)
        print(recommendations)
        
        # Save to file
        output_file = save_recommendations(recommendations)
        print(f"\nRecommendations have been saved to: {output_file}")
        
        # Send to Slack
        print("\nSending recommendations to Slack...")
        if send_slack_alert(recommendations):
            print("Successfully sent to Slack")
        else:
            print("Failed to send to Slack. Check your SLACK_WEBHOOK_URL environment variable.")
        
    except Exception as e:
        print(f"Error in cost analysis process: {str(e)}")
