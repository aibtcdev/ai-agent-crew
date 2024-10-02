clarityHints = """
### Clarity Hints

- all Clarity code blocks should start with ```clarity
- reentrancy is not possible at the language level, transactions are atomic
- traits are a defined interface that can be implemented by contracts
- `contract-caller` represents the principal that called the contract
- `tx-sender` represents the principal that initiated the transaction and can be another contract
- `as-contract` is used to switch calling context from user to contract
- `contract-call?` is used to interact with other contracts
- `try!`, `unwrap!`, `unwrap-err!` are used to handle control flow
"""
