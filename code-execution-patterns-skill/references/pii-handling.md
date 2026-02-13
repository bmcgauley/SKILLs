# PII Handling and Tokenization Patterns

**Last Updated**: 2025-11-09

## Overview

When processing data containing Personally Identifiable Information (PII), it's critical to keep sensitive data out of the conversation context. This guide explains patterns for securely handling PII in agent code execution.

## What is PII?

**Personally Identifiable Information** includes:

- Email addresses
- Phone numbers
- Social Security Numbers (SSN)
- Credit card numbers
- IP addresses
- Physical addresses
- Names (in some contexts)
- Medical record numbers
- Financial account numbers
- Biometric data
- Government IDs

## The PII Problem in Context

### Why PII in Context is Risky

1. **Conversation logs** may be stored
2. **Context window** persists across interactions
3. **Error messages** might expose PII
4. **Debugging logs** could leak sensitive data
5. **Model training** (depending on provider policies)

### Example: Unsafe PII Handling

```python
# ❌ DANGEROUS - PII flows through context
async def analyze_user_feedback(feedback_text: str):
    # feedback_text = "Contact me at john.doe@email.com or 555-123-4567"

    # PII now in conversation context!
    sentiment = await mcp.call("analyze_sentiment", {
        "text": feedback_text  # Contains email and phone
    })

    entities = await mcp.call("extract_entities", {
        "text": feedback_text  # PII exposed again
    })

    # PII remains in context throughout conversation
    return {
        "sentiment": sentiment,
        "entities": entities,
        "original": feedback_text  # PII in response!
    }
```

## Tokenization Solution

### What is PII Tokenization?

**Tokenization** replaces PII with placeholder tokens:

- Original: `"Contact me at john.doe@email.com or 555-123-4567"`
- Tokenized: `"Contact me at [EMAIL_1] or [PHONE_1]"`

The mapping between tokens and original values is stored securely **outside the conversation context**.

### Basic Tokenization Pattern

```python
# ✅ SAFE - PII tokenized before context interaction
async def analyze_user_feedback_safe(feedback_text: str):
    # Step 1: Tokenize PII in execution environment
    tokenized = await mcp.call("helper_tokenize_pii", {
        "text": feedback_text,
        "pii_types": ["email", "phone", "ssn", "credit_card"]
    })

    # Response:
    # {
    #     "tokenized_text": "Contact me at [EMAIL_1] or [PHONE_1]",
    #     "token_map_id": "tm_abc123",
    #     "tokens_found": {
    #         "EMAIL_1": "email",
    #         "PHONE_1": "phone"
    #     }
    # }

    safe_text = tokenized["tokenized_text"]
    token_map_id = tokenized["token_map_id"]

    # Step 2: Process tokenized text (safe for context)
    sentiment = await mcp.call("analyze_sentiment", {
        "text": safe_text  # No PII!
    })

    entities = await mcp.call("extract_entities", {
        "text": safe_text  # No PII!
    })

    # Step 3: Only detokenize if absolutely necessary
    # Keep results tokenized for security
    return {
        "sentiment": sentiment,
        "entities": entities,
        "text": safe_text,  # Tokenized version only
        "token_map_id": token_map_id  # For later detokenization
    }
```

## Advanced Tokenization Patterns

### Pattern 1: Selective Detokenization

**Use Case**: Only reveal PII when user explicitly needs it.

```python
async def process_with_selective_reveal(user_data: str, reveal_pii: bool = False):
    # Tokenize all PII
    tokenized = await mcp.call("helper_tokenize_pii", {
        "text": user_data,
        "pii_types": ["email", "phone", "ssn", "address", "name"]
    })

    safe_text = tokenized["tokenized_text"]
    token_map_id = tokenized["token_map_id"]

    # Process safely
    analysis = await analyze_text(safe_text)
    insights = await extract_insights(safe_text)

    # Only detokenize if user explicitly requested
    if reveal_pii:
        final_text = await mcp.call("helper_detokenize_pii", {
            "text": analysis["summary"],
            "token_map_id": token_map_id
        })
    else:
        # Keep tokenized for security
        final_text = analysis["summary"]

    return {
        "analysis": analysis,
        "insights": insights,
        "text": final_text,
        "pii_revealed": reveal_pii
    }
```

### Pattern 2: Partial Detokenization

**Use Case**: Reveal some PII types but not others.

```python
async def partial_detokenize(text: str, token_map_id: str, reveal_types: List[str]):
    # Get full token map
    token_map = await mcp.call("helper_get_token_map", {
        "token_map_id": token_map_id
    })

    # Filter to only requested types
    filtered_map = {
        token: value
        for token, value in token_map.items()
        if value["type"] in reveal_types
    }

    # Detokenize only selected types
    result = await mcp.call("helper_detokenize_pii", {
        "text": text,
        "token_map": filtered_map
    })

    return result

# Usage
result = await partial_detokenize(
    text=safe_text,
    token_map_id=token_map_id,
    reveal_types=["email"]  # Reveal emails but not phone/SSN
)
```

