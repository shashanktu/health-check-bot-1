import requests
import json
from datetime import datetime
import pandas as pd

class AzureInsightsClient:
    def __init__(self, workspace_id: str, api_key: str):
        self.workspace_id = workspace_id
        self.api_key = api_key
        self.endpoint = f"https://api.applicationinsights.io/v1/apps/{workspace_id}/query"
        self.headers = {
            "Content-Type": "application/json",
            "X-Api-Key": api_key
        }
    
    def execute_query(self, kql_query: str, timespan: str = "10080m") -> dict:
        """Execute KQL query against Application Insights"""
        body = {
            "query": kql_query,
            "timespan": timespan
        }
        
        response = requests.post(
            self.endpoint,
            headers=self.headers,
            json=body
        )
        response.raise_for_status()
        return response.json()
    
    def get_operation_summary(self, days: int = 7) -> list:
        """Get operation summary with requests, performance, and success metrics"""
        timespan = f"{days * 24 * 60}m"
        kql_query = """
        requests 
        | summarize 
            TotalRequests = count(), 
            AvgResponseMs = avg(duration), 
            SuccessfulRequests = sum(iif(success == true, 1, 0)), 
            FailedRequests = sum(iif(success == false, 1, 0)) 
        by operation_Name 
        | order by TotalRequests desc
        """
        
        print(f"\n{'='*20} OPERATION SUMMARY {'='*20}")
        print(f"Executing query for the last {days} days...")
        
        try:
            response = self.execute_query(kql_query, timespan)
            
            if not response.get('tables'):
                print("No data found")
                return []
            
            results = []
            for table in response['tables']:
                if not table.get('rows'):
                    continue
                    
                columns = [col['name'] for col in table['columns']]
                
                for row in table['rows']:
                    row_data = {}
                    for i, value in enumerate(row):
                        col_name = columns[i]
                        
                        if col_name == 'AvgResponseMs':
                            row_data['Avg Response (ms)'] = round(value, 2) if value else 0
                        elif col_name == 'operation_Name':
                            row_data['Operation Name'] = value
                        elif col_name == 'TotalRequests':
                            row_data['Total Requests'] = int(value)
                        elif col_name == 'SuccessfulRequests':
                            row_data['Successful Requests'] = int(value)
                        elif col_name == 'FailedRequests':
                            row_data['Failed Requests'] = int(value)
                        else:
                            row_data[col_name] = value
                    
                    results.append(row_data)
            
            # Sort by Total Requests descending
            results.sort(key=lambda x: x.get('Total Requests', 0), reverse=True)
            
            # Display results
            if results:
                df = pd.DataFrame(results)
                print("[SUCCESS] Query executed successfully:")
                print(df.to_string(index=False))
            else:
                print("No data found for the Operation Summary")
            
            return results
            
        except Exception as e:
            print(f"[ERROR] Failed to execute Operation Summary query")
            print(f"Error details: {str(e)}")
            return []
    
    def get_daily_users(self, days: int = 7) -> list:
        """Get daily active users trend"""
        timespan = f"{days * 24 * 60}m"
        kql_query = """
        union requests, pageViews 
        | summarize DailyUsers = dcount(user_Id) by bin(timestamp, 1d) 
        | order by timestamp asc
        """
        
        print(f"\n{'='*20} USER TREND (Daily Active Users) {'='*20}")
        print(f"Executing query for the last {days} days...")
        
        try:
            response = self.execute_query(kql_query, timespan)
            
            if not response.get('tables'):
                print("No data found")
                return []
            
            results = []
            for table in response['tables']:
                if not table.get('rows'):
                    continue
                    
                columns = [col['name'] for col in table['columns']]
                
                for row in table['rows']:
                    row_data = {}
                    for i, value in enumerate(row):
                        col_name = columns[i]
                        
                        if col_name == 'timestamp':
                            # Convert timestamp to readable date
                            date_obj = datetime.fromisoformat(value.replace('Z', '+00:00'))
                            row_data['Date'] = date_obj.strftime('%Y-%m-%d')
                        elif col_name == 'DailyUsers':
                            row_data['Daily Unique Users'] = int(value)
                        else:
                            row_data[col_name] = value
                    
                    results.append(row_data)
            
            # Display results
            if results:
                df = pd.DataFrame(results)
                print("[SUCCESS] Query executed successfully:")
                print(df.to_string(index=False))
            else:
                print("No data found for Daily Active Users")
            
            return results
            
        except Exception as e:
            print(f"[ERROR] Failed to execute User Trend query")
            print(f"Error details: {str(e)}")
            return []

def get_insights():
    # Configuration
    workspace_id = "f3a1f701-305b-45a7-abba-39325ee0797b"
    api_key = "ckqmnknnogni43iik2zje27ykt2s0qqhbpncx78x"
    
    print("================= AZURE AUTHENTICATION =================")
    print("Using Application Insights API Key for Authorization.")
    
    # Initialize client
    client = AzureInsightsClient(workspace_id, api_key)
    
    # Execute queries
    operation_summary = client.get_operation_summary(days=7)
    daily_users = client.get_daily_users(days=7)
    
    print("\n================= SCRIPT COMPLETE =================")
    
    return {
        "operation_summary": operation_summary,
        "daily_users": daily_users
    }

if __name__ == "__main__":
    get_insights()