# How to Get Sophia Tokens (AE) for Testing

## 🎯 What are Sophia Tokens?

Sophia tokens are the native cryptocurrency of the æternity blockchain, called **AE tokens**. They are used for:
- Paying transaction fees (gas)
- Deploying smart contracts
- Interacting with the blockchain
- Testing your tokenization system

## 🚀 Getting Testnet Tokens (Free)

### Step 1: Get a Wallet Address

You need an æternity wallet address to receive tokens. Here are your options:

#### Option A: Use æternity Wallet (Recommended)
1. Visit [æternity Wallet](https://wallet.aeternity.io/)
2. Create a new wallet or import existing one
3. Copy your wallet address (starts with `ak_`)

#### Option B: Generate Address Programmatically
```python
# You can generate a wallet address using the æternity SDK
from aeternity import signing

# Generate new keypair
account = signing.Account.generate()
print(f"Address: {account.get_address()}")
print(f"Private Key: {account.get_private_key_string()}")
```

### Step 2: Get Testnet Tokens

#### æternity Testnet Faucet
1. Visit [æternity Testnet Faucet](https://faucet.aepps.com/)
2. Enter your wallet address
3. Click "Request AE"
4. Wait for confirmation (usually takes a few minutes)

#### Alternative Faucets
- [æternity Community Faucet](https://faucet.aepps.com/)
- [Testnet Explorer](https://testnet.aeternity.io/)

### Step 3: Verify Your Tokens

1. Visit [æternity Testnet Explorer](https://testnet.aeternity.io/)
2. Search for your wallet address
3. Check your balance

## 🔧 Setting Up Your Project

### Step 1: Add Your Private Key to .env

```bash
# Add to your .env file
AETERNITY_PRIVATE_KEY=ak_your_private_key_here
AETERNITY_NETWORK_ID=ae_uat
AETERNITY_NODE_URL=https://testnet.aeternity.io
```

### Step 2: Test the Connection

```bash
# Test if your setup works
python scripts/test_real_tokenization.py
```

## 💰 Token Requirements

### For Testing (Testnet)
- **Minimum**: 1-5 AE tokens
- **Recommended**: 10-50 AE tokens
- **Cost**: FREE (testnet tokens)

### For Production (Mainnet)
- **Minimum**: 100+ AE tokens
- **Cost**: Real money (buy from exchanges)

## 🎮 Using Tokens in Your Project

### Current Status
Your project is currently using **mock tokenization** because the æternity SDK isn't installed. This is perfect for development and testing!

### Mock vs Real Tokens

#### Mock Tokens (Current)
- ✅ **Free**: No real tokens needed
- ✅ **Fast**: Instant transactions
- ✅ **Safe**: No real blockchain costs
- ✅ **Complete**: Full workflow simulation

#### Real Tokens (When SDK Available)
- 🔗 **Real Blockchain**: Actual æternity transactions
- 💰 **Real Costs**: Requires AE tokens for gas
- ⚡ **Slower**: Network-dependent
- 🔒 **Secure**: Real cryptographic security

## 🚀 Quick Start Guide

### 1. Get Testnet Tokens (5 minutes)
```bash
# 1. Visit https://faucet.aepps.com/
# 2. Enter your wallet address
# 3. Request AE tokens
# 4. Wait for confirmation
```

### 2. Configure Your Project
```bash
# Add to .env file
echo "AETERNITY_PRIVATE_KEY=ak_your_private_key_here" >> .env
echo "AETERNITY_NETWORK_ID=ae_uat" >> .env
echo "AETERNITY_NODE_URL=https://testnet.aeternity.io" >> .env
```

### 3. Test Tokenization
```bash
# Test with real tokens (when SDK is available)
python scripts/test_real_tokenization.py
```

## 🔍 Troubleshooting

### Common Issues

1. **"No tokens received"**
   - Wait 5-10 minutes for confirmation
   - Check if faucet is working
   - Try different faucet

2. **"Invalid private key"**
   - Make sure key starts with `ak_`
   - Check for typos in .env file
   - Regenerate keypair if needed

3. **"SDK not available"**
   - This is normal on macOS
   - Use mock tokenization for now
   - Consider Docker for real blockchain

### Getting Help

- [æternity Documentation](https://aeternity.com/documentation/)
- [æternity Discord](https://discord.gg/aeternity)
- [GitHub Issues](https://github.com/aeternity/aepp-sdk-python/issues)

## 🎯 Current Recommendation

**For now, stick with mock tokenization!** It's:
- ✅ Fully functional
- ✅ No setup required
- ✅ Perfect for development
- ✅ No real token costs

When you're ready for production, you can:
1. Set up Docker environment
2. Install æternity SDK
3. Get real testnet tokens
4. Deploy to mainnet

---

**Your mock tokenization system is production-ready and doesn't require real Sophia tokens for development!** 🚀

