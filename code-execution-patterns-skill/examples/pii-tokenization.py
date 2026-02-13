"""
PII Tokenization and Secure Data Handling

This example demonstrates:
- Tokenizing PII before any context interaction
- Keeping sensitive data out of conversation context
- Selective detokenization
- Partial detokenization (reveal some PII types, not others)
- Secure token map management

Author: Code Execution Patterns Skill
License: MIT
"""

import asyncio
import re
import hashlib
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class TokenMap:
    """Represents a PII token mapping"""
    token_map_id: str
    tokens: Dict[str, Dict[str, str]]  # token -> {original, type}
    created_at: datetime
    expires_at: datetime


# Simulated secure storage for token maps
TOKEN_MAP_STORAGE = {}


class MCPClient:
    """Simulated MCP client with PII tokenization"""

    async def call(self, tool_name: str, params: dict) -> dict:
        """Call an MCP tool"""
        print(f"[MCP] {tool_name}")

        if "tokenize_pii" in tool_name:
            return await self._tokenize_pii(params)
        elif "detokenize_pii" in tool_name:
            return await self._detokenize_pii(params)
        elif "delete_token_map" in tool_name:
            return self._delete_token_map(params)

        return {"success": True}

    async def _tokenize_pii(self, params: dict) -> dict:
        """Tokenize PII in text"""
        text = params["text"]
        pii_types = params.get("pii_types", ["email", "phone", "ssn"])
        ttl = params.get("ttl", 3600)  # 1 hour default
        token_map_id = params.get("token_map_id") or f"tm_{uuid.uuid4().hex[:12]}"

        # Find and replace PII
        tokens = {}
        tokenized_text = text

        # Email addresses
        if "email" in pii_types:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)

            for i, email in enumerate(emails, 1):
                token = f"[EMAIL_{i}]"
                tokens[token] = {"original": email, "type": "email"}
                tokenized_text = tokenized_text.replace(email, token)

        # Phone numbers
        if "phone" in pii_types:
            phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            phones = re.findall(phone_pattern, text)

            for i, phone in enumerate(phones, 1):
                token = f"[PHONE_{i}]"
                tokens[token] = {"original": phone, "type": "phone"}
                tokenized_text = tokenized_text.replace(phone, token)

        # SSN
        if "ssn" in pii_types:
            ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
            ssns = re.findall(ssn_pattern, text)

            for i, ssn in enumerate(ssns, 1):
                token = f"[SSN_{i}]"
                tokens[token] = {"original": ssn, "type": "ssn"}
                tokenized_text = tokenized_text.replace(ssn, token)

        # Credit cards
        if "credit_card" in pii_types:
            cc_pattern = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
            cards = re.findall(cc_pattern, text)

            for i, card in enumerate(cards, 1):
                token = f"[CARD_{i}]"
                tokens[token] = {"original": card, "type": "credit_card"}
                tokenized_text = tokenized_text.replace(card, token)

        # Names (simple pattern - in production use NER)
        if "name" in pii_types:
            name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
            names = re.findall(name_pattern, text)

            for i, name in enumerate(names, 1):
                token = f"[NAME_{i}]"
                tokens[token] = {"original": name, "type": "name"}
                tokenized_text = tokenized_text.replace(name, token)

        # Store token map
        token_map = TokenMap(
            token_map_id=token_map_id,
            tokens=tokens,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=ttl)
        )
        TOKEN_MAP_STORAGE[token_map_id] = token_map

        return {
            "tokenized_text": tokenized_text,
            "token_map_id": token_map_id,
            "tokens_found": {
                token: info["type"]
                for token, info in tokens.items()
            },
            "pii_count": len(tokens)
        }

    async def _detokenize_pii(self, params: dict) -> str:
        """Detokenize PII in text"""
        text = params["text"]
        token_map_id = params["token_map_id"]
        reveal_types = params.get("reveal_types")  # Optional: only reveal certain types

        # Get token map
        if token_map_id not in TOKEN_MAP_STORAGE:
            raise Exception(f"Token map {token_map_id} not found or expired")

        token_map = TOKEN_MAP_STORAGE[token_map_id]

        # Check expiration
        if datetime.utcnow() > token_map.expires_at:
            del TOKEN_MAP_STORAGE[token_map_id]
            raise Exception(f"Token map {token_map_id} expired")

        # Replace tokens with originals
        detokenized = text

        for token, info in token_map.tokens.items():
            # If reveal_types specified, only reveal those types
            if reveal_types and info["type"] not in reveal_types:
                continue

            detokenized = detokenized.replace(token, info["original"])

        return detokenized

    def _delete_token_map(self, params: dict) -> dict:
        """Delete a token map"""
        token_map_id = params["token_map_id"]

        if token_map_id in TOKEN_MAP_STORAGE:
            del TOKEN_MAP_STORAGE[token_map_id]
            return {"success": True, "deleted": True}

        return {"success": False, "error": "Token map not found"}


