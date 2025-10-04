# Buddi Tokenization PoC

A proof-of-concept system for tokenizing user conversation summaries from the Buddi API on the æternity blockchain using Sophia smart contracts.

## Architecture

1. **Data Fetching**: Fetch conversation summaries from Buddi API
2. **Tokenization**: Deploy smart contracts on æternity blockchain
3. **Storage**: Store data in PostgreSQL database
4. **Analytics**: Analyze conversations for sentiment and keywords
5. **UI**: FastAPI dashboard for data visualization

## Tech Stack

- Python 3.8+
- FastAPI
- æternity Python SDK
- PostgreSQL
- Sophia smart contracts
- HuggingFace Transformers

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables: `cp .env.example .env`
3. Run database migrations: `alembic upgrade head`
4. Start the application: `uvicorn app.main:app --reload`

## Project Structure

```
buddi-chain/
├── app/
│   ├── api/           # FastAPI routes
│   ├── core/          # Core configuration
│   ├── db/            # Database models and connection
│   ├── services/      # Business logic
│   └── main.py        # FastAPI application
├── contracts/         # Sophia smart contracts
├── data/             # Data storage
│   ├── raw/          # Raw API data
│   └── processed/    # Processed datasets
├── scripts/          # Utility scripts
└── tests/            # Test files
```
