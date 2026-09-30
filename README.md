Readme · MD
# ✦ Nexus - AI Powered Company Assistant
 
> **Ask your company's knowledge. Get intelligent, context-aware answers.**
 
Nexus is a full-stack, AI-powered knowledge assistant that lets employees interact with internal company documents in natural language. Rather than searching through policies, guides, and internal documentation manually, employees can ask questions such as: *“What is the annual leave policy?”*
 
Nexus retrieves relevant information from the organization’s knowledge base and uses an LLM to produce a grounded, context-aware answer with supporting sources.
 
## 1. Why Nexus?
 
Modern organizations accumulate extensive internal information, including:
 
-  HR policies
-  Security guidelines
-  IT documentation
-  Company procedures
-  Travel policies
-  Expense policies
-  Employee guidelines
Traditional document search requires employees to know where information lives and which keywords to use. Nexus changes that interaction model:
 
```text
Employee → Ask a question → Retrieve relevant knowledge → Generate a contextual answer → Show supporting sources
```
 
## 2. Core Features
 
### (a) AI Knowledge Assistant
 
Employees can interact with company knowledge using natural language.
 
```text
User:    What is the annual leave policy?
Nexus:   Employees are entitled to ...
Sources: 01_Annual_Leave_Policy.pdf
```
 
Responses are grounded in the organization’s internal knowledge base instead of relying solely on the model’s general knowledge.
 
### (b) Retrieval-Augmented Generation (RAG)
 
Nexus uses a Retrieval-Augmented Generation architecture:
 
```text
User question → Query processing → Document retrieval → Relevant chunks → Reranking → Context construction → LLM
→ Grounded answer → Source citations
```
 
The pipeline is built on **LangChain**, which powers document loading, text splitting, embeddings, and vector store integration. This produces answers based on the organization’s own documents.
 
### (c) Hybrid Knowledge Retrieval
 
The modular retrieval pipeline supports:
 
- Document loading and text extraction (LangChain document loaders for PDF, DOCX, TXT, and Markdown)
- Text chunking (LangChain `RecursiveCharacterTextSplitter`) and embedding generation
- Vector search (LangChain Chroma vector store) and hybrid retrieval
- Reranking and context construction
- Citation generation
### (d) LLM Integration
 
Nexus supports multiple LLM providers through a centralized LLM management layer. Current integrations include:
 
- Google Gemini
- Groq
The provider layer is separated from the application, making model integrations easy to switch or extend.
 
### (e) Authentication and Authorization
 
Nexus uses JWT authentication, role-based authorization, and Google Sign-In.
 
| Role | Capabilities |
| --- | --- |
| Employee | Create an account, sign in, use the AI assistant, access company knowledge, and view conversation history. |
| Administrator | Access the admin dashboard, upload company documents, manage the knowledge base, and monitor the document ecosystem. |
 
### (f) Persistent Storage with Neon PostgreSQL

Nexus stores its application data in **Neon** (serverless PostgreSQL) when `DATABASE_URL` is set:

- User accounts (email/password and Google Sign-In)
- Conversations and chat history
- The original uploaded company documents (stored as binary, `BYTEA`)

Data survives redeploys and restarts on hosts with temporary disks, such as Render's free tier. If `DATABASE_URL` is not set, Nexus falls back to a local SQLite file, so local development needs no extra setup.

## 3. System Architecture
 
```text
React + Vite UI
       │ HTTP / REST
       ▼
FastAPI Backend API
       │
       ├── Authentication layer ────── Neon PostgreSQL
       ├── Chat / query layer ──────┐   (users, chats, documents)
       └── Documents layer ─────────┼── PDF / text processing
                                    ▼
                               RAG engine 
                               (LangChain)
                                    │
                          Retrieval pipeline
   (chunking, embeddings, hybrid search, reranking, and context building)
                                    │
                                ChromaDB
                                    │
                              LLM manager
                             (Gemini / Groq)
                                    │
                             Grounded answer
```

> **Note:** Neon PostgreSQL stores application data (users, conversations, messages, and the original uploaded files). ChromaDB stores the vector index. On startup, Nexus rebuilds the index from the files stored in Neon if it is empty (see 4(c)).
 
## 4. RAG Pipeline
 
### (a) Document ingestion
 
```text
Company document → Document loader → Text extraction → Text chunking → Embedding generation → Vector storage → ChromaDB
```
 
### (b) Question answering
 
```text
User query → Query processing → Semantic / hybrid retrieval → Candidate documents → Reranking → Top relevant context
→ Prompt construction → LLM → Final answer
```
 
During retrieval, the LangChain Chroma vector store handles similarity search with relevance scores, which is combined with BM25 keyword search for hybrid retrieval.
 
This separation keeps knowledge retrieval distinct from language generation.

### (c) Persistence and restore on startup

When an admin uploads a document, the original file is saved to Neon PostgreSQL in addition to being chunked and embedded into ChromaDB.

```text
Upload → Save original file to Neon → Chunk → Embed → ChromaDB
```

On backend startup, a background task compares the files stored in Neon with the ChromaDB index. Any document missing from the index is re-downloaded from Neon and re-ingested automatically. This keeps the knowledge base intact even when the server's local disk is wiped (for example, after a redeploy on Render's free tier).
 
 
## 5. Technology Stack
 
