# --- Ensure Az Modules are Imported ---

Import-Module Az.Accounts -ErrorAction Stop
 
# --- Configuration & Authentication Details ---

# Service Principal Details (Commented out as API Key is ACTIVE)

# $SubscriptionID = "46269e09-e1e1-4067-af90-78fd27b1b64d"

# $TenantId = "5f3ec70f-0215-4f44-bdab-f5beda7cdd74"

# $ClientId = "6b3df361-4ae6-48fa-9453-f86863af023c"

# $ClientSecret = "PbA8Q~h~p-xLb5sNIkJZWpkL3j57iM3B-TAemagV" 

$WorkspaceId = "f3a1f701-305b-45a7-abba-39325ee0797b"
 
# >>> API KEY AUTHENTICATION (ACTIVE) <<<

# API Key is used to bypass Azure AD authentication.

$ApiKey = "ckqmnknnogni43iik2zje27ykt2s0qqhbpncx78x" 

# >>> END API KEY AUTHENTICATION <<<
 
# --- 1. KQL Query Request Body (Operation Summary: Total, Avg Response, Success, Failed) ---

$QueryTimeMinutes = 60 * 24 * 7 # 7 days

$TimeSpan = "$($QueryTimeMinutes)m" 

# KQL Query: Summarize all core metrics by operation name, ordered by total volume.

$KqlQuery = "requests | summarize TotalRequests = count(), AvgResponseMs = avg(duration), SuccessfulRequests = sum(iif(success == true, 1, 0)), FailedRequests = sum(iif(success == false, 1, 0)) by operation_Name | order by TotalRequests desc"
 
$MetricsRequestBody = @{

    query = $KqlQuery

    timespan = $TimeSpan

} | ConvertTo-Json
 
# --- 2. Authentication and Token Retrieval ---

Write-Host "═════════════════ AZURE AUTHENTICATION ═════════════════" -ForegroundColor Cyan
 
# Prepare headers for the API call

$headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"

$headers.Add("Content-Type", "application/json")
 
if (-not [string]::IsNullOrWhiteSpace($ApiKey)) {

    # --- METHOD 1: Use API Key (Bypasses Azure AD) ---

    Write-Host "Using Application Insights API Key for Authorization." -ForegroundColor Yellow

    $headers.Add("X-Api-Key", $ApiKey)

} else {

    # --- METHOD 2: Fallback to Service Principal (Kept for completeness) ---

    Write-Host "Using Service Principal (Azure AD) for Authorization. API Key is preferred." -ForegroundColor Yellow

    try {

        # Note: This block is generally skipped but kept for completeness in case the API Key fails.

        $SubscriptionID = "46269e09-e1e1-4067-af90-78fd27b1b64d"

        $TenantId = "5f3ec70f-0215-4f44-bdab-f5beda7cdd74"

        $ClientId = "6b3df361-4ae6-48fa-9453-f86863af023c"

        $ClientSecret = "PbA8Q~h~p-xLb5sNIkJZWpkL3j57iM3B-TAemagV" 

        Disconnect-AzAccount -Scope Process -ErrorAction SilentlyContinue

        $SecureClientSecret = ConvertTo-SecureString $ClientSecret -AsPlainText

        $Credential = New-Object System.Management.Automation.PSCredential($ClientId, $SecureClientSecret)

        Connect-AzAccount -ServicePrincipal -Tenant $TenantId -Credential $Credential -ErrorAction Stop | Out-Null

        Select-AzSubscription -SubscriptionId $SubscriptionID | Out-Null
 
        $AiResourceUrl = "https://api.applicationinsights.io"

        $token = (Get-AzAccessToken -ResourceUrl $AiResourceUrl -ErrorAction Stop).Token

        $headers.Add("Authorization", "Bearer $token")

        Write-Host "✅ Authentication successful and new token retrieved." -ForegroundColor Green
 
    } catch {

        Write-Error "Authentication or Token retrieval failed via Service Principal."

        Write-Output "Error: $($_.Exception.Message)"

        exit 1

    }

}
 
 
# --- 3. API Call Setup ---

# API endpoint construction using the Application Insights App ID for the KQL query endpoint

$AiQueryEndpoint = "https://api.applicationinsights.io/v1/apps/$WorkspaceId/query"
 
 
# --- 4. Execute Query and Display Results (Operation Summary) ---

Write-Host "`n═════════════════ OPERATION SUMMARY (Requests, Performance, Success) ═════════════════" -ForegroundColor White -BackgroundColor DarkBlue

