# Smoke Test Bot Backend

A production-ready FastAPI backend service for performing smoke tests on applications. This service provides REST APIs to test database connectivity, application endpoints, Azure KeyVault secrets, and VM metrics.

## Features

✅ **Asynchronous Operations** - All I/O operations are non-blocking  
✅ **Concurrent API Testing** - Test multiple endpoints simultaneously  
✅ **Retry Logic** - Exponential backoff for failed requests  
✅ **JSON Logging** - Structured logging for easy parsing  
✅ **Azure Integration** - KeyVault secrets and Monitor metrics support  
✅ **PostgreSQL Support** - Async connections to PostgreSQL databases  
✅ **Type Safety** - Full Pydantic type hints throughout  
✅ **Docker Ready** - Production-grade multi-stage Dockerfile included  
✅ **Comprehensive Tests** - Full test coverage with mocking  

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit Frontend                     │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────────────────────────────────────────────┐
│            FastAPI Smoke Test Bot Backend                │
├──────────────────────────────────────────────────────────┤
│ Endpoints:                                               │
│  • POST /run-all          (Run all tests)               │
│  • POST /test/db          (Database check)              │
│  • POST /test/apis        (API check)                   │
│  • POST /test/secrets     (KeyVault check)              │
│  • POST /test/metrics     (VM metrics check)            │
│  • GET  /health           (Health check)                │
└──────────────────────────────────────────────────────────┘
        │          │          │          │
        ▼          ▼          ▼          ▼
   ┌────────┐ ┌─────────┐ ┌────────┐ ┌────────┐
   │  DB    │ │ APIs    │ │Azure   │ │Azure   │
   │        │ │         │ │KeyVault│ │Monitor │
   └────────┘ └─────────┘ └────────┘ └────────┘
```

## Project Structure

```
smoke_test_bot/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── routers/
│   │   ├── db_check.py         # Database check endpoint
│   │   ├── api_check.py        # API check endpoint
│   │   ├── secret_check.py     # KeyVault check endpoint
│   │   ├── metrics_check.py    # Metrics check endpoint
│   │   └── run_all.py          # Run all tests endpoint
│   ├── services/
│   │   ├── db_service.py       # Database service logic
│   │   ├── api_service.py      # API service logic
│   │   ├── secret_service.py   # KeyVault service logic
│   │   └── metrics_service.py  # Metrics service logic
│   ├── utils/
│   │   ├── logger.py           # JSON logging utility
│   │   ├── http_client.py      # Async HTTP client with retries
│   │   └── response_builder.py # Response standardization
│   └── models/
│       ├── request_models.py   # Pydantic request models
│       └── response_models.py  # Pydantic response models
├── tests/
│   ├── conftest.py             # Pytest configuration and fixtures
│   ├── test_db.py              # Database service tests
│   ├── test_api.py             # API service tests
│   ├── test_secrets.py         # KeyVault service tests
│   └── test_metrics.py         # Metrics service tests
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── Dockerfile                  # Multi-stage Docker build
└── README.md                   # This file
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL (for database tests)
- Azure subscription (for KeyVault and Monitor tests)
- Docker (optional, for containerized deployment)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smoke-bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Setup

1. **Build Docker image**
   ```bash
   docker build -t smoke-test-bot:latest .
   ```

2. **Run Docker container**
   ```bash
   docker run -d \
     --name smoke-test-bot \
     -p 8000:8000 \
     --env-file .env \
     smoke-test-bot:latest
   ```

3. **Check container logs**
   ```bash
   docker logs -f smoke-test-bot
   ```

## Environment Variables

### Required Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database
SAMPLE_QUERY=SELECT 1

# Azure KeyVault
AZURE_KEYVAULT_NAME=your-keyvault-name
AZURE_SECRET_LIST=["secret1", "secret2"]
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id

# Azure VM Metrics
VM_RESOURCE_ID=/subscriptions/.../virtualMachines/vm-name
```

### Optional Variables

```env
# Logging
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json

# Timeouts and Retries
DB_TIMEOUT=10
DB_RETRIES=3
API_TIMEOUT=10
API_RETRIES=2
AZURE_TIMEOUT=10

