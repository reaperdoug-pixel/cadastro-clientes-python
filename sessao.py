"""Estado de sessão em memória para a execução atual do terminal."""

usuario_atual: dict | None = None


def iniciar(usuario_id: int, login: str, permissoes: str) -> None:
    global usuario_atual
    usuario_atual = {"id": usuario_id, "login": login, "permissoes": permissoes}


def encerrar() -> None:
    global usuario_atual
    usuario_atual = None


def possui_permissao(*perfis: str) -> bool:
    return usuario_atual is not None and usuario_atual["permissoes"] in perfis
