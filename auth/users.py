import hashlib
from auth.db import get_connection


# =========================
# UTIL
# =========================
def hash_password(password: str) -> str:
    """
    Gera hash SHA256 da senha
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# =========================
# EMPRESAS
# =========================
def create_company(name: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO companies (name) VALUES (?)",
        (name,)
    )

    conn.commit()
    company_id = cursor.lastrowid
    conn.close()

    return company_id


# =========================
# USUÁRIOS
# =========================
def create_user(
    company_id: int,
    name: str,
    email: str,
    password: str,
    is_admin: bool = False
):
    conn = get_connection()
    cursor = conn.cursor()

    password_hash = hash_password(password)

    cursor.execute("""
        INSERT INTO users (company_id, name, email, password_hash, is_admin)
        VALUES (?, ?, ?, ?, ?)
    """, (
        company_id,
        name,
        email,
        password_hash,
        int(is_admin)
    ))

    conn.commit()
    conn.close()


def authenticate_user(email: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()

    password_hash = hash_password(password)

    cursor.execute("""
        SELECT users.*, companies.name AS company_name
        FROM users
        JOIN companies ON users.company_id = companies.id
        WHERE email = ? AND password_hash = ?
    """, (email, password_hash))

    user = cursor.fetchone()
    conn.close()

    return dict(user) if user else None