# æternity Blockchain Integration Setup

This guide explains how to set up real æternity blockchain tokenization for the Buddi Tokenization PoC.

## 🚀 Quick Start

### 1. Install æternity SDK

```bash
# Install the æternity Python SDK from GitHub
python scripts/install_aeternity_sdk.py
```

### 2. Configure æternity Settings

Add your æternity private key to the `.env` file:

```bash
# æternity Blockchain Configuration
AETERNITY_NETWORK_ID=ae_uat  # or ae_mainnet for mainnet
AETERNITY_NODE_URL=https://testnet.aeternity.io  # or mainnet URL
AETERNITY_PRIVATE_KEY=your_private_key_here
```

### 3. Test Real Tokenization

```bash
# Test the real æternity blockchain integration
python scripts/test_real_tokenization.py
```

## 🔧 Configuration Options

### Network Configuration

| Network | Network ID | Node URL | Description |
|---------|------------|----------|-------------|
| Testnet | `ae_uat` | `https://testnet.aeternity.io` | Development and testing |
| Mainnet | `ae_mainnet` | `https://mainnet.aeternity.io` | Production use |

### Environment Variables

```bash
# Required for real tokenization
AETERNITY_PRIVATE_KEY=ak_...  # Your æternity private key
AETERNITY_NETWORK_ID=ae_uat   # Network identifier
AETERNITY_NODE_URL=https://testnet.aeternity.io  # Node URL

# Optional
AETERNITY_GAS_LIMIT=1000000   # Gas limit for transactions
AETERNITY_GAS_PRICE=1000000000  # Gas price in aettos
```

## 🏗️ Smart Contracts

The system uses two Sophia smart contracts:

### 1. AnchorRegistry.aes
- **Purpose**: Anchors conversation data to the blockchain
- **Functions**: `anchor()`, `verify_anchor()`
- **Deployment**: Automatic on first use

### 2. AccessNFT.aes
- **Purpose**: Mints NFTs representing conversation ownership
- **Functions**: `mint()`, `owner_of()`, `transfer()`
- **Deployment**: Automatic on first use

## 🔄 Tokenization Process

### Real Blockchain Flow

1. **Data Preparation**
   - Calculate Merkle root hash of conversation data
   - Create manifest and policy JSON
   - Prepare storage hint

2. **Contract Deployment**
   - Deploy AnchorRegistry contract
   - Deploy AccessNFT contract
   - Store contract addresses

3. **Data Anchoring**
   - Call `AnchorRegistry.anchor()` with Merkle root
   - Get anchor ID from transaction result
   - Verify anchor creation

4. **NFT Minting**
   - Call `AccessNFT.mint()` with user wallet and anchor ID
   - Get token ID from transaction result
   - Verify NFT ownership

5. **Database Storage**
   - Save all blockchain metadata
   - Store transaction hashes
   - Update conversation status

## 🧪 Testing

### Test Scripts

```bash
# Install and test æternity SDK
python scripts/install_aeternity_sdk.py

# Test real tokenization
python scripts/test_real_tokenization.py

# Test with specific conversation
python scripts/fetch_real_conversations.py
```

### Manual Testing

```python
from app.services.real_tokenization import RealTokenizationService

# Initialize service
service = RealTokenizationService()

# Deploy contracts
anchor_addr, nft_addr = await service.deploy_contracts()

# Tokenize conversation
result = await service.tokenize_conversation(
    conversation_data=your_data,
    user_wallet="ak_your_wallet_address",
    token_uri="https://buddi.ai/memory/123"
)
```

## 🔒 Security Considerations

### Private Key Management
- **Never commit private keys to version control**
- Use environment variables or secure key management
- Consider using hardware wallets for production

### Network Security
- Use testnet for development
- Verify all transactions before mainnet deployment
- Implement proper error handling and retry logic

### Gas Management
- Set appropriate gas limits
- Monitor gas prices
- Implement gas estimation

## 🚨 Troubleshooting

### Common Issues

1. **SDK Import Error**
   ```bash
   # Solution: Install æternity SDK
   python scripts/install_aeternity_sdk.py
   ```

2. **Private Key Not Found**
   ```bash
   # Solution: Add to .env file
   echo "AETERNITY_PRIVATE_KEY=your_key_here" >> .env
   ```

3. **Network Connection Error**
   ```bash
   # Solution: Check node URL and network ID
   # Testnet: https://testnet.aeternity.io
   # Mainnet: https://mainnet.aeternity.io
   ```

4. **Contract Deployment Failed**
   ```bash
   # Solution: Check gas settings and account balance
   # Ensure sufficient AE tokens for deployment
   ```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Resources

- [æternity Python SDK](https://github.com/aeternity/aepp-sdk-python)
- [æternity Documentation](https://aeternity.com/documentation/)
- [Sophia Language Reference](https://aeternity.com/sophia/)
- [Testnet Faucet](https://faucet.aepps.com/)

## 🔄 Migration from Mock to Real

The system automatically detects if the æternity SDK is available and configured:

- **SDK Available + Private Key Set**: Uses real blockchain
- **SDK Missing or No Private Key**: Falls back to mock implementation

No code changes required - just install the SDK and configure your private key!

## 🎯 Production Deployment

### Checklist

- [ ] Install æternity SDK
- [ ] Configure mainnet settings
- [ ] Set production private key
- [ ] Deploy contracts to mainnet
- [ ] Test with small amounts
- [ ] Monitor gas costs
- [ ] Set up error monitoring
- [ ] Implement backup strategies

### Monitoring

- Track transaction success rates
- Monitor gas costs
- Log all blockchain interactions
- Set up alerts for failures

## 💡 Best Practices

1. **Start with Testnet**: Always test on testnet first
2. **Use Environment Variables**: Never hardcode sensitive data
3. **Implement Retry Logic**: Handle network failures gracefully
4. **Monitor Gas Costs**: Optimize gas usage for cost efficiency
5. **Error Handling**: Provide meaningful error messages
6. **Logging**: Log all blockchain interactions for debugging
7. **Testing**: Write comprehensive tests for all scenarios

---

**Note**: The æternity Python SDK repository was archived on August 12, 2024. This integration uses the archived version for compatibility. Consider migrating to newer alternatives if available.
