"""
Database layer.

Uses PostgreSQL when DATABASE_URL is set (persistent, works on free hosting
such as Neon or Supabase). Falls back to local SQLite for development.

The public function names are unchanged, so the rest of the app needs no edits.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from app.config import get_settings

def _use_postgres() -> bool:
    return bool(get_settings().database_url)

# DATABASE PATH (SQLite fallback)

def get_database_path() -> Path:
    settings = get_settings()
    path = Path(settings.sqlite_database)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

# CONNECTION WRAPPER
# Lets the rest of this file use one style of code for both databases.

class _Connection:
    def __init__(self, raw, is_postgres: bool):
        self.raw = raw
        self.is_postgres = is_postgres

    def execute(self, sql: str, params: tuple = ()):

        if self.is_postgres:
            from psycopg2.extras import RealDictCursor

            cursor = self.raw.cursor(cursor_factory=RealDictCursor)
            cursor.execute(sql.replace("?", "%s"), params)
            return cursor

        return self.raw.execute(sql, params)

    def commit(self):
        self.raw.commit()

    def close(self):
        self.raw.close()

def get_connection() -> _Connection:
    if _use_postgres():
        import psycopg2
        raw = psycopg2.connect(get_settings().database_url)
        return _Connection(raw, True)

    raw = sqlite3.connect(get_database_path())
    raw.row_factory = sqlite3.Row
    return _Connection(raw, False)

# INITIALIZE DATABASE
def initialize_database():
    connection = get_connection()
    auto_id = (
        "SERIAL PRIMARY KEY"
        if connection.is_postgres
        else "INTEGER PRIMARY KEY AUTOINCREMENT"
    )

    blob = "BYTEA" if connection.is_postgres else "BLOB"

    # USERS TABLE

    connection.execute(
        f"""
        CREATE TABLE IF NOT EXISTS users (
            id {auto_id},
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT,
            google_id TEXT UNIQUE,
            auth_provider TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'employee',
            created_at TEXT NOT NULL
        )
        """
    )

    # CONVERSATIONS TABLE

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            title TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    # MESSAGES TABLE

    connection.execute(
        f"""
        CREATE TABLE IF NOT EXISTS messages (
            id {auto_id},
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            query_type TEXT,
            provider TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
        """
    )

    # DOCUMENT FILES TABLE
    # Keeps the original uploaded files so the vector index can be
    # rebuilt after a restart (free hosts wipe local disk).

    connection.execute(
        f"""
        CREATE TABLE IF NOT EXISTS document_files (
            filename TEXT PRIMARY KEY,
            file_type TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            content {blob} NOT NULL,
            uploaded_at TEXT NOT NULL
        )
        """
    )

    # MIGRATION: databases created before per-user history existed
    # have no user_id column on conversations. Add it. Old conversations
    # keep user_id = NULL, so they are not shown to anyone.

    if connection.is_postgres:
        connection.execute(
            "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS user_id TEXT"
        )

    else:
        columns = [
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(conversations)"
            ).fetchall()
        ]

        if "user_id" not in columns:
            connection.execute(
                "ALTER TABLE conversations ADD COLUMN user_id TEXT"
            )

    # INDEXES
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id)"
    )

    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id)"
    )

    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"
    )

    connection.commit()

    connection.close()

# PER-USER HISTORY LIMIT
# Each user keeps only their most recent conversations.
MAX_CONVERSATIONS_PER_USER = 30

# CHECK CONVERSATION ACCESS
# True if the conversation does not exist yet (the user may create it)
# or already belongs to this user. False if it belongs to someone else
# (or is an old conversation with no owner).

def can_access_conversation(conversation_id: str,user_id: str) -> bool:

    connection = get_connection()

    row = connection.execute(
        "SELECT user_id FROM conversations WHERE id = ?",
        (conversation_id,)
    ).fetchone()

    connection.close()

    if row is None:
        return True
    return row["user_id"] == str(user_id)

# DELETE OLD CONVERSATIONS OF ONE USER

def prune_conversations(user_id: str,keep: int = MAX_CONVERSATIONS_PER_USER):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT id FROM conversations
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """,
        (str(user_id),)
    ).fetchall()

    for row in rows[keep:]:

        connection.execute(
            "DELETE FROM messages WHERE conversation_id = ?",
            (row["id"],)
        )

        connection.execute(
            "DELETE FROM conversations WHERE id = ?",
            (row["id"],)
        )

    connection.commit()

    connection.close()

# CREATE CONVERSATION
def create_conversation(conversation_id: str,user_id: str,title: str = "New conversation"):

    now = datetime.now(timezone.utc).isoformat()
    connection = get_connection()
    cursor = connection.execute(
        """
        INSERT INTO conversations
        (id, user_id, title, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT (id) DO NOTHING
        """,
        (conversation_id, str(user_id), title, now, now)
    )

    created = cursor.rowcount == 1
    connection.commit()
    connection.close()

    # A new conversation may push the user over the limit.

    if created:
        prune_conversations(user_id)

# UPDATE CONVERSATION

