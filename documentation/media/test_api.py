import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

print("Testing API components...")

try:
    from dotenv import load_dotenv
    print("✓ dotenv imported successfully")
except ImportError:
    print("✗ Failed to import dotenv")

try:
    from sentence_transformers import SentenceTransformer
    print("✓ SentenceTransformer imported successfully")
except ImportError:
    print("✗ Failed to import SentenceTransformer")

try:
    from pinecone import Pinecone
    print("✓ Pinecone imported successfully")
except ImportError:
    print("✗ Failed to import Pinecone")

try:
    from groq import Groq
    print("✓ Groq imported successfully")
except ImportError:
    print("✗ Failed to import Groq")

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# Check environment variables
pinecone_key = os.getenv("PINECONE_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")

print(f"PINECONE_API_KEY: {'✓ Set' if pinecone_key else '✗ Not set'}")
print(f"GROQ_API_KEY: {'✓ Set' if groq_key else '✗ Not set'}")

# Test connections
if pinecone_key:
    try:
        pc = Pinecone(api_key=pinecone_key)
        indexes = pc.list_indexes()
        print(f"✓ Pinecone connection successful. Found {len(indexes)} indexes")
        for idx in indexes:
            print(f"  - {idx.name}")
    except Exception as e:
        print(f"✗ Pinecone connection failed: {e}")

if groq_key:
    try:
        groq_client = Groq(api_key=groq_key)
        # Just test a simple API call to check connection
        print("✓ Groq client initialized successfully")
    except Exception as e:
        print(f"✗ Groq client initialization failed: {e}")

print("\nTest completed.")