# Thresholds
METRIC_THRESHOLD_CPU=80
METRIC_THRESHOLD_MEMORY=500
```

See `.env.example` for complete configuration template.

## API Endpoints

### Health Check

```bash
curl -X GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "success",
  "message": "Service is healthy",
  "data": {
    "status": "healthy",
    "service_name": "smoke-test-bot",
    "version": "1.0.0",
    "timestamp": "2024-11-14T10:30:00"
  }
}
```

### Run All Tests

```bash
curl -X POST http://localhost:8000/run-all \
  -H "Content-Type: application/json" \
  -d '{
    "include_db_check": true,
    "include_api_check": true,
    "include_secret_check": true,
    "include_metrics_check": true
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "All tests completed",
  "data": {
    "run_id": "550e8400-e29b-41d4-a716-446655440000",
    "overall_status": "OK",
    "summary": {
      "total_tests": 4,
      "passed_tests": 4,
      "warning_tests": 0,
      "failed_tests": 0
    },
    "details": {
      "database": {...},
      "apis": {...},
      "secrets": {...},
      "metrics": {...}
    },
    "timestamp": "2024-11-14T10:30:00"
  }
}
```

### Database Check

```bash
curl -X POST http://localhost:8000/test/db \
  -H "Content-Type: application/json" \
  -d '{
    "database_url": "postgresql+asyncpg://user:password@host/db",
    "query": "SELECT 1"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Database check completed",
  "data": {
    "test_name": "database_check",
    "status": "UP",
    "details": {
      "connection_status": "connected",
      "query_status": "executed",
      "query_result_summary": "1"
    },
    "timestamp": "2024-11-14T10:30:00",
    "latency_ms": 125.50
  }
}
```

### API Check

```bash
curl -X POST http://localhost:8000/test/apis \
  -H "Content-Type: application/json" \
  -d '{
    "api_list": [
      {
        "name": "example_api",
        "method": "GET",
        "url": "https://api.example.com/health",
        "expected_status": 200
      }
    ]
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "API check completed",
  "data": {
    "test_name": "api_check",
    "status": "OK",
    "details": {
      "apis_tested": 1,
      "apis_passed": 1,
      "apis_failed": 0,
      "api_results": [
        {
          "name": "example_api",
          "url": "https://api.example.com/health",
          "method": "GET",
          "status_code": 200,
          "expected_status": 200,
          "status": "OK",
          "latency_ms": 145.30
        }
      ]
    },
    "timestamp": "2024-11-14T10:30:00",
    "latency_ms": 150.50
  }
}
```

### Secret Check

```bash
curl -X POST http://localhost:8000/test/secrets \
  -H "Content-Type: application/json" \
  -d '{
    "keyvault_name": "my-keyvault",
    "secret_list": ["secret1", "secret2"]
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Secret check completed",
  "data": {
    "test_name": "secret_check",
    "status": "OK",
    "details": {
      "total_secrets": 2,
      "found_secrets": 2,
      "secret_results": [
        {
          "name": "secret1",
          "status": "FOUND"
        },
        {
          "name": "secret2",
          "status": "FOUND"
        }
      ]
    },
    "timestamp": "2024-11-14T10:30:00",
    "latency_ms": 320.75
  }
}
```

### Metrics Check

```bash
curl -X POST http://localhost:8000/test/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "resource_id": "/subscriptions/sub-id/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm-name",
    "cpu_threshold": 80,
    "memory_threshold": 500
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Metrics check completed",
  "data": {
    "test_name": "metrics_check",
    "status": "OK",
    "details": {
      "cpu_usage": {
        "value": 45.50,
        "unit": "percentage",
        "threshold": 80,
        "status": "OK"
      },
      "memory_usage": {
        "value": 2048.00,
        "unit": "MB",
        "threshold": 500,
        "status": "OK"
      }
    },
    "timestamp": "2024-11-14T10:30:00",
    "latency_ms": 425.30
  }
}
```

## Running Tests

### Run all tests

```bash
pytest tests/ -v
```

### Run tests with coverage

```bash
pytest tests/ -v --cov=app --cov-report=html
```

### Run specific test file

```bash
pytest tests/test_db.py -v
```

### Run with asyncio support

```bash
pytest tests/ -v --asyncio-mode=auto
```

## Configuration Details

### Database Configuration

The service uses `asyncpg` for non-blocking PostgreSQL connections:

- **DATABASE_URL**: Full connection string in format `postgresql+asyncpg://user:password@host:port/database`
- **SAMPLE_QUERY**: Query to test connectivity (default: `SELECT 1`)
- **DB_TIMEOUT**: Connection timeout in seconds (default: 10)
- **DB_RETRIES**: Number of retry attempts (default: 3)

