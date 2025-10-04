# Buddi Conversation Scheduler

This document describes the periodic conversation fetching and processing system for the Buddi Tokenization PoC.

## Overview

The scheduler automatically fetches new conversations from the Buddi API every 1-2 hours, processes them through analytics and tokenization, and stores them in the database. It includes duplicate detection, error handling, and rate limiting.

## Features

- **Periodic Fetching**: Automatically fetches conversations every 2 hours (configurable)
- **Duplicate Detection**: Skips conversations already in the database
- **Rate Limiting**: Prevents excessive API calls
- **Error Handling**: Graceful error recovery and logging
- **Analytics Processing**: Automatic sentiment analysis and quality scoring
- **Tokenization**: Mock blockchain tokenization for each conversation
- **API Management**: RESTful API for controlling the scheduler

## Components

### 1. Scheduler Service (`app/services/scheduler.py`)

The main scheduler class that handles:
- Periodic conversation fetching
- Duplicate detection
- Batch processing
- Error handling and recovery

### 2. Management Script (`manage_scheduler.py`)

Command-line tool for managing the scheduler:

```bash
# Start the scheduler
python manage_scheduler.py start

# Stop the scheduler
python manage_scheduler.py stop

# Run a manual fetch
python manage_scheduler.py fetch

# Check scheduler status
python manage_scheduler.py status
```

### 3. Background Runner (`scripts/run_scheduler.py`)

Long-running script for continuous operation:

```bash
# Run in foreground
python scripts/run_scheduler.py

# Run in background
nohup python scripts/run_scheduler.py > scheduler.log 2>&1 &
```

### 4. API Endpoints (`app/api/scheduler.py`)

RESTful API for scheduler management:

- `GET /api/scheduler/status` - Get scheduler status
- `POST /api/scheduler/start` - Start the scheduler
- `POST /api/scheduler/stop` - Stop the scheduler
- `POST /api/scheduler/fetch` - Manual fetch
- `POST /api/scheduler/config` - Update configuration

## Configuration

### Environment Variables

```bash
# Buddi API Configuration
BUDDI_API_BASE_URL=https://apis.getbuddi.ai/v1/dev
BUDDI_API_KEY=your_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///./buddi_chain.db

# Scheduler Configuration (optional)
SCHEDULER_FETCH_INTERVAL_HOURS=2
SCHEDULER_MAX_CONVERSATIONS_PER_FETCH=50
```

### Scheduler Settings

- **Fetch Interval**: 2 hours (configurable 1-24 hours)
- **Max Conversations per Fetch**: 50 (configurable 1-1000)
- **Rate Limiting**: Minimum 1 hour between fetches
- **Error Recovery**: 5-minute delay on errors

## Usage

### 1. Start the Scheduler

```bash
# Using management script
python manage_scheduler.py start

# Using background runner
python scripts/run_scheduler.py

# Using systemd (production)
sudo systemctl start buddi-scheduler
```

### 2. Monitor Status

```bash
# Check status via CLI
python manage_scheduler.py status

# Check status via API
curl http://localhost:8000/api/scheduler/status

# View logs
tail -f scheduler.log
```

### 3. Manual Operations

```bash
# Trigger manual fetch
python manage_scheduler.py fetch

# Or via API
curl -X POST http://localhost:8000/api/scheduler/fetch
```

### 4. Configuration Updates

```bash
# Update fetch interval to 1 hour
curl -X POST "http://localhost:8000/api/scheduler/config?fetch_interval_hours=1"

# Update max conversations to 100
curl -X POST "http://localhost:8000/api/scheduler/config?max_conversations_per_fetch=100"
```

## Production Deployment

### 1. Systemd Service

Copy the service file to systemd directory:

```bash
sudo cp scripts/buddi-scheduler.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable buddi-scheduler
sudo systemctl start buddi-scheduler
```

### 2. Log Management

```bash
# View logs
sudo journalctl -u buddi-scheduler -f

# View recent logs
sudo journalctl -u buddi-scheduler --since "1 hour ago"
```

### 3. Monitoring

```bash
# Check service status
sudo systemctl status buddi-scheduler

# Check if running
ps aux | grep run_scheduler.py
```

## Database Schema

The scheduler populates the `conversations` table with:

- **Raw Data**: Summary, actions, metadata from Buddi API
- **Analytics**: Sentiment, topics, keywords, quality scores
- **Tokenization**: Anchor ID, token ID, Merkle root, contract addresses
- **Timestamps**: Created/updated timestamps
- **Status**: Processing and export flags

## Error Handling

### Common Issues

1. **API Rate Limiting**: Scheduler respects rate limits and waits
2. **Duplicate Conversations**: Automatically detected and skipped
3. **Database Errors**: Transactions rolled back on errors
4. **Network Issues**: Automatic retry with exponential backoff

### Logging

All operations are logged with appropriate levels:
- **INFO**: Normal operations and status updates
- **WARNING**: Non-critical issues (rate limiting, empty responses)
- **ERROR**: Processing failures and exceptions
- **DEBUG**: Detailed operation information

## Monitoring and Alerts

### Key Metrics

- **Fetch Success Rate**: Percentage of successful fetches
- **Processing Rate**: Conversations processed per hour
- **Error Rate**: Failed operations per hour
- **Database Growth**: New conversations per day

### Health Checks

```bash
# Check if scheduler is running
curl -s http://localhost:8000/api/scheduler/status | jq '.is_running'

# Check last fetch time
curl -s http://localhost:8000/api/scheduler/status | jq '.last_fetch_time'

# Check conversation count
curl -s http://localhost:8000/conversations/ | jq '.total'
```

## Troubleshooting

### Scheduler Not Starting

1. Check API key configuration
2. Verify database connectivity
3. Check Python environment and dependencies
4. Review logs for specific errors

### No New Conversations

1. Check API endpoint and authentication
2. Verify date parameters in API calls
3. Check if all conversations are already processed
4. Review rate limiting settings

### High Error Rate

1. Check network connectivity
2. Verify API endpoint availability
3. Review database performance
4. Check for resource constraints

## Development

### Testing

```bash
# Test manual fetch
python manage_scheduler.py fetch

# Test API endpoints
curl -X POST http://localhost:8000/api/scheduler/fetch

# Test configuration updates
curl -X POST "http://localhost:8000/api/scheduler/config?fetch_interval_hours=1"
```

### Debugging

Enable debug logging by modifying the logging level in `app/services/scheduler.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

- **API Key**: Store securely in environment variables
- **Database**: Use proper authentication and encryption
- **Network**: Use HTTPS for API communications
- **Access Control**: Restrict scheduler API endpoints in production

## Performance Optimization

- **Batch Processing**: Process multiple conversations in batches
- **Connection Pooling**: Reuse database connections
- **Caching**: Cache frequently accessed data
- **Resource Limits**: Monitor memory and CPU usage

## Future Enhancements

- **Real Blockchain Integration**: Replace mock tokenization with real æternity contracts
- **Advanced Analytics**: Add more sophisticated analysis algorithms
- **Webhook Support**: Real-time conversation processing
- **Distributed Processing**: Scale across multiple instances
- **Advanced Monitoring**: Prometheus metrics and Grafana dashboards
