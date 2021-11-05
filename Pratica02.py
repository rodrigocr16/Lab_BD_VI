# Modules
import mariadb
import sys
import pandas as pd 
import apyori
import matplotlib
import matplotlib.pyplot as plt

# MariaDB Connection
try:
    conn = mariadb.connect(
        user="root",
        password="senha123",
        host="127.0.0.1",
        port=8082,
        database="PRATICA01"
    )
except mariadb.Error as e:
    print(f"Error connecting to platform: {e}")
    sys.exit(1)
cur = conn.cursor()


def importar():
    inv = pd.read_csv(r'E:\Fatec\6SEM\FABRICIO_Lab_VI\Praticas\basket.csv')
    for i,row in inv.iterrows():
        row["date_time"] = pd.Timestamp.to_pydatetime(pd.to_datetime(row["date_time"]))
        cur.execute("INSERT INTO INVENTARIO VALUES (?,?,?,?,?)", (row["Transaction"], row["Item"], row["date_time"], row["period_day"], row["weekday_weekend"]))
        print("Record inserted")
        cur.execute("COMMIT")


def listar_tipos_produtos(fonte):
    visited = []
    count = 0
    if fonte == 'inventario':
        cur.execute("SELECT * FROM INVENTARIO")
    elif fonte == 'compras':
        cur.execute("SELECT * FROM COMPRAS")
    produtos = [prod[1] for prod in cur.fetchall()]
    for p in range(0, len(produtos)):
        if produtos[p] not in visited:
            visited.append(produtos[p])
            count += 1
    return visited


def graf_total():
    cur.execute("SELECT * FROM INVENTARIO")
    produtos = [prod[1] for prod in cur.fetchall()]
    print(pd.DataFrame(produtos).value_counts().sort_values().plot(kind = 'bar', figsize=(30, 10)))
    plt.show()
    return


def graf_manha():
    cur.execute("SELECT * FROM INVENTARIO WHERE PERIOD_DAY = 'MORNING'")
    produtos = [prod[1] for prod in cur.fetchall()]
    print(pd.DataFrame(produtos).value_counts())
    print(pd.DataFrame(produtos).value_counts().sort_values().plot(kind = 'bar', figsize=(30, 10)))
    plt.show()
    return


def graf_tarde():
    cur.execute("SELECT * FROM INVENTARIO WHERE PERIOD_DAY = 'AFTERNOON'")
    produtos = [prod[1] for prod in cur.fetchall()]
    print(pd.DataFrame(produtos).value_counts())
    print(pd.DataFrame(produtos).value_counts().sort_values().plot(kind = 'bar', figsize=(30, 10)))
    plt.show()
    return


def graf_noite():
    cur.execute("SELECT * FROM INVENTARIO WHERE PERIOD_DAY = 'EVENING'")
    produtos = [prod[1] for prod in cur.fetchall()]
    print(pd.DataFrame(produtos).value_counts())
    print(pd.DataFrame(produtos).value_counts().sort_values().plot(kind = 'bar', figsize=(30, 5)))
    plt.show()
    return


def support(Ix, Iy, bd):
    sup = 0
    for transaction in bd:
        if (Ix.union(Iy)).issubset(transaction):
            sup+=1
    sup = sup/len(bd)
    return sup


def confidence(Ix, Iy, bd):
    Ix_count = 0
    Ixy_count = 0
    for transaction in bd:
        if Ix.issubset(transaction):
            Ix_count+=1
            if (Ix.union(Iy)).issubset(transaction):
                Ixy_count+=1
    conf = Ixy_count / Ix_count
    return conf


def prune(ass_rules, min_sup, min_conf):
    pruned_ass_rules = []
    for ar in ass_rules:
        if ar['support'] >= min_sup and ar['confidence'] >= min_conf:
            pruned_ass_rules.append(ar)
    return pruned_ass_rules