try {

    Write-Host "Executing KQL Query: '$KqlQuery' for the last $TimeSpan..." -ForegroundColor Cyan

    $response = Invoke-RestMethod -Method 'POST' -Uri $AiQueryEndpoint -Headers $headers -Body $MetricsRequestBody -ErrorAction Stop
 
    Write-Host "✅ Query executed successfully. Displaying results:" -ForegroundColor Green
 
    # Process and Display KQL Results

    if ($response.tables) {

        foreach ($table in $response.tables) {

            Write-Host "`nTable Name: $($table.name)" -ForegroundColor Yellow

            if ($table.rows) {

                $rows = @()

                foreach ($row in $table.rows) {

                    $rowData = [ordered]@{}

                    for ($i = 0; $i -lt $table.columns.Count; $i++) {

                        $columnName = $table.columns[$i].name

                        $columnValue = $row[$i]
 
                        # Apply user-friendly formatting and rounding

                        if ($columnName -eq 'AvgResponseMs') {

                             $rowData['Avg Response (ms)'] = [math]::Round($columnValue, 2)

                        } elseif ($columnName -eq 'operation_Name') {

                             $rowData['Operation Name'] = $columnValue

                        } elseif ($columnName -eq 'TotalRequests') {

                             $rowData['Total Requests'] = [int]$columnValue

                        } elseif ($columnName -eq 'SuccessfulRequests') {

                             $rowData['Successful Requests'] = [int]$columnValue

                        } elseif ($columnName -eq 'FailedRequests') {

                             $rowData['Failed Requests'] = [int]$columnValue

                        } else {

                             $rowData[$columnName] = $columnValue

                        }

                    }

                    $rows += New-Object PSObject -Property $rowData

                }

                # Sort by volume of requests (Total Requests)

                $rows | Sort-Object -Property 'Total Requests' -Descending | Format-Table -AutoSize

            } else {

                Write-Host "No data found for the Operation Summary in the last $TimeSpan." -ForegroundColor Yellow

            }

        }

    } else {

        Write-Host "Operation Summary query returned no tables or an unexpected format." -ForegroundColor Red

    }

} catch {

    Write-Output "❌ ERROR: Failed to execute Operation Summary query."

    Write-Output "Error details: $($_.Exception.Message)"

    exit 1

}
 
 
# --- 5. Execute Query and Display Results (Daily Active Users) ---

Write-Host "`n═════════════════ USER TREND (Daily Active Users) ═════════════════" -ForegroundColor White -BackgroundColor DarkBlue
 
# KQL Query: Summarize the daily count of unique users over the last 7 days.

$KqlQueryUsers = "union requests, pageViews | summarize DailyUsers = dcount(user_Id) by bin(timestamp, 1d) | order by timestamp asc"
 
$MetricsRequestBodyUsers = @{

    query = $KqlQueryUsers

    timespan = $TimeSpan

} | ConvertTo-Json
 
try {

    Write-Host "Executing KQL Query: '$KqlQueryUsers' for the last $TimeSpan..." -ForegroundColor Cyan

    $response = Invoke-RestMethod -Method 'POST' -Uri $AiQueryEndpoint -Headers $headers -Body $MetricsRequestBodyUsers -ErrorAction Stop
 
    Write-Host "✅ Query executed successfully. Displaying results:" -ForegroundColor Green
 
    # Process and Display KQL Results

    if ($response.tables) {

        foreach ($table in $response.tables) {

            Write-Host "`nTable Name: $($table.name)" -ForegroundColor Yellow

            if ($table.rows) {

                $rows = @()

                foreach ($row in $table.rows) {

                    $rowData = [ordered]@{}

                    for ($i = 0; $i -lt $table.columns.Count; $i++) {

                        $columnName = $table.columns[$i].name

                        $columnValue = $row[$i]
 
                        # Apply user-friendly formatting and rounding

                        if ($columnName -eq 'timestamp') {

                             # Convert UTC timestamp string to a local DateTime object for readability

                             $rowData['Date'] = [datetime]$columnValue | Get-Date -Format "yyyy-MM-dd"

                        } elseif ($columnName -eq 'DailyUsers') {

                             $rowData['Daily Unique Users'] = [int]$columnValue

                        } else {

                             $rowData[$columnName] = $columnValue

                        }

                    }

                    $rows += New-Object PSObject -Property $rowData

                }

                $rows | Format-Table -AutoSize

            } else {

                Write-Host "No data found for Daily Active Users in the last $TimeSpan." -ForegroundColor Yellow

            }

        }

    } else {

        Write-Host "User Trend query returned no tables or an unexpected format." -ForegroundColor Red

    }

} catch {

    Write-Output "❌ ERROR: Failed to execute User Trend query."

    Write-Output "Error details: $($_.Exception.Message)"

    exit 1

}
 
Write-Host "`n═════════════════ SCRIPT COMPLETE ═════════════════" -ForegroundColor Green
 