### Pattern 3: PII Redaction (Permanent Removal)

**Use Case**: Completely remove PII without ability to recover.

```python
async def redact_pii_permanently(text: str):
    # Redact instead of tokenize
    redacted = await mcp.call("helper_redact_pii", {
        "text": text,
        "pii_types": ["ssn", "credit_card"],
        "replacement": "[REDACTED]"
    })

    # Returns:
    # {
    #     "redacted_text": "SSN: [REDACTED], Card: [REDACTED]",
    #     "redaction_count": 2,
    #     "redacted_types": ["ssn", "credit_card"]
    # }

    # Original PII is gone forever
    return redacted["redacted_text"]
```

### Pattern 4: PII Hashing

**Use Case**: Need to match records without revealing PII.

```python
async def hash_pii_for_matching(email: str, phone: str):
    # Hash PII for matching
    hashed = await mcp.call("helper_hash_pii", {
        "values": {
            "email": email,
            "phone": phone
        },
        "algorithm": "sha256",
        "salt": "unique-salt-per-user"
    })

    # Returns:
    # {
    #     "email_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    #     "phone_hash": "d14a028c2a3a2bc9476102bb288234c415a2b01f828ea62ac5b3e42f"
    # }

    # Can match records without storing actual PII
    return {
        "email_hash": hashed["email_hash"],
        "phone_hash": hashed["phone_hash"]
    }
```

## Multi-Document Processing

### Pattern: Consistent Tokenization Across Documents

**Use Case**: Process multiple documents from same user with consistent tokens.

```python
async def process_user_documents(documents: List[str], user_id: str):
    # Use user-specific token map
    token_map_id = f"user_{user_id}_tokenmap"

    tokenized_docs = []
    for doc in documents:
        tokenized = await mcp.call("helper_tokenize_pii", {
            "text": doc,
            "pii_types": ["email", "phone", "name"],
            "token_map_id": token_map_id  # Reuse same map
        })

        # Same PII gets same token across documents
        # john.doe@email.com → [EMAIL_1] in all documents
        tokenized_docs.append(tokenized["tokenized_text"])

    # Process all documents with consistent tokens
    combined_analysis = await analyze_multiple_documents(tokenized_docs)

    return {
        "analysis": combined_analysis,
        "documents_processed": len(documents),
        "token_map_id": token_map_id
    }
```

## Storage and Lifecycle Management

### Secure Token Map Storage

```python
async def create_secure_token_map(text: str):
    # Tokenize with secure storage
    tokenized = await mcp.call("helper_tokenize_pii", {
        "text": text,
        "pii_types": ["email", "phone", "ssn"],
        "storage": {
            "location": "encrypted_storage",
            "encryption": "AES-256",
            "access_control": "strict"
        },
        "ttl": 3600  # Auto-delete after 1 hour
    })

    return tokenized
```

### Token Map Expiration

```python
async def process_with_expiration(text: str):
    # Create token map with TTL
    tokenized = await mcp.call("helper_tokenize_pii", {
        "text": text,
        "pii_types": ["email", "phone"],
        "ttl": 1800  # 30 minutes
    })

    safe_text = tokenized["tokenized_text"]
    token_map_id = tokenized["token_map_id"]

    # Process within TTL window
    result = await process_text(safe_text)

    # Explicitly delete token map when done
    await mcp.call("helper_delete_token_map", {
        "token_map_id": token_map_id
    })

    return result
```

## Compliance Patterns

### GDPR: Right to be Forgotten

```python
async def delete_user_pii(user_id: str):
    # Delete all token maps for user
    token_maps = await mcp.call("helper_list_token_maps", {
        "user_id": user_id
    })

    for token_map_id in token_maps:
        await mcp.call("helper_delete_token_map", {
            "token_map_id": token_map_id
        })

    # Verify deletion
    remaining = await mcp.call("helper_list_token_maps", {
        "user_id": user_id
    })

    return {
        "deleted_count": len(token_maps),
        "remaining_count": len(remaining),
        "fully_deleted": len(remaining) == 0
    }
```

### HIPAA: Audit Logging

```python
async def process_medical_data_with_audit(patient_data: str, processor_id: str):
    # Tokenize medical data
    tokenized = await mcp.call("helper_tokenize_pii", {
        "text": patient_data,
        "pii_types": ["ssn", "medical_record_number", "name"],
        "audit": {
            "enabled": True,
            "processor_id": processor_id,
            "purpose": "medical_analysis",
            "timestamp": datetime.utcnow().isoformat()
        }
    })

    # All access is logged
    safe_text = tokenized["tokenized_text"]
    token_map_id = tokenized["token_map_id"]

    # Process data
    result = await analyze_medical_data(safe_text)

    # Audit detokenization
    if needs_original:
        detokenized = await mcp.call("helper_detokenize_pii", {
            "text": result["summary"],
            "token_map_id": token_map_id,
            "audit": {
                "processor_id": processor_id,
                "reason": "physician_review"
            }
        })

    return result
```