def apriori_2(itemset, bd, min_sup, min_conf):
    ass_rules = []
    fortes = []
    ass_rules.append([]) #level 1 (large itemsets)
    for item in itemset:
        sup = support({item}, {item}, bd)
        ass_rules[0].append({'rule': str(item), 'support':sup, 'confidence':1})
    ass_rules[0] = prune(ass_rules[0],min_sup,min_conf)
    ass_rules.append([]) #level 2 (2 items association)
    for item_1 in ass_rules[0]:
        for item_2 in ass_rules[0]:
            if item_1['rule'] != item_2['rule']:
                rule = item_1['rule'] + '_' + item_2['rule']
                Ix = {item_1['rule']}
                Iy = {item_2['rule']}
                sup = support(Ix, Iy, bd)
                conf = confidence(Ix, Iy, bd)
                ass_rules[1].append({'rule': rule, 'support':sup, 'confidence':conf})
                fortes.append({'rule': rule, 'support':sup, 'confidence':conf})
    ass_rules[1] = prune(ass_rules[1], min_sup, min_conf)
    return fortes


def apriori_organize(fonte):
    if fonte == "inventario":
        cur.execute("SELECT TRANSACTION, ITEM FROM INVENTARIO")
    elif fonte == "compras":
        cur.execute("SELECT ID, PRODUTO FROM COMPRAS")
    produtos = [prod for prod in cur.fetchall()]
    i = 1
    ap = []
    apri = []
    for p in produtos:
        if (p[0] == i):
            ap.append(p[1])
        else:
            apri.append(set(ap))
            ap.clear()
            ap.append(p[1])
            i += 1
    apri.append(set(ap))
    return apri


# SEG_EX01

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


def efetuar_compra(carrinho):
    cur.execute("SELECT MAX(ID) FROM COMPRAS")
    indice = cur.fetchone()[0]
    if indice is None:
        indice = 1
    else:
        indice += 1
    for produto in carrinho:
        cur.execute("INSERT INTO COMPRAS(ID, PRODUTO) VALUES(?, ?)", (indice, produto))
    cur.execute("COMMIT")
    return


def apriori(fonte):
    itemset = listar_tipos_produtos(fonte)
    transactions_bd = apriori_organize(fonte)
    fortes = apriori_2(itemset, transactions_bd, 0.05, 0.05)
    return pd.DataFrame(fortes).sort_values(ascending = False, by=['support','confidence']).head(2)


def menu_regras():
    nova_regra = []
    i = 0
    while i != '0':
        print("\n1. Acrescentar regra manualmente\n2. Listar regras\n3. Remover regra"
              "\n4. Acrescentar regra via APRIORI\n0. Retornar")
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
        elif i == '4':
            for rule in apriori().rule:
                pro = []
                pro.append(rule[0:rule.find('_')])
                rec = rule[rule.find('_') + 1:]
                print(pro, ' -> ', rec)
                inserir_regra(pro, rec)


def menu():
    i = 0
    carrinho = []
    while i != '0':
        if carrinho:
            print("\nSeu carrinho: ", carrinho)

        # MENU
        print("\nEscolha uma opção:\n1. Adicionar produto ao carrinho\n2. Confirmar seleção\n3. Gerenciar regras"
              "\n4. Ex 2.a) Tipos de Produtos\n5. Ex 2.b) Gráfico Total de Vendas\n6. Ex 2.c) Gráfico Vendas Manhã"
              "\n7. Ex 2.d) Gráfico Vendas Tarde \n8. Ex 2.e) Gráfico Vendas Noite\n9. Ex 2.f) Regras Fortes"
              "\n0. Sair\n")
        i = input("Sua escolha: ")
        if i == '0':
            return
        elif i == '1':
            while i:
                i = input("> ")
                if i:
                    carrinho.append(i)
        elif i == '2':
            efetuar_compra(carrinho)
            recomendacoes = verificar_regras(carrinho)
            if recomendacoes:
                print("Itens recomendados: ", recomendacoes)
            else:
                print("Não há recomendações")
            carrinho.clear()
        elif i == '3':
            menu_regras()
        elif i == '4':
            for produto in listar_tipos_produtos("inventario"):
                print(">", produto)
            print(len(listar_tipos_produtos("inventario")), "registros encontrados.")
            input()
        elif i == '5':
            graf_total()
        elif i == '6':
            graf_manha()
        elif i == '7':
            graf_tarde()
        elif i == '8':
            graf_noite()
        elif i == '9':
            fonte = input("De qual tabela?\n> ")
            print(apriori(fonte))
            input()


if __name__ == '__main__':
    menu()
