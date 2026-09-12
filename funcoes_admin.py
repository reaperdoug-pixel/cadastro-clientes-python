"""Regras de autenticação e administração de usuários."""

import base64
import getpass
import hashlib
import hmac
import os
from datetime import datetime

from persistencia import (
    atualizar_usuario_banco,
    buscar_usuario_por_login,
    carregar_usuarios_ativos,
    criar_usuario_banco,
    inativar_usuario_banco,
)
import sessao

PERFIS = ("ADMIN", "ESTOQUISTA", "CONSULTA")


def _agora() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def gerar_hash_senha(senha: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, 310_000)
    return "pbkdf2_sha256$310000$%s$%s" % (
        base64.b64encode(salt).decode("ascii"), base64.b64encode(digest).decode("ascii"),
    )


def validar_senha(senha: str, senha_hash: str) -> bool:
    try:
        algoritmo, iteracoes, salt, digest = senha_hash.split("$")
        if algoritmo != "pbkdf2_sha256":
            return False
        calculado = hashlib.pbkdf2_hmac(
            "sha256", senha.encode("utf-8"), base64.b64decode(salt), int(iteracoes)
        )
        return hmac.compare_digest(calculado, base64.b64decode(digest))
    except (ValueError, TypeError):
        return False


def _ler_senha(confirmar: bool = True) -> str | None:
    senha = getpass.getpass("Senha: ")
    if len(senha) < 8:
        print("Senha inválida: use ao menos 8 caracteres.")
        return None
    if confirmar and senha != getpass.getpass("Confirme a senha: "):
        print("As senhas não conferem.")
        return None
    return senha


def criar_administrador_inicial() -> bool:
    if carregar_usuarios_ativos():
        return False
    print("\n=== Primeiro acesso: crie o administrador do sistema ===")
    login = input("Login do administrador: ").strip().lower()
    senha = _ler_senha()
    if not login or senha is None:
        print("Administrador inicial não criado.")
        return False
    try:
        usuario_id = criar_usuario_banco(login, gerar_hash_senha(senha), "ADMIN", _agora())
        sessao.iniciar(usuario_id, login, "ADMIN")
        print("Administrador criado e autenticado.")
        return True
    except Exception as err:
        print(f"Não foi possível criar o administrador: {err}")
        return False


def login() -> bool:
    login_informado = input("Login: ").strip().lower()
    senha = getpass.getpass("Senha: ")
    usuario = buscar_usuario_por_login(login_informado)
    if not usuario or not validar_senha(senha, usuario[2]):
        print("Login ou senha inválidos.")
        return False
    sessao.iniciar(usuario[0], usuario[1], usuario[5])
    print(f"Sessão iniciada para {usuario[1]} ({usuario[5]}).")
    return True


def cadastrar_usuario() -> None:
    login_novo = input("Login: ").strip().lower()
    if not login_novo:
        print("Login é obrigatório.")
        return
    perfil = input("Perfil (ADMIN/ESTOQUISTA/CONSULTA): ").strip().upper()
    senha = _ler_senha()
    if perfil not in PERFIS or senha is None:
        print("Perfil ou senha inválidos.")
        return
    try:
        criar_usuario_banco(login_novo, gerar_hash_senha(senha), perfil, _agora())
        print("Usuário cadastrado.")
    except Exception as err:
        print(f"Não foi possível cadastrar: {err}")


def listar_usuarios() -> None:
    usuarios = carregar_usuarios_ativos()
    print("\nID   | Login                | Perfil       | Criado em")
    print("-" * 65)
    for usuario_id, login_nome, criado, perfil in usuarios:
        print(f"{usuario_id:<4} | {login_nome:<20} | {perfil:<12} | {criado}")


def editar_usuario() -> None:
    listar_usuarios()
    try:
        usuario_id = int(input("ID do usuário: ").strip())
    except ValueError:
        print("ID inválido.")
        return
    perfil = input("Novo perfil (ADMIN/ESTOQUISTA/CONSULTA): ").strip().upper()
    if perfil not in PERFIS:
        print("Perfil inválido.")
        return
    alterar_senha = input("Alterar senha? (S/N): ").strip().upper() == "S"
    senha_hash = None
    if alterar_senha:
        senha = _ler_senha()
        if senha is None:
            return
        senha_hash = gerar_hash_senha(senha)
    print("Usuário atualizado." if atualizar_usuario_banco(usuario_id, perfil, senha_hash) else "Usuário não encontrado.")


def inativar_usuario() -> None:
    listar_usuarios()
    try:
        usuario_id = int(input("ID do usuário para inativar: ").strip())
    except ValueError:
        print("ID inválido.")
        return
    if sessao.usuario_atual and usuario_id == sessao.usuario_atual["id"]:
        print("Não é permitido inativar o usuário da sessão atual.")
        return
    print("Usuário inativado." if inativar_usuario_banco(usuario_id, _agora()) else "Usuário não encontrado.")
