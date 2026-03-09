from auth.db import init_db
from auth.users import create_company, create_user

# Inicializa banco
init_db()

# =========================
# CONFIGURE AQUI
# =========================
COMPANY_NAME = "Empresa Demo"
ADMIN_NAME = "Administrador"
ADMIN_EMAIL = "admin@empresa.com"
ADMIN_PASSWORD = "123456"

# =========================
# EXECUÇÃO
# =========================
company_id = create_company(COMPANY_NAME)

create_user(
    company_id=company_id,
    name=ADMIN_NAME,
    email=ADMIN_EMAIL,
    password=ADMIN_PASSWORD,
    is_admin=True
)

print("✅ Usuário administrador criado com sucesso!")
print(f"Login: {ADMIN_EMAIL}")
print(f"Senha: {ADMIN_PASSWORD}")