$logs = @(
    "2025-05-30T02:03:01.114-05:00 [INFO ] [DatadogAgent] [corrId=INC0503408]
Alert triggered.
Integration=Datadog-DynamicInventory,
Host=ushoupwimrut159,
Environment=PROD,
Metric=system.mem.used,
Threshold=90%,
ObservedValue=92%,
AlertTitle=PROD - ImageRight High Memory Usage",
    "",
    "2025-05-30T02:03:05.882-05:00 [INFO ] [InfinityIncidentReportingJob] [corrId=INC0503408]
Job execution started.
JobName=InfinityIncidentReportingJob,
Application=Infinity,
Severity=P3,
IncidentNumber=INC0503408,
SupportGroup=SNOW-Policy-Systems-Support,
TriggerSource=Datadog",
    "",
    "2025-05-30T02:03:09.441-05:00 [INFO ] [BoxStorageMonitor] [corrId=INC0503408]
Scanning Box folder.
Path=/mnt/box/infinity/imageright/,
TotalSize=94.1GB,
FilesCount=19682,
DiskUsedPct=91.0,
Host=ushoupwimrut159",
    "",
    "2025-05-30T02:04:18.227-05:00 [INFO ] [InfinityClaimsApp] [corrId=INC0503408]
Incident processing initiated.
IncidentId=INC0503408,
Source=InfinityApps,
Priority=MODERATE",
    "",
    "2025-05-30T02:05:12.774-05:00 [WARN ] [MemoryUsageTracker] [corrId=INC0503408]
High memory usage detected.
Host=ushoupwimrut159,
MemoryUsedPct=91.6,
TimeWindow=02:00-02:10 CT,
PrimaryConsumer=BoxFolderCache",
    "",
    "2025-05-30T02:06:47.219-05:00 [WARN ] [ImageRightProcessor] [corrId=INC0503408]
ImageRight module under memory pressure.
HeapUsed=7.3GB,
HeapMax=8.0GB,
NonHeapUsed=1.4GB,
ActiveImageStreams=71,
Source=/mnt/box/infinity/imageright/",
"",
"2025-05-30T02:07:54.608-05:00 [ERROR] [BoxAttachmentLoader] [corrId=INC0503408]
Memory allocation failure.
Module=ImageRight,
Operation=ImageAggregation,
RequestedBuffer=256MB,
AvailableHeap=214MB,
Path=/mnt/box/infinity/imageright/",
"",
"2025-05-30T02:08:11.993-05:00 [ERROR] [InfinityIncidentReportingJob] [corrId=INC0503408]
Incident reporting job impacted.
JobName=InfinityIncidentReportingJob,
IncidentNumber=INC0503408,
Severity=P3,
RootCause=High memory usage due to Box folder (ImageRight),
PeakMemoryUsage=92%,
Host=ushoupwimrut159",
"",

"2025-05-30T02:09:03.481-05:00 [ERROR] [InfinityClaimsApp] [corrId=INC0503408]
Downstream job failure propagated.
HttpStatus=503,
ErrorCode=INCIDENT_REPORTING_FAILED,
Message=Incident reporting delayed due to host memory saturation.",
"",
"2025-05-30T02:10:02.317-05:00 [INFO ] [HealthMonitor] [corrId=INC0503408]
System health snapshot.
CPU=11.57%,
Memory=92%,
Disk(/mnt/box)=91%,
Status=DEGRADED",
"",
"2025-05-30T02:10:45.990-05:00 [INFO ] [InfinityIncidentReportingJob] [corrId=INC0503408]
Marking job execution as FAILED.
RetryPolicy=EXPONENTIAL_BACKOFF,
NextRetryInMinutes=20,
MaxRetries=3",
"",
"2025-05-30T06:33:37.441-05:00 [INFO ] [SNOWIncidentUpdater] [corrId=INC0503408]
Incident resolved.
IncidentNumber=INC0503408,
Resolution=Box folder cleanup and ImageRight stream throttling,
ResolvedBy=PLATFORM OPS,
ResolvedAt=2025-05-30 06:33:37",
"",
"2025-05-30T06:33:38.019-05:00 [INFO ] [CrashAnalyzer] [corrId=INC0503408]
Post-incident validation complete.
No JVM crashes or OOMKill events detected during incident window (02:00-06:33 CT)."


)

foreach ($log in $logs) {
    if ($log -eq "") {
        Write-Host ""
    } else {
        Write-Host $log -ForegroundColor White
    }
    Start-Sleep -Seconds (Get-Random -Minimum .1 -Maximum .5)
}






 

 

 

 

 

 

 

 

 

 

 

 