| Area | Technology | Purpose |
| --- | --- | --- |
| Frontend | React | User interface |
| Frontend | Vite | Frontend build tooling |
| Frontend | React Router | Application routing |
| Frontend | Axios | API communication |
| Frontend | Lucide React | UI icons |
| Backend | Python | Backend language |
| Backend | FastAPI | REST API framework |
| Backend | Pydantic | Data validation and configuration |
| Backend | JWT | Authentication |
| Backend | Google Identity Services | Google authentication |
| AI / RAG | LangChain | RAG orchestration framework |
| AI / RAG | LangChain Community | Document loaders and embedding integrations |
| AI / RAG | LangChain Text Splitters | Document chunking |
| AI / RAG | LangChain Chroma | ChromaDB vector store integration |
| AI / RAG | Gemini | LLM |
| AI / RAG | Groq | LLM inference |
| AI / RAG | Sentence Transformers | Embeddings |
| AI / RAG | FastEmbed | Embedding generation through LangChain |
| AI / RAG | ChromaDB | Vector database |
| Database | SQLite | Application data (local development fallback) |
| Database | Neon (PostgreSQL) | Persistent application data: users, chat history, uploaded files |
| Database | psycopg2 | PostgreSQL driver |
| Database | ChromaDB | Vector storage |
 
 
## 6. Security
 
Nexus includes the following security mechanisms:
 
- JWT-based authentication
- Role-based authorization
- Protected API endpoints
- Admin-only document management
- Environment-based secret configuration
- Google OAuth / Identity Services
- API key protection through environment variables
- `.gitignore` protection for local secrets and runtime databases
- Neon connection string (`DATABASE_URL`) kept in environment variables, never committed; SSL enforced via `sslmode=require`
### Environment variables
 
Store sensitive configuration in `backend/.env`:
 
```dotenv
BACKEND_PORT = 4000
JWT_SECRET_KEY = your-secret-key
JWT_ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 60
 
GOOGLE_CLIENT_ID=your-google-client-id
 
ADMIN_EMAIL=your-admin-email
ADMIN_PASSWORD=your-admin-password
 
GEMINI_API_KEY=your-gemini-key
GROQ_API_KEY=your-groq-key
 
GEMINI_MODEL=gemini-3.5-flash-lite 
GROQ_MODEL=openai/gpt-oss-20b
 
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
 
CHROMA_PERSIST_DIRECTORY=./data/chroma
CHROMA_COLLECTION_NAME=company_knowledge
 
CHUNK_SIZE=800
CHUNK_OVERLAP=120
 
TOP_K=8
FINAL_K=5
MIN_RELEVANCE_SCORE=0.30
 
DATABASE_URL=postgresql://user:password@your-neon-host/neondb?sslmode=require

# Local development fallback (used only when DATABASE_URL is not set)
SQLITE_DATABASE=./data/company_ai.db
 
VITE_FRONTEND_URL=your-frontend-url
```
 
Create `frontend/.env` as well:
 
```dotenv
VITE_API_URL=http://localhost:4000
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```
 
> Never commit `.env` files or API keys to GitHub.
 
## 7. Local Development
 
### (a) Clone the repository
 
```bash
git clone https://github.com/sai-hrushita-kolachina/Nexus.git
cd Nexus
```
 
### (b) Set up the backend
 
```bash
cd backend
python -m venv venv
```
 
Activate the virtual environment on Windows:
 
```powershell
venv\Scripts\activate
```
 
Install dependencies and start the API:
 
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 4000
```
 
The backend runs at `http://localhost:4000`.
 
### (c) Set up the frontend
 
In another terminal:
 
```bash
cd frontend
npm install
npm run dev
```
 
The frontend runs at `http://localhost:5173`.


## 8. Admin Workflow
 
```text
Admin login → Admin dashboard → Upload document → Document processing → Text extraction → Chunking
 → Embeddings → Vector database → Available for RAG
```
 
Once documents are indexed, employees can query them through the AI assistant. The original file is also stored in Neon, so it is restored automatically if the server restarts with an empty vector index.
 
## 9. Employee Workflow
 
```text
Employee login → Nexus chat → Ask question → Retrieve relevant knowledge → Generate answer → Display sources
```
 
## 10. Example Queries
 
Once company documents are uploaded, employees can ask questions such as:
 
- What is the annual leave policy?
- What is the work-from-home policy?
- How many sick leaves are available?
- What is the employee attendance policy?
- What is the company’s information security policy?
- How do I report an IT issue?
- What is the expense reimbursement procedure?
The assistant retrieves relevant company information and generates an answer grounded in the available knowledge base.
 
 
## 11. Future Improvements
 
-  Production-grade vector database
-  Persistent cloud storage (application data and uploaded files now persist in Neon; the vector index is still rebuilt from them on startup)
-  Move vector storage to pgvector on Neon
-  Advanced admin analytics
-  Support for additional document formats
-  Improved hybrid retrieval
-  Metadata-based filtering
-  RAG observability and monitoring
##  12. Deployment
 
Nexus can be deployed as two services:
 
```text
Vercel  → Frontend (React)
Render  → Backend (FastAPI)
Neon    → Database (PostgreSQL)
```

 
## 13. Application
 
- **Employee Chat:** A conversational interface for interacting with company knowledge.
- **Admin Dashboard:** A workspace for managing the organization’s knowledge base and uploading documents.
- **Document Management:** Uploaded documents are processed and indexed for retrieval.
## 14. Author
 
**Sai Hrushita Kolachina**