## Error Handling

### Safe Error Messages

```python
async def safe_error_handling(user_input: str):
    try:
        # Tokenize first
        tokenized = await mcp.call("helper_tokenize_pii", {
            "text": user_input,
            "pii_types": ["email", "phone", "ssn"]
        })

        # Process tokenized data
        result = await process_data(tokenized["tokenized_text"])

        return result

    except Exception as e:
        # ❌ DANGEROUS - May expose PII
        # raise Exception(f"Failed to process: {user_input}")

        # ✅ SAFE - No PII in error
        raise Exception(f"Failed to process input (length: {len(user_input)})")
```

## Testing PII Handling

### Unit Tests for Tokenization

```python
import pytest

@pytest.mark.asyncio
async def test_pii_tokenization():
    input_text = "Contact john.doe@example.com or 555-123-4567"

    tokenized = await mcp.call("helper_tokenize_pii", {
        "text": input_text,
        "pii_types": ["email", "phone"]
    })

    # Verify PII removed
    assert "@example.com" not in tokenized["tokenized_text"]
    assert "555-123-4567" not in tokenized["tokenized_text"]

    # Verify tokens present
    assert "[EMAIL_" in tokenized["tokenized_text"]
    assert "[PHONE_" in tokenized["tokenized_text"]

    # Verify reversible
    detokenized = await mcp.call("helper_detokenize_pii", {
        "text": tokenized["tokenized_text"],
        "token_map_id": tokenized["token_map_id"]
    })

    assert detokenized == input_text
```

### Integration Tests for PII Pipeline

```python
@pytest.mark.asyncio
async def test_pii_pipeline():
    # Realistic input with multiple PII types
    user_feedback = """
    Hi, I'm Jane Smith (SSN: 123-45-6789).
    Contact me at jane.smith@email.com or 555-987-6543.
    My address is 123 Main St, Anytown, CA 12345.
    """

    # Process safely
    result = await process_user_feedback_safe(user_feedback)

    # Verify no PII in result
    assert "123-45-6789" not in str(result)
    assert "jane.smith@email.com" not in str(result)
    assert "555-987-6543" not in str(result)
    assert "Jane Smith" not in str(result)

    # Verify processing occurred
    assert "sentiment" in result
    assert "entities" in result

    # Verify can retrieve if needed
    if result.get("token_map_id"):
        original = await mcp.call("helper_detokenize_pii", {
            "text": result["text"],
            "token_map_id": result["token_map_id"]
        })
        # Original data matches
        assert all(pii in original for pii in [
            "jane.smith@email.com",
            "555-987-6543"
        ])
```

## Best Practices

### 1. Tokenize Early, Detokenize Late (or Never)

```python
# ✅ GOOD
async def process_data(raw_data: str):
    # Tokenize immediately
    tokenized = await tokenize_pii(raw_data)

    # Process tokenized data
    result = await process(tokenized["tokenized_text"])

    # Return tokenized (don't detokenize unless necessary)
    return result
```

### 2. Minimal PII Types

```python
# Only tokenize what you need to protect
tokenized = await mcp.call("helper_tokenize_pii", {
    "text": text,
    "pii_types": ["ssn", "credit_card"]  # Only high-risk PII
})
```

### 3. Short Token Map Lifetimes

```python
# Set appropriate TTL
tokenized = await mcp.call("helper_tokenize_pii", {
    "text": text,
    "pii_types": ["email", "phone"],
    "ttl": 1800  # 30 minutes, not 24 hours
})
```

### 4. Audit All Access

```python
# Log all tokenization/detokenization
tokenized = await mcp.call("helper_tokenize_pii", {
    "text": text,
    "pii_types": ["ssn"],
    "audit": {
        "enabled": True,
        "user_id": current_user_id,
        "purpose": "fraud_detection"
    }
})
```

### 5. Never Log PII

```python
# ❌ BAD
logger.info(f"Processing: {user_email}")

# ✅ GOOD
logger.info(f"Processing user: {user_id}")
```

## Summary

**Key Principles**:

1. **Tokenize before context** - PII should never enter conversation
2. **Store token maps securely** - Encrypted, access-controlled, short TTL
3. **Minimize detokenization** - Only when absolutely necessary
4. **Audit everything** - Log all PII access
5. **Delete promptly** - Short TTLs, explicit cleanup

**Benefits**:

- **Compliance** with GDPR, HIPAA, CCPA
- **Security** against data leaks
- **Privacy** for users
- **Auditability** of PII access

**Remember**: When in doubt, tokenize! It's easier to detokenize later than to remove PII from logs.
