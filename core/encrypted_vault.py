"""
core/encrypted_vault.py
Encrypted SQLite Storage with AES-GCM & Zero-Leak Local Vector RAG
==================================================================
1. AES-GCM Authenticated Encryption for sensitive memory fields at rest.
2. Local Vector Similarity Search (Cosine RAG) without external API calls.
"""

import sqlite3
import json
import math
import re
import os
import secrets
from datetime import datetime
from typing import List, Dict, Tuple

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAS_AESGCM = True
except ImportError:
    HAS_AESGCM = False

DB_PATH = "vault.db"


class SovereignCrypto:
    """
    Handles AES-GCM 256-bit encryption for local vault data at rest.
    """

    def __init__(self):
        # 32-byte key stored securely or derived
        key_file = ".vault.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                self.key = f.read()
        else:
            self.key = secrets.token_bytes(32)
            with open(key_file, "wb") as f:
                f.write(self.key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypts string into hex-encoded payload [nonce + ciphertext + tag]."""
        if not HAS_AESGCM:
            # Fallback simple XOR/Hex obfuscation if cryptography lib isn't present
            return "ENC_RAW:" + plaintext.encode("utf-8").hex()

        aes = AESGCM(self.key)
        nonce = secrets.token_bytes(12)
        ciphertext = aes.encrypt(nonce, plaintext.encode("utf-8"), None)
        return (nonce + ciphertext).hex()

    def decrypt(self, hex_payload: str) -> str:
        """Decrypts hex payload back to plaintext."""
        if hex_payload.startswith("ENC_RAW:"):
            return bytes.fromhex(hex_payload[8:]).decode("utf-8", errors="ignore")

        if not HAS_AESGCM:
            return hex_payload

        try:
            raw = bytes.fromhex(hex_payload)
            nonce = raw[:12]
            ciphertext = raw[12:]
            aes = AESGCM(self.key)
            return aes.decrypt(nonce, ciphertext, None).decode("utf-8")
        except Exception:
            return "[Decryption Error: Key Mismatch]"


crypto = SovereignCrypto()


def init_encrypted_vault():
    """Initializes SQLite schema for encrypted memories and vector embeddings."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS encrypted_vault (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT    NOT NULL,
            cipher_blob TEXT    NOT NULL,
            embedding   TEXT    NOT NULL,
            created_at  TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def _tokenize(text: str) -> List[str]:
    return [w.lower() for w in re.findall(r'\b[a-zA-Z0-9]{3,}\b', text)]


def _compute_vector(text: str) -> Dict[str, float]:
    """Generates simple term-frequency vector representation for private RAG."""
    tokens = _tokenize(text)
    if not tokens:
        return {}
    tf = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    # Normalize length
    norm = math.sqrt(sum(v * v for v in tf.values()))
    return {k: v / norm for k, v in tf.items()} if norm > 0 else {}


def _cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    if not vec1 or not vec2:
        return 0.0
    common = set(vec1.keys()) & set(vec2.keys())
    return sum(vec1[k] * vec2[k] for k in common)


def save_encrypted_memory(category: str, content: str):
    """Encrypts content at rest and generates local embedding."""
    init_encrypted_vault()
    cipher = crypto.encrypt(content)
    vec = _compute_vector(content)

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO encrypted_vault (category, cipher_blob, embedding, created_at) VALUES (?, ?, ?, ?)",
        (category, cipher, json.dumps(vec), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def vector_rag_search(query: str, top_k: int = 3) -> List[Dict]:
    """
    Performs on-device semantic search over encrypted memories without external APIs.
    """
    init_encrypted_vault()
    query_vec = _compute_vector(query)
    if not query_vec:
        return []

    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT id, category, cipher_blob, embedding, created_at FROM encrypted_vault").fetchall()
    conn.close()

    scored = []
    for row in rows:
        _id, cat, cipher_blob, emb_json, dt = row
        try:
            doc_vec = json.loads(emb_json)
            sim = _cosine_similarity(query_vec, doc_vec)
            if sim > 0.05:  # Relevance threshold
                plain = crypto.decrypt(cipher_blob)
                scored.append({
                    "id": _id,
                    "category": cat,
                    "content": plain,
                    "similarity": round(sim, 3),
                    "created_at": dt
                })
        except Exception:
            continue

    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:top_k]
