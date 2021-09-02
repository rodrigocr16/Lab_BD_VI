# Modules
import mariadb
import sys


# MariaDB Connection
try:
    conn = mariadb.connect(
        user="username",
        password="password",
        host="endereço_IP",
        port=8082,
        database="PRATICA01"
    )
except mariadb.Error as e:
    print(f"Error connecting to platform: {e}")
    sys.exit(1)
cur = conn.cursor()


def pegar_recomendacao(recomendacoes, carrinho, regra_id):
    cur.execute("SELECT PRODUTO FROM RECOMENDACAO WHERE ID = ?", (regra_id,))
    recomendacao = cur.fetchone()[0]
    if recomendacao not in carrinho and recomendacao not in recomendacoes:
        return recomendacao


def listar_regras():
    cur.execute("SELECT * FROM RECOMENDACAO")
    recomendacoes = (cur.fetchall())
    print("\nRegras:")
    for id, recomendacao in recomendacoes:
        print(id, recomendacao)
        cur.execute("SELECT PRODUTO FROM REGRAS WHERE ID = ?", (id,))
        print(">", cur.fetchall(), "\n")


def excluir_regra(id):
    cur.execute("DELETE FROM RECOMENDACAO WHERE ID = ?", (id,))
    cur.execute("DELETE FROM REGRAS WHERE ID = ?", (id,))
    cur.execute("COMMIT")


def inserir_regra(nova_regra, nova_recomendacao):
    cur.execute("SELECT MAX(ID) FROM REGRAS")
    indice = cur.fetchone()[0] + 1
    for produto in nova_regra:
        cur.execute("INSERT INTO REGRAS(ID, PRODUTO) VALUES(?, ?)", (indice, produto))
    cur.execute("INSERT INTO RECOMENDACAO(ID, PRODUTO) VALUES(?, ?)", (indice, nova_recomendacao))
    cur.execute("COMMIT")


def verificar_regras(carrinho):
    cur.execute("SELECT DISTINCT ID FROM REGRAS")
    regras = [reg[0] for reg in cur.fetchall()]
    recomendacoes = []
    for regra in regras:
        cur.execute("SELECT PRODUTO FROM REGRAS where ID = ?", (regra,))
        produtos = [reg[0] for reg in cur.fetchall()]
        if set(produtos).issubset(set(carrinho)):
            recomendacao = pegar_recomendacao(recomendacoes, carrinho, regra)
            if recomendacao is not None:
                recomendacoes.append(recomendacao)
    return recomendacoes


def menu_regras():
    nova_regra = []
    i = 0
    while i != '0':
        print("\n1. Acrescentar regra\n2. Listar regras\n3. Remover regra\n0. Retornar")
        i = input("Sua escolha: ")
        if i == '0':
            return
        elif i == '1':
            print("Digite os produtos que compõem a regra (insira '0' para encerrar)")
            while i != '0':
                i = (input("> "))
                if i != '0':
                    nova_regra.append(i)
            print("Qual a recomendação para ", nova_regra, "?")
            nova_recomendacao = input("> ")
            inserir_regra(nova_regra, nova_recomendacao)
        elif i == '2':
            listar_regras()
        elif i == '3':
            listar_regras()
            i = input("\nQual o número da regra que quer deletar?\n> ")
            excluir_regra(i)


def menu():
    i = 0
    carrinho = []
    while i != '0':
        if carrinho:
            print("\nSeu carrinho: ", carrinho)

        # MENU
        print("\nEscolha uma opção:\n1. Adicionar produto ao carrinho\n2. Confirmar seleção\n3. Gerenciar regras\n0. Sair")
        i = input("Sua escolha: ")
        if i == '0':
            return
        elif i == '1':
            carrinho.append(input("> "))
        elif i == '2':
            recomendacoes = verificar_regras(carrinho)
            if recomendacoes:
                print("Itens recomendados: ", recomendacoes)
            else:
                print("Não há recomendações")
            return
        elif i == '3':
            menu_regras()


if __name__ == '__main__':
    menu()