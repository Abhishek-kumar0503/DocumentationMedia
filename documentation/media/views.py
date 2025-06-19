import os
import json
import psycopg2
from psycopg2.extras import execute_values
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
from .models import DocumentationFile
import uuid
import time

# Load environment variables
load_dotenv()

# Initialize clients
# CHANGE THIS LINE - Use the same model as in pgvector.ipynb
model = SentenceTransformer("all-mpnet-base-v2")  # Previously was all-MiniLM-L6-v2
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# PostgreSQL connection settings
PG_HOST = os.getenv("PG_HOST", "127.0.0.1")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_USER = os.getenv("PG_USER", "avi")
PG_PASSWORD = os.getenv("PG_PASSWORD", "root")
PG_DATABASE = os.getenv("PG_DATABASE", "documents")
# Update dimension to match the all-mpnet-base-v2 model
VECTOR_DIMENSION = 768  # Changed from 384 to match all-mpnet-base-v2 dimensions

# Directory to store shared chats
SHARED_CHATS_DIR = os.path.join(settings.BASE_DIR, 'media', 'shared_chats')

# Create directory if it doesn't exist
if not os.path.exists(SHARED_CHATS_DIR):
    os.makedirs(SHARED_CHATS_DIR)

# Helper function for PostgreSQL connection
def get_db_connection():
    """Create and return a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            dbname=PG_DATABASE
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        raise

# Setup pgvector and required tables
def setup_pgvector():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Create extension if it doesn't exist
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            conn.commit()
            
            # Check if the documents table exists
            cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name = 'documents'
            );
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                # Create documents table with the correct schema
                cursor.execute(f"""
                CREATE TABLE documents (
                    id SERIAL PRIMARY KEY,
                    namespace TEXT NOT NULL,
                    doc_type TEXT NOT NULL,
                    heading TEXT,
                    path TEXT,
                    url TEXT,
                    content TEXT NOT NULL,
                    chunk_id INTEGER,
                    total_chunks INTEGER,
                    level INTEGER,
                    embedding VECTOR({VECTOR_DIMENSION}) NOT NULL
                );
                """)
                conn.commit()
                
                # Create indices after table is created
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS documents_embedding_idx 
                ON documents 
                USING ivfflat (embedding vector_cosine_ops) 
                WITH (lists = 100);
                """)
                conn.commit()
                
                cursor.execute("CREATE INDEX IF NOT EXISTS documents_namespace_idx ON documents (namespace);")
                conn.commit()
                
                print("Database table created with proper schema")
            else:
                print("Using existing documents table")
                
    except Exception as e:
        conn.rollback()
        print(f"Error setting up database: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()

# Try to setup pgvector on module import
try:
    setup_pgvector()
    print("✅ pgvector setup complete")
except Exception as e:
    print(f"⚠️ pgvector setup failed: {e}")

# Function to query documents from pgvector
def query_similar_docs(question_embedding, namespace, top_k=5):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Use vector similarity search with cosine distance
            cursor.execute("""
                SELECT 
                    id, 
                    heading, 
                    path, 
                    url, 
                    content, 
                    chunk_id, 
                    total_chunks, 
                    level,
                    1 - (embedding <=> %s::vector) as similarity
                FROM 
                    documents
                WHERE 
                    namespace = %s
                ORDER BY 
                    embedding <=> %s::vector
                LIMIT %s
            """, (question_embedding, namespace, question_embedding, top_k))
            
            # Fetch results
            results = cursor.fetchall()
            
            # Format as a structure similar to Pinecone results
            matches = []
            for row in results:
                matches.append({
                    "id": str(row[0]),
                    "metadata": {
                        "heading": row[1],
                        "path": row[2],
                        "url": row[3],
                        "content": row[4],
                        "chunk_id": row[5],
                        "total_chunks": row[6],
                        "level": row[7],
                    },
                    "score": float(row[8])  # similarity score
                })
            
            return {"matches": matches}
            
    except Exception as e:
        print(f"Error querying PostgreSQL: {e}")
        return {"matches": []}
    finally:
        conn.close()

def index(request):
    return render(request, 'index.html')

def ai_chat(request, tool_name=None):
    # If tool_name is not provided in URL, check query parameter or use default
    if tool_name is None:
        tool_name = request.GET.get('tool_name', 'django')
    
    # Map simple tool name to a friendly display name (if needed)
    # You can remove this mapping if tool_name is already the display name
    tool_names = {
        'django': 'Django',
        'javascript': 'JavaScript',
        'python': 'Python',
        'react': 'React',
        'pytest': 'Pytest',
        'git': 'Git',
        'postman': 'Postman',
        'vscode': 'VS Code',
        'docker': 'Docker',
        'github': 'GitHub',
        'kubernetes': 'Kubernetes',
        'fastapi': 'Fast API',
        'java': 'Java',
        'c': 'C',
        'c++': 'C++',
        'flask': 'Flask',
        'vuejs': 'Vue.js',
        'tensorflow': 'TensorFlow',
        'kotlin': 'Kotlin',
        'postgresql': 'PostgreSQL',
        'mysql': 'MySQL',
        'linux': 'Linux',
        'gitlab': 'GitLab',
        'awscli': 'AWS CLI',
        'other': 'Other',
        # Add more mappings as needed
    }
    
    # Get display name or capitalize the tool name if not in mapping
    display_name = tool_names.get(tool_name.lower(), tool_name.capitalize())
    
    return render(request, 'ai.html', {
        'doc_type': tool_name,  # Keep this for backward compatibility
        'doc_type_name': display_name
    })

def copy_doc_text(request):
    name = request.GET.get('name', '').lower()
    print(f"🔍 DEBUG - copy_doc_text requested for: {name}")
    
    try:
        doc = DocumentationFile.objects.get(name__iexact=name)
        print(f"🔎 Found document: {doc.name}, type: {doc.doc_type}")
        
        # Create dummy content for when file doesn't exist
        dummy_content = f"# Documentation for {doc.name}\n\nThis is placeholder text for {doc.name} documentation."
        
        # Try to get the real content if available
        if doc.documentation_file:
            try:
                file_path = doc.documentation_file.path
                import os
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return JsonResponse({'text': f.read()})
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
        
        # Return dummy content if we couldn't get the real file
        return JsonResponse({'text': dummy_content})
    
    except DocumentationFile.DoesNotExist:
        print(f"❌ ERROR - Documentation not found for: {name}")
        return JsonResponse({'text': f"No documentation found for {name}"})

def copy_ai_summary(request):
    name = request.GET.get('name', '').lower()
    print(f"🔍 DEBUG - copy_ai_summary requested for: {name}")
    
    try:
        doc = DocumentationFile.objects.get(name__iexact=name)
        
        # Create dummy AI summary
        dummy_summary = f"# AI Summary for {doc.name}\n\nThis is a placeholder AI summary for {doc.name}."
        
        # Try to get the real content if available
        if doc.ai_documentation_file:
            try:
                file_path = doc.ai_documentation_file.path
                import os
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return JsonResponse({'summary': f.read()})
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
        
        # Return dummy content if we couldn't get the real file
        return JsonResponse({'summary': dummy_summary})
    
    except DocumentationFile.DoesNotExist:
        print(f"❌ ERROR - Documentation not found for: {name}")
        return JsonResponse({'summary': f"No AI summary found for {name}"})

def debug_db(request):
    from django.http import HttpResponse
    import os
    
    output = "<h1>Database Debug Info</h1>"
    
    # List all documents
    docs = DocumentationFile.objects.all()
    output += f"<p>Total documents: {len(docs)}</p>"
    output += "<table border='1'><tr><th>Name</th><th>Type</th><th>Doc File</th><th>AI File</th><th>File Exists</th></tr>"
    
    for doc in docs:
        doc_path = "None"
        ai_path = "None"
        file_exists = "No"
        
        if doc.documentation_file:
            try:
                doc_path = doc.documentation_file.path
                file_exists = "Yes" if os.path.exists(doc_path) else "No"
            except:
                doc_path = "Error getting path"
                
        if hasattr(doc, 'ai_documentation_file') and doc.ai_documentation_file:
            try:
                ai_path = doc.ai_documentation_file.path
            except:
                ai_path = "Error getting path"
        
        output += f"<tr><td>{doc.name}</td><td>{doc.doc_type}</td><td>{doc_path}</td>"
        output += f"<td>{ai_path}</td><td>{file_exists}</td></tr>"
    
    output += "</table>"
    
    # Add pgvector database info
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Check if the documents table exists
            cursor.execute("SELECT COUNT(*) FROM documents;")
            doc_count = cursor.fetchone()[0]
            output += f"<h2>pgvector Database</h2><p>Total vectors: {doc_count}</p>"
            
            # Get namespace stats
            cursor.execute("SELECT namespace, COUNT(*) FROM documents GROUP BY namespace;")
            namespaces = cursor.fetchall()
            
            if namespaces:
                output += "<table border='1'><tr><th>Namespace</th><th>Document Count</th></tr>"
                for ns in namespaces:
                    output += f"<tr><td>{ns[0]}</td><td>{ns[1]}</td></tr>"
                output += "</table>"
    except Exception as e:
        output += f"<p>Error querying pgvector: {str(e)}</p>"
    finally:
        conn.close()
        
    return HttpResponse(output)

def docs(request, doc_id):
    # Simple view that renders a placeholder
    return render(request, 'docs.html', {'doc_id': doc_id})

@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question')
            tool_name = data.get('tool_name')
            
            if not question or not tool_name:
                return JsonResponse({"error": "Missing question or tool_name"}, status=400)
            
            # Form the namespace name (similar to previous Pinecone index name)
            namespace = f"{tool_name}-docs"
            
            try:
                # Get embeddings for the question
                question_embedding = model.encode(question).tolist()
                
                # Query pgvector instead of Pinecone
                results = query_similar_docs(question_embedding, namespace, top_k=4)
                
                # If no results, return a message
                if not results or not results.get("matches"):
                    return JsonResponse({
                        "answer": f"I don't have enough information about {tool_name} to answer your question. We'll add more documentation soon."
                    })
                
                # Prepare context for Groq
                contexts = []
                for match in results["matches"]:
                    metadata = match["metadata"]
                    contexts.append(f"Section: {metadata.get('heading', '')}\n\nContent: {metadata.get('content', '')}")
                
                # Join contexts
                context = "\n\n" + "=" * 40 + "\n\n".join(contexts) + "\n\n" + "=" * 40 + "\n\n"
                
                # Get answer from Groq
                system_prompt = f"""You are an expert {tool_name.capitalize()} documentation assistant. Your task is to provide high-quality answers by:
                1. SUMMARIZING the relevant information from the provided documentation context
                2. EXTRACTING and HIGHLIGHTING any code examples that directly answer the question
                3. STRUCTURING your answer in a clear format with proper sections
                4. FOCUSING only on the parts of the context most relevant to the question
                
                FORMAT your response as follows:
                - Start with a direct, concise answer to the question
                - Include code examples in properly formatted markdown code blocks
                - Cite the specific documentation sections you used
                
                If the provided context doesn't contain sufficient information, acknowledge this limitation clearly."""
                
                user_prompt = f"Question: {question}\n\nDocumentation context:\n{context}"
                
                response = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model="llama3-8b-8192",
                    temperature=0.1,
                    max_tokens=1200
                )
                
                answer = response.choices[0].message.content
                
                return JsonResponse({
                    "answer": answer,
                    "sources": [match["metadata"].get("path", "") for match in results["matches"]]
                })
                
            except Exception as e:
                print(f"Error querying pgvector or calling Groq: {str(e)}")
                return JsonResponse({
                    "answer": f"I'm still learning about {tool_name}. The documentation will be available soon."
                })
                
        except Exception as e:
            print(f"Error processing request: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Only POST requests allowed"}, status=405)