### API Check Configuration

The service makes concurrent HTTP requests to multiple endpoints:

- **API_LIST**: JSON array of API configurations with `name`, `method`, `url`, `expected_status`
- **API_TIMEOUT**: Individual request timeout in seconds (default: 10)
- **API_RETRIES**: Retry attempts per request (default: 2)

### Azure Configuration

Supports two authentication methods:

1. **Client Secret**: Uses `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`
2. **Managed Identity**: Falls back to DefaultAzureCredential (no env vars needed)

### Metric Thresholds

- **METRIC_THRESHOLD_CPU**: CPU usage threshold percentage (default: 80%)
- **METRIC_THRESHOLD_MEMORY**: Available memory threshold in MB (default: 500MB)

Status levels:
- **OK**: Within normal thresholds
- **WARNING**: Threshold exceeded by <50%
- **CRITICAL**: Threshold exceeded by >50%

## Troubleshooting

### Database Connection Failed

**Problem**: `connection timeout after 10 seconds`

**Solution**:
1. Verify DATABASE_URL is correct
2. Check database server is running and accessible
3. Increase DB_TIMEOUT if network is slow
4. Check firewall rules and network security groups

### KeyVault Authentication Failed

**Problem**: `Forbidden` or `Permission denied` error

**Solution**:
1. Verify AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID are correct
2. Check service principal has `Key Vault Secrets Officer` role
3. Verify KeyVault name matches AZURE_KEYVAULT_NAME
4. Check KeyVault firewall settings

### Metrics Query Failed

**Problem**: `Invalid resource ID format`

**Solution**:
1. Verify VM_RESOURCE_ID format: `/subscriptions/{id}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vm}`
2. Check subscription ID and resource group name are correct
3. Ensure managed identity has `Monitoring Reader` role

### High Latency on API Tests

**Problem**: API responses taking too long

**Solution**:
1. Check network connectivity to API endpoints
2. Increase API_TIMEOUT if endpoints are slow
3. Check if endpoints have rate limiting
4. Monitor Azure Monitor for network issues

### Out of Memory

**Problem**: Service running out of memory

**Solution**:
1. Reduce number of concurrent API requests
2. Implement pagination for large test lists
3. Allocate more memory to container: `docker run -m 2g ...`

## Performance Considerations

- **Concurrent Requests**: Uses `httpx.AsyncClient` for concurrent API testing
- **Connection Pooling**: Reuses connections for better performance
- **Retry Logic**: Exponential backoff prevents retry storms
- **Timeout Management**: All operations have configurable timeouts
- **Resource Cleanup**: Properly closes database connections and HTTP clients

## Security Best Practices

1. **Never commit `.env` file** - Use `.env.example` as template
2. **Use Managed Identity** when possible instead of client secrets
3. **Enable HTTPS** for production deployments
4. **Rotate secrets** regularly
5. **Use strong passwords** for database connections
6. **Enable audit logging** in Azure services
7. **Implement rate limiting** on API endpoints
8. **Use network security groups** to restrict access

## Logging

The service uses structured JSON logging for easy parsing:

```json
{
  "timestamp": "2024-11-14T10:30:00.123456",
  "service": "smoke-test-bot",
  "version": "1.0.0",
  "level": "INFO",
  "message": "Database check completed",
  "latency_ms": 125.50,
  "run_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

Set `LOG_LEVEL` to control verbosity:
- `DEBUG`: Detailed diagnostic information
- `INFO`: Informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages only

## API Documentation

Interactive API documentation available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues, questions, or suggestions:

1. Check troubleshooting section above
2. Review test files for usage examples
3. Check Azure documentation for service-specific issues
4. Submit GitHub issue with detailed error logs

## Version History

### v1.0.0 (2024-11-14)
- Initial release
- Database connectivity checks
- API endpoint validation
- Azure KeyVault secret verification
- Azure Monitor VM metrics collection
- Comprehensive test coverage
- Production-ready Dockerfile
- Full API documentation