def update_conversation(conversation_id: str):
    now = datetime.now(timezone.utc).isoformat()
    connection = get_connection()
    connection.execute(
        "UPDATE conversations SET updated_at = ? WHERE id = ?",
        (now, conversation_id)
    )
    connection.commit()
    connection.close()

# SAVE MESSAGE

def save_message(conversation_id: str,role: str,content: str,query_type: str | None = None,provider: str | None = None):

    now = datetime.now(timezone.utc).isoformat()

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO messages
        (conversation_id, role, content, query_type, provider, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (conversation_id, role, content, query_type, provider, now)
    )

    connection.commit()
    connection.close()
    update_conversation(conversation_id)

# GET THIS USER'S CONVERSATIONS

def get_conversations(user_id: str):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT id, title, created_at, updated_at
        FROM conversations
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """,
        (str(user_id),)
    ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows[:MAX_CONVERSATIONS_PER_USER]
    ]

# GET ALL MESSAGES OF ONE OF THIS USER'S CONVERSATIONS
# Returns an empty list if the conversation is not theirs.

def get_messages(conversation_id: str,user_id: str):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT m.id, m.conversation_id, m.role, m.content,
               m.query_type, m.provider, m.created_at
        FROM messages m
        JOIN conversations c ON c.id = m.conversation_id
        WHERE m.conversation_id = ? AND c.user_id = ?
        ORDER BY m.id ASC
        """,
        (conversation_id, str(user_id))
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]

# GET RECENT MESSAGES
# Used by ConversationRewriter so follow-up questions such as
# "Can I carry it over?" can be resolved against earlier messages.

def get_recent_messages(conversation_id: str,limit: int = 10):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT role, content, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (conversation_id, limit)
    ).fetchall()

    connection.close()

    messages = [dict(row) for row in rows]

    # SQL returns newest -> oldest; the rewriter needs oldest -> newest.
    messages.reverse()

    return messages

# DELETE ONE OF THIS USER'S CONVERSATIONS
# Returns True if something was deleted.

def delete_conversation(conversation_id: str,user_id: str) -> bool:

    connection = get_connection()

    owned = connection.execute(
        "SELECT id FROM conversations WHERE id = ? AND user_id = ?",
        (conversation_id, str(user_id))
    ).fetchone()

    if owned is None:
        connection.close()
        return False

    connection.execute(
        "DELETE FROM messages WHERE conversation_id = ?",
        (conversation_id,)
    )

    connection.execute(
        "DELETE FROM conversations WHERE id = ?",
        (conversation_id,)
    )

    connection.commit()

    connection.close()

    return True

# USERS

_USER_COLUMNS = """
    id, name, email, password_hash, google_id,
    auth_provider, role, created_at
"""

def get_user_by_email(email: str):

    connection = get_connection()

    row = connection.execute(
        f"SELECT {_USER_COLUMNS} FROM users WHERE email = ? LIMIT 1",
        (email.lower(),)
    ).fetchone()

    connection.close()

    return dict(row) if row else None

def get_user_by_google_id(google_id: str):

    connection = get_connection()

    row = connection.execute(
        f"SELECT {_USER_COLUMNS} FROM users WHERE google_id = ? LIMIT 1",
        (google_id,)
    ).fetchone()

    connection.close()

    return dict(row) if row else None

def create_user(name,email,password_hash=None,google_id=None,auth_provider="local",role="employee"):
    """
    Create a new user in the users table.
    """

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO users (
                name, email, password_hash, google_id,
                auth_provider, role, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                email,
                password_hash,
                google_id,
                auth_provider,
                role,
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        connection.commit()

        row = connection.execute(
            f"SELECT {_USER_COLUMNS} FROM users WHERE email = ? LIMIT 1",
            (email,),
        ).fetchone()

        if row is None:
            raise RuntimeError(
                "User was created but could not be retrieved."
            )

        return dict(row)

    finally:
        connection.close()

# DOCUMENT FILES (persistent copy of every uploaded document)

def save_document_file(filename: str,file_type: str,content: bytes):

    connection = get_connection()

    if connection.is_postgres:
        import psycopg2
        payload = psycopg2.Binary(content)
    else:
        payload = content

    connection.execute(
        """
        INSERT INTO document_files
        (filename, file_type, size_bytes, content, uploaded_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT (filename) DO UPDATE SET
            file_type = excluded.file_type,
            size_bytes = excluded.size_bytes,
            content = excluded.content,
            uploaded_at = excluded.uploaded_at
        """,
        (
            filename,
            file_type,
            len(content),
            payload,
            datetime.now(timezone.utc).isoformat(),
        ),
    )

    connection.commit()

    connection.close()

def list_document_files():
    """Metadata only (no file bytes)."""

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT filename, file_type, size_bytes, uploaded_at
        FROM document_files
        ORDER BY filename ASC
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]

def get_document_file(filename: str) -> bytes | None:

    connection = get_connection()

    row = connection.execute(
        "SELECT content FROM document_files WHERE filename = ?",
        (filename,)
    ).fetchone()

    connection.close()

    if not row:
        return None

    return bytes(row["content"])
