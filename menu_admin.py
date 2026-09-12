"""Menu de autenticação e CRUD de usuários."""

from funcoes_admin import cadastrar_usuario, editar_usuario, inativar_usuario, listar_usuarios, login
import sessao


def sub_menu_admin() -> None:
    while True:
        print("\n" + "=" * 50)
        print("         DEGEHUB ERP | ADMINISTRAÇÃO")
        print("=" * 50)
        print("1. Login" if sessao.usuario_atual is None else "1. Trocar login")
        if sessao.possui_permissao("ADMIN"):
            print("2. Cadastrar usuário")
            print("3. Listar usuários")
            print("4. Editar usuário")
            print("5. Inativar usuário")
        print("0. Voltar ao menu principal")
        opcao = input("Opção: ").strip()
        if opcao == "1":
            login()
        elif sessao.possui_permissao("ADMIN") and opcao == "2":
            cadastrar_usuario()
        elif sessao.possui_permissao("ADMIN") and opcao == "3":
            listar_usuarios()
        elif sessao.possui_permissao("ADMIN") and opcao == "4":
            editar_usuario()
        elif sessao.possui_permissao("ADMIN") and opcao == "5":
            inativar_usuario()
        elif opcao == "0":
            return
        else:
            print("Opção inválida ou sem permissão.")