# Function to store documents in PostgreSQL
@csrf_exempt
def store_documents(request):
    """API endpoint to store documents in PostgreSQL with vector embeddings"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            documents = data.get('documents', [])
            namespace = data.get('namespace')
            doc_type = data.get('doc_type')
            
            if not documents or not namespace or not doc_type:
                return JsonResponse({"error": "Missing documents, namespace, or doc_type"}, status=400)
            
            # Generate embeddings for documents
            contents = [f"{doc.get('heading', '')}\n\n{doc.get('content', '')}" for doc in documents]
            embeddings = model.encode(contents)
            
            # Store in database
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    records = []
                    for i, doc in enumerate(documents):
                        record = (
                            namespace,
                            doc_type,
                            doc.get("heading", ""),
                            doc.get("path", ""),
                            doc.get("url", ""),
                            doc.get("content", ""),
                            doc.get("chunk_id"),
                            doc.get("total_chunks"),
                            doc.get("level", 1),
                            embeddings[i].tolist()
                        )
                        records.append(record)
                    
                    execute_values(
                        cursor,
                        """
                        INSERT INTO documents 
                        (namespace, doc_type, heading, path, url, content, chunk_id, total_chunks, level, embedding)
                        VALUES %s
                        """,
                        records,
                        template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    )
                    conn.commit()
                    
                return JsonResponse({
                    "success": True,
                    "message": f"Successfully stored {len(documents)} documents in namespace '{namespace}'",
                    "count": len(documents)
                })
                
            except Exception as e:
                conn.rollback()
                print(f"Error storing documents in PostgreSQL: {e}")
                return JsonResponse({"error": str(e)}, status=500)
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error processing document storage request: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Only POST requests allowed"}, status=405)

@csrf_exempt
@require_http_methods(["POST"])
def create_shared_chat(request):
    """Create a shareable chat session"""
    try:
        data = json.loads(request.body)
        
        # Generate a unique ID
        chat_id = str(uuid.uuid4())[:8]
        
        # Create chat object
        chat_data = {
            'chat_id': chat_id,
            'tool_name': data.get('tool_name', 'generic'),
            'messages': data.get('messages', []),
            'created_at': data.get('created_at', time.strftime('%Y-%m-%dT%H:%M:%SZ'))
        }
        
        # Save to file
        file_path = os.path.join(SHARED_CHATS_DIR, f'{chat_id}.json')
        with open(file_path, 'w') as f:
            json.dump(chat_data, f)
        
        return JsonResponse({
            'success': True,
            'chat_id': chat_id
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_shared_chat(request, chat_id):
    """Retrieve a shared chat by ID"""
    try:
        file_path = os.path.join(SHARED_CHATS_DIR, f'{chat_id}.json')
        
        if not os.path.exists(file_path):
            return JsonResponse({
                'success': False,
                'error': 'Chat not found'
            }, status=404)
        
        with open(file_path, 'r') as f:
            chat_data = json.load(f)
        
        return JsonResponse(chat_data)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