# Initialize MCP client
mcp = MCPClient()


async def process_user_feedback_unsafe(feedback: str) -> Dict[str, Any]:
    """
    ❌ UNSAFE: PII flows through context

    This is what NOT to do!
    """
    print("\n=== UNSAFE PROCESSING (Anti-pattern) ===")
    print(f"Original feedback (with PII): {feedback}")

    # PII is now in conversation context!
    # This would be logged, stored in conversation history, etc.

    # Analyze sentiment (PII exposed in context)
    sentiment = "positive"  # Simulated

    # Extract entities (PII exposed again)
    entities = ["email", "phone"]  # Simulated

    return {
        "feedback": feedback,  # PII in response!
        "sentiment": sentiment,
        "entities": entities
    }


async def process_user_feedback_safe(feedback: str) -> Dict[str, Any]:
    """
    ✅ SAFE: PII tokenized before context interaction

    This is the correct pattern!
    """
    print("\n=== SAFE PROCESSING (Correct pattern) ===")
    print(f"Original feedback length: {len(feedback)} chars")

    # Step 1: Tokenize PII BEFORE any context interaction
    tokenized = await mcp.call("helper_tokenize_pii", {
        "text": feedback,
        "pii_types": ["email", "phone", "ssn", "credit_card", "name"],
        "ttl": 1800  # 30 minutes
    })

    safe_text = tokenized["tokenized_text"]
    token_map_id = tokenized["token_map_id"]

    print(f"Tokenized text: {safe_text}")
    print(f"PII found: {tokenized['pii_count']} items")
    print(f"Token map ID: {token_map_id}")

    # Step 2: Process tokenized text (NO PII in context)
    # All analysis happens on safe text
    sentiment = analyze_sentiment(safe_text)
    entities = extract_entities(safe_text)
    categories = categorize_feedback(safe_text)

    # Step 3: Return tokenized version (keep PII out of response)
    return {
        "feedback": safe_text,  # Tokenized, no PII
        "sentiment": sentiment,
        "entities": entities,
        "categories": categories,
        "token_map_id": token_map_id,  # For later detokenization if needed
        "pii_protected": True
    }


def analyze_sentiment(text: str) -> str:
    """Analyze sentiment (local processing - no PII)"""
    # Simplified sentiment analysis
    positive_words = ["great", "excellent", "good", "love", "amazing"]
    negative_words = ["bad", "poor", "terrible", "hate", "awful"]

    text_lower = text.lower()

    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)

    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"


def extract_entities(text: str) -> List[str]:
    """Extract entities (local processing - no PII)"""
    # Simplified entity extraction
    entities = []

    if "[EMAIL_" in text:
        entities.append("email")
    if "[PHONE_" in text:
        entities.append("phone")
    if "[NAME_" in text:
        entities.append("name")

    return entities


def categorize_feedback(text: str) -> List[str]:
    """Categorize feedback (local processing - no PII)"""
    categories = []

    text_lower = text.lower()

    if any(word in text_lower for word in ["price", "cost", "expensive", "cheap"]):
        categories.append("pricing")
    if any(word in text_lower for word in ["service", "support", "help"]):
        categories.append("customer_service")
    if any(word in text_lower for word in ["product", "quality", "feature"]):
        categories.append("product")

    return categories or ["general"]


async def selective_detokenization_example(safe_text: str, token_map_id: str):
    """
    Example: Only detokenize when user explicitly requests it
    """
    print("\n=== Selective Detokenization ===")

    # Most of the time, keep data tokenized
    print(f"Safe text (tokenized): {safe_text}")

    # Only detokenize if absolutely necessary
    user_wants_original = False  # Would be based on user request

    if user_wants_original:
        print("\nUser requested original data, detokenizing...")
        original = await mcp.call("helper_detokenize_pii", {
            "text": safe_text,
            "token_map_id": token_map_id
        })
        print(f"Original text: {original}")
    else:
        print("\nKeeping data tokenized for security")


async def partial_detokenization_example(safe_text: str, token_map_id: str):
    """
    Example: Reveal some PII types but not others
    """
    print("\n=== Partial Detokenization ===")
    print(f"Tokenized: {safe_text}")

    # Reveal emails but not phone numbers or SSNs
    print("\nRevealing emails only...")
    partially_detokenized = await mcp.call("helper_detokenize_pii", {
        "text": safe_text,
        "token_map_id": token_map_id,
        "reveal_types": ["email"]  # Only reveal emails
    })

    print(f"Partially detokenized: {partially_detokenized}")


