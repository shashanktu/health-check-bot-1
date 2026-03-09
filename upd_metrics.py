import requests
import json
import time
import random
# from datetime import datetime, timedelta
from datetime import datetime, timedelta, UTC

base_time = datetime.now(UTC) - timedelta(minutes=2)
today = datetime.now(UTC).strftime("%Y-%m-%d")

# --- CONFIG ---
WORKSPACE_ID = "f3a1f701-305b-45a7-abba-39325ee0797b"
API_KEY = "ckqmnknnogni43iik2zje27ykt2s0qqhbpncx78x"

QUERY_TIME_MINUTES = 60 * 24 * 7
TIMESPAN = f"{QUERY_TIME_MINUTES}m"

AI_QUERY_ENDPOINT = f"https://api.applicationinsights.io/v1/apps/{WORKSPACE_ID}/query"

headers = {
    "Content-Type": "application/json",
    "X-Api-Key": API_KEY
}

# --- INFRASTRUCTURE METRICS QUERY ---
kql_query_infra = """
performanceCounters
| where name in ('% Processor Time', 'Available MBytes', 'Disk Bytes/sec', 'Bytes Received/sec', 'Bytes Sent/sec')
| summarize AvgValue = avg(value) by name, Instance=tostring(customDimensions.cloud_RoleInstance)
"""

body_infra = {
    "query": kql_query_infra,
    "timespan": TIMESPAN
}

print("\nExecuting Infrastructure Metrics Query...\n")

try:
    response = requests.post(
        AI_QUERY_ENDPOINT,
        headers=headers,
        data=json.dumps(body_infra)
    )

    response.raise_for_status()
    data = response.json()

    if "tables" in data:
        for table in data["tables"]:
            columns = [c["name"] for c in table["columns"]]

            name_idx = columns.index("name")
            instance_idx = columns.index("Instance")
            avg_idx = columns.index("AvgValue")

            rows = []

            for row in table["rows"]:
                raw_name = row[name_idx]
                instance = row[instance_idx]
                value = round(row[avg_idx], 2)

                if raw_name == "% Processor Time":
                    metric = "Avg CPU Usage"
                    unit = "%"
                elif raw_name == "Available MBytes":
                    metric = "Avg Available Memory"
                    unit = "MB"
                elif raw_name == "Disk Bytes/sec":
                    metric = "Avg Disk I/O (Total)"
                    unit = "Bytes/sec"
                elif raw_name == "Bytes Received/sec":
                    metric = "Avg Network Rx"
                    unit = "Bytes/sec"
                elif raw_name == "Bytes Sent/sec":
                    metric = "Avg Network Tx"
                    unit = "Bytes/sec"
                else:
                    metric = raw_name
                    unit = ""

                rows.append({
                    "Instance": instance,
                    "Metric Name": metric,
                    "Average Value": value,
                    "Unit": unit
                })

            rows = sorted(rows, key=lambda x: (x["Instance"], x["Metric Name"]))

            for r in rows:
                print(
                    f"{r['Instance']} | {r['Metric Name']} | "
                    f"{r['Average Value']} {r['Unit']}"
                )

    else:
        print("No infrastructure metrics returned.")

except Exception as e:
    print("❌ ERROR executing infrastructure query")
    print(str(e))


# --- APPLICATION LOGS (SIMULATED) ---
# base_time = datetime.utcnow() - timedelta(minutes=2)
# today = datetime.utcnow().strftime("%Y-%m-%d")

logs = [
f"{today}T{base_time.strftime('%H:%M:%S')}.214Z [INFO ] [ClaimsService] [corrId=7f3c2b9a12f4]",
"Request received for ClaimId=CLM-102348, PolicyId=POL-998721",
"",
f"{today}T{(base_time + timedelta(seconds=0.528)).strftime('%H:%M:%S')}.742Z [INFO ] [PolicyReconciliationProcessor] [corrId=7f3c2b9a12f4]",
"Starting reconciliation for PolicyId=POL-998721, Mode=SYNC, Source=PremiumSyncJob",
"",
f"{today}T{(base_time + timedelta(seconds=4.904)).strftime('%H:%M:%S')}.118Z [WARN ] [PolicyReconciliationProcessor] [corrId=7f3c2b9a12f4]",
"Upstream call to PolicyAPI /policies/998721 is taking longer than expected.",
"elapsedMs=4800, timeoutMs=5000, retryAttempt=1",
"",
f"{today}T{(base_time + timedelta(seconds=5.768)).strftime('%H:%M:%S')}.982Z [ERROR] [PolicyReconciliationProcessor] [corrId=7f3c2b9a12f4]",
"Failed to reconcile policy. Upstream PolicyAPI timeout.",
"PolicyId=POL-998721, Job=PremiumSyncJob,",
"ErrorType=TimeoutException,",
"Message=Request to PolicyAPI exceeded configured timeout of 5000 ms.",
"",
f"{today}T{(base_time + timedelta(seconds=5.771)).strftime('%H:%M:%S')}.985Z [ERROR] [ClaimsService] [corrId=7f3c2b9a12f4]",
"Claims processing failed due to PolicyReconciliationProcessor error.",
"HttpStatus=502, ErrorCode=POLICY_RECONCILIATION_FAILED,",
"RootCause=Upstream PolicyAPI timeout during PremiumSyncJob.",
"",
f"{today}T{(base_time + timedelta(seconds=5.796)).strftime('%H:%M:%S')}.010Z [INFO ] [PolicyReconciliationProcessor] [corrId=7f3c2b9a12f4]",
"Marking reconciliation attempt as FAILED. NextRetryInMinutes=15, MaxRetries=3."
]

print("\n--- APPLICATION LOGS ---\n")

for log in logs:
    print(log)
    time.sleep(random.uniform(0.1, 0.5))


# --- EXCEPTIONS QUERY ---
kql_query_exceptions = """
exceptions
| project timestamp, severityLevel, type, outerMessage,
Instance=tostring(customDimensions.cloud_RoleInstance)
| order by timestamp desc
| take 25
"""

body_ex = {
    "query": kql_query_exceptions,
    "timespan": TIMESPAN
}

print("\n--- EXCEPTIONS ---\n")

try:
    response = requests.post(
        AI_QUERY_ENDPOINT,
        headers=headers,
        data=json.dumps(body_ex)
    )

    response.raise_for_status()
    data = response.json()

    if "tables" in data and data["tables"][0]["rows"]:
        rows = data["tables"][0]["rows"]

        for row in rows:
            timestamp = row[0][:19].replace("T", " ")
            severity = row[1]
            ex_type = row[2]
            message = (row[3][:80] + "...") if row[3] else ""
            instance = row[4]

            print(
                f"{timestamp} | {severity} | {ex_type} | "
                f"{instance} | {message}"
            )
    else:
        print("No exceptions found.")

except Exception as e:
    print("❌ ERROR executing exception query")
    print(str(e))