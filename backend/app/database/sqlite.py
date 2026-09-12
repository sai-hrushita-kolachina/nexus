import sqlite3

from pathlib import Path

from datetime import datetime, timezone

from app.config import get_settings

# DATABASE PATH

def get_database_path() -> Path:

    settings = get_settings()

    path = Path(
        settings.sqlite_database
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    return path

# DATABASE CONNECTION

def get_connection():

    connection = sqlite3.connect(
        get_database_path()
    )

    connection.row_factory = sqlite3.Row

    return connection

# INITIALIZE DATABASE

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    # USERS TABLE

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

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

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (

            id TEXT PRIMARY KEY,

            title TEXT,

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL

        )
        """
    )

    # MESSAGES TABLE

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            conversation_id TEXT NOT NULL,

            role TEXT NOT NULL,

            content TEXT NOT NULL,

            query_type TEXT,

            provider TEXT,

            created_at TEXT NOT NULL,

            FOREIGN KEY (conversation_id)
            REFERENCES conversations(id)

        )
        """
    )

    # INDEXES

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_messages_conversation

        ON messages(conversation_id)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_users_email

        ON users(email)
        """
    )

    connection.commit()

    connection.close()

# CREATE CONVERSATION

def create_conversation(
    conversation_id: str,
    title: str = "New conversation"
):

    now = datetime.now(
        timezone.utc
    ).isoformat()

    connection = get_connection()

    connection.execute(
        """
        INSERT OR IGNORE INTO conversations
        (
            id,
            title,
            created_at,
            updated_at
        )

        VALUES (?, ?, ?, ?)
        """,
        (
            conversation_id,
            title,
            now,
            now
        )
    )

    connection.commit()

    connection.close()

# UPDATE CONVERSATION

def update_conversation(
    conversation_id: str
):

    now = datetime.now(
        timezone.utc
    ).isoformat()

    connection = get_connection()

    connection.execute(
        """
        UPDATE conversations

        SET updated_at = ?

        WHERE id = ?
        """,
        (
            now,
            conversation_id
        )
    )

    connection.commit()

    connection.close()

# SAVE MESSAGE

def save_message(
    conversation_id: str,
    role: str,
    content: str,
    query_type: str | None = None,
    provider: str | None = None
):

    now = datetime.now(
        timezone.utc
    ).isoformat()

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO messages
        (
            conversation_id,
            role,
            content,
            query_type,
            provider,
            created_at
        )

        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            conversation_id,
            role,
            content,
            query_type,
            provider,
            now
        )
    )

    connection.commit()

    connection.close()

    update_conversation(
        conversation_id
    )

# GET ALL CONVERSATIONS

def get_conversations():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            id,
            title,
            created_at,
            updated_at

        FROM conversations

        ORDER BY updated_at DESC
        """
    ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]

# GET ALL MESSAGES

def get_messages(
    conversation_id: str
):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            id,
            conversation_id,
            role,
            content,
            query_type,
            provider,
            created_at

        FROM messages

        WHERE conversation_id = ?

        ORDER BY id ASC
        """,
        (
            conversation_id,
        )
    ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]

# GET RECENT MESSAGES

# THIS IS USED BY:

# ConversationRewriter

# to understand things like:

# User:
# What is the leave policy?

# AI:
# Employees get 24 days of annual leave.

# User:
# Can I carry it over?

# The rewriter receives the previous messages and can
# understand that "it" refers to annual leave.

def get_recent_messages(
    conversation_id: str,
    limit: int = 10
):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            role,
            content,
            created_at

        FROM messages

        WHERE conversation_id = ?

        ORDER BY id DESC

        LIMIT ?
        """,
        (
            conversation_id,
            limit
        )
    ).fetchall()

    connection.close()

    messages = [
        dict(row)
        for row in rows
    ]

    # SQL returns newest → oldest.

    # ConversationRewriter needs:

    # oldest → newest

    messages.reverse()

    return messages

# DELETE CONVERSATION

def delete_conversation(
    conversation_id: str
):

    connection = get_connection()

    # Delete messages first
    connection.execute(
        """
        DELETE FROM messages

        WHERE conversation_id = ?
        """,
        (
            conversation_id,
        )
    )

    # Delete conversation
    connection.execute(
        """
        DELETE FROM conversations

        WHERE id = ?
        """,
        (
            conversation_id,
        )
    )

    connection.commit()

    connection.close()

# USERS

def get_user_by_email(email: str):

    connection = get_connection()

    row = connection.execute(
        """
        SELECT
            id,
            name,
            email,
            password_hash,
            google_id,
            auth_provider,
            role,
            created_at

        FROM users

        WHERE email = ?

        LIMIT 1
        """,
        (
            email.lower(),
        )
    ).fetchone()

    connection.close()

    if not row:
        return None

    return dict(row)

def get_user_by_google_id(google_id: str):

    connection = get_connection()

    row = connection.execute(
        """
        SELECT
            id,
            name,
            email,
            password_hash,
            google_id,
            auth_provider,
            role,
            created_at

        FROM users

        WHERE google_id = ?

        LIMIT 1
        """,
        (
            google_id,
        )
    ).fetchone()

    connection.close()

    if not row:
        return None

    return dict(row)

def create_user(
    name,
    email,
    password_hash=None,
    google_id=None,
    auth_provider="local",
    role="employee",
):
    """
    Create a new user in the users table.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO users (
                name,
                email,
                password_hash,
                google_id,
                auth_provider,
                role,
                created_at
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
                datetime.utcnow().isoformat(),
            ),
        )

        connection.commit()

        user_id = cursor.lastrowid

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                password_hash,
                google_id,
                auth_provider,
                role,
                created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        )

        row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "User was created but could not be retrieved."
            )

        return dict(row)

    finally:
        connection.close()