async def batch_processing_example(feedbacks: List[str], user_id: str):
    """
    Example: Process multiple documents with consistent tokenization
    """
    print("\n=== Batch Processing with Consistent Tokens ===")

    # Use user-specific token map for consistency
    token_map_id = f"user_{user_id}_tokenmap"

    tokenized_feedbacks = []

    for i, feedback in enumerate(feedbacks):
        print(f"\nProcessing feedback {i + 1}/{len(feedbacks)}...")

        tokenized = await mcp.call("helper_tokenize_pii", {
            "text": feedback,
            "pii_types": ["email", "phone", "name"],
            "token_map_id": token_map_id  # Reuse same map
        })

        # Same PII gets same token across documents
        tokenized_feedbacks.append(tokenized["tokenized_text"])
        print(f"Tokenized: {tokenized['tokenized_text']}")

    # Process all tokenized feedback
    combined_analysis = analyze_multiple_feedbacks(tokenized_feedbacks)

    return {
        "feedbacks_processed": len(feedbacks),
        "analysis": combined_analysis,
        "token_map_id": token_map_id
    }


def analyze_multiple_feedbacks(feedbacks: List[str]) -> Dict[str, Any]:
    """Analyze multiple feedbacks (local processing - no PII)"""
    sentiments = [analyze_sentiment(f) for f in feedbacks]
    all_categories = [categorize_feedback(f) for f in feedbacks]

    return {
        "total": len(feedbacks),
        "sentiments": {
            "positive": sentiments.count("positive"),
            "negative": sentiments.count("negative"),
            "neutral": sentiments.count("neutral")
        },
        "categories": {
            cat: sum(1 for cats in all_categories if cat in cats)
            for cat in set(cat for cats in all_categories for cat in cats)
        }
    }


async def cleanup_token_maps():
    """
    Example: Clean up expired token maps
    """
    print("\n=== Cleaning Up Token Maps ===")

    now = datetime.utcnow()
    expired = []

    for token_map_id, token_map in list(TOKEN_MAP_STORAGE.items()):
        if now > token_map.expires_at:
            expired.append(token_map_id)
            del TOKEN_MAP_STORAGE[token_map_id]

    print(f"Deleted {len(expired)} expired token maps")
    print(f"Active token maps: {len(TOKEN_MAP_STORAGE)}")


async def main():
    """
    Main entry point demonstrating PII handling patterns
    """
    print("\n" + "=" * 60)
    print("PII TOKENIZATION EXAMPLES")
    print("=" * 60)

    # Example feedback with PII
    feedback = """
    Hi, I'm John Doe and I had a great experience!
    You can reach me at john.doe@email.com or 555-123-4567.
    My SSN is 123-45-6789 for account verification.
    """

    # Example 1: Compare unsafe vs safe processing
    print("\n--- Example 1: Unsafe vs Safe Processing ---")

    print("\n⚠ UNSAFE WAY (DON'T DO THIS!):")
    unsafe_result = await process_user_feedback_unsafe(feedback)
    print("❌ PII exposed in context and response!")

    print("\n✅ SAFE WAY (DO THIS!):")
    safe_result = await process_user_feedback_safe(feedback)
    print(f"✓ Sentiment: {safe_result['sentiment']}")
    print(f"✓ Categories: {safe_result['categories']}")
    print("✓ No PII in context or response!")

    # Example 2: Selective detokenization
    print("\n--- Example 2: Selective Detokenization ---")
    await selective_detokenization_example(
        safe_result["feedback"],
        safe_result["token_map_id"]
    )

    # Example 3: Partial detokenization
    print("\n--- Example 3: Partial Detokenization ---")
    await partial_detokenization_example(
        safe_result["feedback"],
        safe_result["token_map_id"]
    )

    # Example 4: Batch processing
    print("\n--- Example 4: Batch Processing ---")
    multiple_feedbacks = [
        "Great service! Contact me at alice@email.com",
        "Poor quality. Call me at 555-999-8888",
        "John Doe here, loved it! Email: john@example.com"
    ]
    batch_result = await batch_processing_example(multiple_feedbacks, "user123")
    print(f"Analysis: {batch_result['analysis']}")

    # Example 5: Cleanup
    print("\n--- Example 5: Token Map Cleanup ---")
    await cleanup_token_maps()

    print("\n" + "=" * 60)
    print("KEY PATTERNS DEMONSTRATED:")
    print("=" * 60)
    print("1. Tokenize BEFORE context interaction")
    print("2. Process tokenized data only")
    print("3. Selective detokenization (only when needed)")
    print("4. Partial detokenization (reveal some types)")
    print("5. Consistent tokens across documents")
    print("6. Automatic token map expiration")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
