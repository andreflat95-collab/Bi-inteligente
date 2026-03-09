import streamlit as st
from auth.users import authenticate_user


# =========================
# SESSION
# =========================
def init_session():
    if "user" not in st.session_state:
        st.session_state.user = None


def login_screen():
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = authenticate_user(email, password)

        if user:
            st.session_state.user = user
            st.success(f"Bem-vindo, {user['name']} 👋")
            st.rerun()
        else:
            st.error("Email ou senha inválidos")


def require_login():
    init_session()

    if st.session_state.user is None:
        login_screen()
        st.stop()


def logout_button():
    if st.button("Sair"):
        st.session_state.user = None
        st.rerun()