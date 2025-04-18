import json  # Para trabalhar com arquivos JSON
from datetime import datetime, timedelta # A linha 'from datetime import datetime, timedelta' importa as classes datetime (para trabalhar com datas e horas) e timedelta (para representar intervalos de tempo) do módulo datetime.
import re  # Para expressões regulares
from collections import defaultdict, Counter # A linha 'from collections import defaultdict, Counter' importa as classes defaultdict (para criar dicionários com valores padrão) e Counter (para contar a ocorrência de elementos em um iterável) do módulo collections.

def carregar_dados(nome_arquivo):
    try:
        with open(nome_arquivo, "r") as arquivo:
            return json.load(arquivo)  
    except FileNotFoundError:
        return []  
    except json.JSONDecodeError:
        return []  

def salvar_dados(nome_arquivo, dados):
    with open(nome_arquivo, "w") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)  

estoque = carregar_dados("estoque.json")
cardapio = carregar_dados("cardapio.json")
mesas = carregar_dados("mesas.json")
pedidos = carregar_dados("pedidos.json")
vendas = carregar_dados("vendas.json")
fila_preparo = carregar_dados("fila_preparo.json")  

def menu_principal():
    while True:
        print("\n=== MENU PRINCIPAL ===")
        print("1. Gestão de Estoque")
        print("2. Gestão da Cozinha")
        print("3. Gestão de Mesas e Pedidos")
        print("4. Gestão de Pagamentos")
        print("5. Relatórios Financeiros")
        print("6. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            sistema_estoque()
        elif opcao == "2":
            sistema_cozinha()
        elif opcao == "3":
            sistema_mesas_pedidos()
        elif opcao == "4":
            sistema_pagamentos()
        elif opcao == "5":
            sistema_relatorios()
        elif opcao == "6":
            print("Saindo...")
            break
        else:
            print("Opção inválida.")

def sistema_estoque(): # Função para gerir o estoque (adicionar, atualizar, consultar)
    while True:
        print("\n=== GESTÃO DE ESTOQUE ===")
        print("1. Cadastrar Produto")
        print("2. Consultar Produtos")
        print("3. Atualizar Produto")
        print("4. Voltar ao Menu Principal")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_produto()
        elif opcao == "2":
            consultar_produtos()
        elif opcao == "3":
            atualizar_produto()
        elif opcao == "4":
            break
        else:
            print("Opção inválida.")

def cadastrar_produto(): 
    print("\n=== Cadastrar Produto ===")
    
    nome = input("Nome do Produto: ")
    quantidade = int(input("Quantidade: "))
    unidade = input("Unidade de Medida: ")
    preco = float(input("Preço Unitário: "))
    validade = input("Data de Validade (dd/mm/aaaa): ")
    limite_minimo = int(input("Estoque mínimo (para alertas): "))

    while True:
        codigo = input("Código do Produto (8 caracteres alfanuméricos): ").upper()
        if not re.match(r'^[A-Z0-9]{8}$', codigo):
            print("Código inválido. Deve conter exatamente 8 letras ou números.")
            continue
        if any(p["codigo"] == codigo for p in estoque):
            print("Já existe um produto com esse código.")
            continue
        break

    produto = {
        "nome": nome,
        "codigo": codigo,
        "quantidade": quantidade,
        "unidade": unidade,
        "preco": preco,
        "validade": validade,
        "limite_minimo": limite_minimo
    }

    estoque.append(produto)
    salvar_dados("estoque.json", estoque)
    print(" Produto cadastrado com sucesso!")

def consultar_produtos(): 
    print("\n=== Produtos no Estoque ===")
    if not estoque:
        print("Nenhum produto cadastrado.")
        return

    hoje = datetime.today()

    for produto in estoque:
        alerta = ""
        validade_str = produto.get('validade', '')
        try:
            validade = datetime.strptime(validade_str, "%d/%m/%Y")
            if validade < hoje:
                alerta += " PRODUTO VENCIDO!"
            elif validade <= hoje + timedelta(days=7):
                alerta += " VALIDADE PRÓXIMA!"
        except ValueError:
            alerta += " DATA INVÁLIDA!"

        if produto['quantidade'] <= produto.get('limite_minimo', 0):
            alerta += "ESTOQUE BAIXO!"

        print(f"Produto: {produto['nome']} | Código: {produto['codigo']} | "
            f"Quantidade: {produto['quantidade']} {produto['unidade']} | "
            f"Preço: R$ {produto['preco']:.2f} | Validade: {produto['validade']} {alerta}")

def atualizar_produto():  
    print("\n=== Atualizar Produto ===")
    codigo_atual = input("Digite o código do produto a ser atualizado: ").upper()

    for produto in estoque:
        if produto['codigo'] == codigo_atual:
            print(f"\nProduto: {produto['nome']} | Código: {produto['codigo']}")

            while True:
                novo_codigo = input(f"Novo código [{produto['codigo']}]: ").upper() or produto['codigo']
                if not re.match(r'^[A-Z0-9]{8}$', novo_codigo):
                    print("Código inválido. Deve conter exatamente 8 letras ou números.")
                    continue
                if novo_codigo != produto['codigo'] and any(p["codigo"] == novo_codigo for p in estoque):
                    print("Já existe um produto com esse código.")
                    continue
                break

            novo_nome = input(f"Novo nome [{produto['nome']}]: ") or produto['nome']
            nova_quantidade = input(f"Nova quantidade [{produto['quantidade']}]: ")
            novo_preco = input(f"Novo preço [{produto['preco']}]: ")
            novo_limite = input(f"Novo estoque mínimo [{produto['limite_minimo']}]: ")
            nova_validade = input(f"Nova validade (dd/mm/aaaa) [{produto['validade']}]: ")

            produto['codigo'] = novo_codigo
            produto['nome'] = novo_nome
            produto['quantidade'] = int(nova_quantidade or produto['quantidade'])
            produto['preco'] = float(novo_preco or produto['preco'])
            produto['limite_minimo'] = int(novo_limite or produto['limite_minimo'])
            produto['validade'] = nova_validade or produto['validade']

            salvar_dados("estoque.json", estoque)
            print(" Produto atualizado com sucesso!")
            return

    print("Produto não encontrado.")

def sistema_cozinha(): # Função para gerir a cozinha (cardápio e receitas)
    while True:
        print("\n=== GESTÃO DA COZINHA ===")
        print("1. Cadastrar Item no Cardápio")
        print("2. Consultar Cardápio")
        print("3. Atualizar Item do Cardápio")
        print("4. Preparar Prato")
        print("5. Atualizar Status de Preparo")  
        print("6. Voltar ao Menu Principal")      
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_item_cardapio()
        elif opcao == "2":
            consultar_cardapio()
        elif opcao == "3":
            atualizar_item_cardapio()
        elif opcao == "4":
            preparar_prato()
        elif opcao == "5":
            atualizar_status_preparo()
        elif opcao == "6":
            break
        else:
            print("Opção inválida.")

def cadastrar_item_cardapio():
    print("\n=== Cadastrar Item no Cardápio ===")
    nome = input("Nome do Prato: ")
    descricao = input("Descrição: ")
    preco = float(input("Preço: "))

    ingredientes = []
    while True:
        ingrediente = input("Ingrediente necessário (ou 'fim' para terminar): ")
        if ingrediente.lower() == 'fim':
            break
        quantidade = float(input(f"Quantidade de {ingrediente}: "))
        ingredientes.append({'ingrediente': ingrediente, 'quantidade': quantidade})

    prato = {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "ingredientes": ingredientes
    }

    cardapio.append(prato)
    salvar_dados("cardapio.json", cardapio)
    print("Prato cadastrado com sucesso!")

def consultar_cardapio(): 
    print("\n=== Cardápio ===")
    if not cardapio:
        print("Nenhum prato cadastrado.")
        return
    for prato in cardapio:
        print(f"\nPrato: {prato['nome']} | Preço: R$ {prato['preco']:.2f}")
        print(f"Descrição: {prato['descricao']}")
        print("Ingredientes:")
        for item in prato['ingredientes']:
            print(f"- {item['codigo']}: {item['quantidade']}")

def atualizar_item_cardapio(): 
    print("\n=== Atualizar Item do Cardápio ===")
    if not cardapio:
        print("Nenhum prato cadastrado.")
        return

    for idx, prato in enumerate(cardapio, 1):
        print(f"{idx}. {prato['nome']}")

    try:
        escolha = int(input("Escolha o número do prato que deseja atualizar: "))
        prato = cardapio[escolha - 1]
    except (ValueError, IndexError):
        print("Escolha inválida.")
        return

    print(f"\nEditando: {prato['nome']}")
    novo_nome = input("Novo nome (ou ENTER para manter): ") or prato['nome']
    nova_descricao = input("Nova descrição (ou ENTER para manter): ") or prato['descricao']
    try:
        novo_preco = input("Novo preço (ou ENTER para manter): ")
        novo_preco = float(novo_preco) if novo_preco else prato['preco']
    except ValueError:
        print("Preço inválido.")
        return

    prato['nome'] = novo_nome
    prato['descricao'] = nova_descricao
    prato['preco'] = novo_preco

    salvar_dados("cardapio.json", cardapio)
    print(" Item atualizado com sucesso!")

def preparar_prato(): 
    print("\n=== Preparar Prato ===")
    if not cardapio:
        print("Nenhum prato cadastrado.")
        return

    for idx, prato in enumerate(cardapio, 1):
        print(f"{idx}. {prato['nome']}")

    try:
        escolha = int(input("Escolha o número do prato a ser preparado: "))
        prato = cardapio[escolha - 1]
    except (ValueError, IndexError):
        print("Escolha inválida.")
        return

    mesa = input("Informe o nome da mesa (ex: Brasil, Alemanha): ").strip().title()

    print(f"\nPreparando: {prato['nome']}...")

    for ingrediente in prato['ingredientes']:
        codigo_ing = ingrediente['codigo'].strip()
        qtd_necessaria = ingrediente['quantidade']
        produto_encontrado = False
        for prod in estoque:
            if prod['codigo'].strip().lower() == codigo_ing.lower():
                produto_encontrado = True
                if prod['quantidade'] < qtd_necessaria:
                    print(f"Ingrediente insuficiente: {prod['nome']} (necessário: {qtd_necessaria}, disponível: {prod['quantidade']})")
                    return
                prod['quantidade'] -= qtd_necessaria
                salvar_dados("estoque.json", estoque)
                break
        if not produto_encontrado:
            print(f"Ingrediente não encontrado no estoque: {codigo_ing}")
            return

    hora_pedido = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    pedido = {
        "prato": prato['nome'],
        "status": "recebido",
        "mesa": mesa,
        "hora_pedido": hora_pedido
    }

    fila_preparo.append(pedido)
    salvar_dados("fila_preparo.json", fila_preparo)

    print(f" Prato '{prato['nome']}' da mesa '{mesa}' enviado para a fila!")

def atualizar_status_preparo():  
    print("\n=== Atualizar Status de Preparo ===")
    if not fila_preparo:
        print("Nenhum prato na fila.")
        return

    for idx, pedido in enumerate(fila_preparo, 1):
        print(f"{idx}. {pedido['prato']} - Status: {pedido['status']}")

    try:
        escolha = int(input("Escolha o número do pedido para atualizar: "))
        pedido = fila_preparo[escolha - 1]
    except (ValueError, IndexError):
        print("Escolha inválida.")
        return

    print(f"Status atual: {pedido['status']}")
    print("Status possíveis: recebido / em preparo / pronto para servir")
    novo_status = input("Digite o novo status: ").strip().lower()

    if novo_status not in ["recebido", "em preparo", "pronto para servir"]:
        print("Status inválido. Tente novamente.")
        return

    pedido['status'] = novo_status
    salvar_dados("fila_preparo.json", fila_preparo)
    print(f"Status de {pedido['prato']} atualizado para '{novo_status}'.")


def sistema_mesas_pedidos(): # Função para gerir mesas e pedidos
    while True:
        print("\n=== GESTÃO DE MESAS E PEDIDOS ===")
        print("1. Cadastrar Mesa")
        print("2. Atribuir Cliente à Mesa")
        print("3. Reservar Mesa")
        print("4. Visualizar Status das Mesas")
        print("5. Registrar Pedido")
        print("6. Modificar Pedido")
        print("7. Cancelar Pedido")
        print("8. Enviar Pedido para Cozinha")
        print("9. Ver Pedidos da Mesa")
        print("10. Cliente Chegou (Confirmar Reserva)")
        print("11. Voltar ao Menu Principal")
        print("12. Marcar Pratos como Entregues") 
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_mesa()
        elif opcao == "2":
            atribuir_cliente()
        elif opcao == "3":
            reservar_mesa()
        elif opcao == "4":
            visualizar_status_mesas()
        elif opcao == "5":
            registrar_pedido()
        elif opcao == "6":
            modificar_pedido()
        elif opcao == "7":
            cancelar_pedido()
        elif opcao == "8":
            enviar_para_cozinha()
        elif opcao == "9":
            ver_pedidos_mesa()
        elif opcao == "10":
            chegada_cliente_reservado()
        elif opcao == "11":
            entregar_prato()  
        elif opcao == "12":
            break
        else:
            print("Opção inválida.")


def cadastrar_mesa():
    nome = input("Nome da Mesa (ex: Brasil, Itália): ").strip().title()
    if any(m['nome'] == nome for m in mesas):
        print("Mesa já cadastrada.")
        return
    try:
        capacidade = int(input("Capacidade da mesa (número de pessoas): "))
    except ValueError:
        print("Capacidade inválida.")
        return
    mesa = {"nome": nome, "capacidade": capacidade, "status": "livre", "pedidos": []}
    mesas.append(mesa)
    salvar_dados("mesas.json", mesas)
    print(f" Mesa '{nome}' cadastrada com sucesso!")

def atribuir_cliente():
    nome_mesa = input("Nome da Mesa: ").strip().title()
    mesa = next((m for m in mesas if m['nome'] == nome_mesa), None)

    if not mesa:
        print("Mesa não encontrada.")
        return

    if mesa['status'] != "livre":
        print("Mesa já está ocupada ou reservada.")
        return

    nome_cliente = input("Nome do Cliente: ").strip().title()
    mesa['status'] = "ocupada"
    mesa['comanda'] = nome_cliente  

    salvar_dados("mesas.json", mesas)
    print(f" Clientes atribuídos à mesa '{nome_mesa}' (Comanda: {nome_cliente}).")

def reservar_mesa():
    print("\n=== Reservar Mesa ===")
    nome = input("Nome da Mesa (ex: Brasil, Alemanha): ").strip().title()
    mesa = next((m for m in mesas if m['nome'] == nome), None)
    if not mesa:
        print("Mesa não encontrada.")
        return
    if mesa['status'] != "livre":
        print(" Mesa já está ocupada ou reservada.")
        return

    responsavel = input("Nome da pessoa responsável pela reserva: ").strip().title()
    try:
        pessoas = int(input("Número de pessoas: "))
    except ValueError:
        print("Número de pessoas inválido.")
        return

    horario = input("Horário da reserva (ex: 19:30): ").strip()
    forma_reserva = input("Forma de reserva (site / ligação / whatsapp): ").strip().lower()
    if forma_reserva not in ['site', 'ligação', 'whatsapp']:
        print("Forma de reserva inválida.")
        return

    mesa['status'] = "reservada"
    mesa['reserva'] = {
        "responsavel": responsavel,
        "pessoas": pessoas,
        "horario": horario,
        "forma": forma_reserva
    }

    salvar_dados("mesas.json", mesas)
    print(f" Mesa '{nome}' reservada com sucesso para {responsavel} às {horario} via {forma_reserva}.")


def visualizar_status_mesas():
    print("\n=== Status das Mesas ===")
    for mesa in mesas:
        info_reserva = ""
        info_comanda = ""
        if mesa['status'] == "reservada" and "reserva" in mesa:
            r = mesa['reserva']
            info_reserva = f" | Reservada por: {r['responsavel']} às {r['horario']} via {r['forma'].capitalize()}"
        if mesa['status'] == "ocupada" and "comanda" in mesa:
            info_comanda = f" | Comanda: {mesa['comanda']}"

        print(f"Mesa: {mesa['nome']} | Capacidade: {mesa['capacidade']} | Status: {mesa['status']}{info_reserva}{info_comanda}")

def registrar_pedido():
    nome = input("Nome da Mesa: ").strip().title()
    mesa = next((m for m in mesas if m['nome'] == nome), None)
    if not mesa:
        print("Mesa não encontrada.")
        return
    if not cardapio:
        print("Cardápio vazio.")
        return

    print("\n--- CARDÁPIO ---")
    for idx, prato in enumerate(cardapio, 1):
        print(f"{idx}. {prato['nome']} - R$ {prato['preco']:.2f}")

    escolha = input("Digite os números dos pratos separados por vírgula (ex: 1,2): ")
    indices = escolha.split(",")

    pedido = []
    total = 0
    for i in indices:
        try:
            prato = cardapio[int(i)-1]
            pedido.append(prato['nome'])
            total += prato['preco']
        except (IndexError, ValueError):
            print(f"Índice inválido: {i}")

    if pedido:
        mesa['pedidos'].append({"itens": pedido, "total": total, "enviado": False})
        salvar_dados("mesas.json", mesas)
        print(" Pedido registrado com sucesso!")

def modificar_pedido():
    nome = input("Nome da Mesa: ").strip().title()
    mesa = next((m for m in mesas if m['nome'] == nome), None)
    if not mesa or not mesa['pedidos']:
        print("Mesa não encontrada ou sem pedidos.")
        return

    ver_pedidos_mesa(nome)
    try:
        idx = int(input("Escolha o número do pedido para modificar: ")) - 1
        pedido = mesa['pedidos'][idx]
    except (IndexError, ValueError):
        print("Pedido inválido.")
        return

    if pedido.get("enviado"):
        print("Pedido já foi enviado à cozinha.")
        return

    print("\n--- CARDÁPIO ---")
    for idx, prato in enumerate(cardapio, 1):
        print(f"{idx}. {prato['nome']} - R$ {prato['preco']:.2f}")

    novo_escolha = input("Digite os novos números de pratos (ex: 1,3): ").split(",")
    novos_itens = []
    novo_total = 0
    for i in novo_escolha:
        try:
            prato = cardapio[int(i)-1]
            novos_itens.append(prato['nome'])
            novo_total += prato['preco']
        except:
            print(f"Índice inválido: {i}")

    pedido['itens'] = novos_itens
    pedido['total'] = novo_total
    salvar_dados("mesas.json", mesas)
    print(" Pedido atualizado com sucesso.")

def cancelar_pedido():
    nome = input("Nome da Mesa: ").strip().title()
    mesa = next((m for m in mesas if m['nome'] == nome), None)
    if not mesa or not mesa['pedidos']:
        print("Mesa não encontrada ou sem pedidos.")
        return

    ver_pedidos_mesa(nome)
    try:
        idx = int(input("Número do pedido a cancelar: ")) - 1
        pedido = mesa['pedidos'][idx]
    except (IndexError, ValueError):
        print("Pedido inválido.")
        return

    if pedido.get("enviado"):
        print("Pedido já foi enviado à cozinha.")
        return

    mesa['pedidos'].pop(idx)
    salvar_dados("mesas.json", mesas)
    print(" Pedido cancelado.")

def enviar_para_cozinha():
    nome = input("Nome da Mesa: ").strip().title()
    mesa = next((m for m in mesas if m['nome'] == nome), None)
    if not mesa or not mesa['pedidos']:
        print("Mesa não encontrada ou sem pedidos.")
        return

    for pedido in mesa['pedidos']:
        if not pedido.get("enviado"):
            for nome_prato in pedido['itens']:
                fila_preparo.append({"prato": nome_prato, "status": "recebido"})
            pedido["enviado"] = True

    salvar_dados("fila_preparo.json", fila_preparo)
    salvar_dados("mesas.json", mesas)
    print(f"Pedidos da mesa '{nome}' enviados à cozinha.")

def ver_pedidos_mesa(nome=None):
    if not nome:
        nome = input("Nome da Mesa: ").strip().title()
    mesa = next((m for m in mesas if m['nome'] == nome), None)
    if not mesa:
        print("Mesa não encontrada.")
        return

    if not mesa['pedidos']:
        print(" Nenhum pedido registrado.")
        return

    print(f"\n Pedidos da Mesa '{nome}':")
    for i, pedido in enumerate(mesa['pedidos'], 1):
        status = "Enviado" if pedido.get("enviado") else "Não enviado"
        print(f"{i}. Itens: {pedido['itens']} | Total: R$ {pedido['total']:.2f} | {status}")

def chegada_cliente_reservado():
    print("\n=== CHEGADA DE CLIENTE COM RESERVA ===")
    nome_mesa = input("Nome da Mesa (ex: Brasil, Alemanha): ").strip().title()
    mesa = next((m for m in mesas if m['nome'] == nome_mesa), None)

    if not mesa:
        print("Mesa não encontrada.")
        return

    if mesa['status'] != "reservada" or "reserva" not in mesa:
        print("Esta mesa não está reservada.")
        return

    nome_cliente = input("Informe o nome da pessoa que fez a reserva: ").strip().title()
    if nome_cliente != mesa['reserva']['responsavel']:
        print("Nome não corresponde ao da reserva.")
        return

    mesa['status'] = "ocupada"
    mesa['comanda'] = nome_cliente   
    del mesa['reserva']  

    salvar_dados("mesas.json", mesas)
    print(f" Mesa '{nome_mesa}' agora está ocupada por {nome_cliente}. Comanda registrada.")

def entregar_prato():
    global fila_preparo  

    if not fila_preparo:
        print("Nenhum prato na fila de preparo.")
        return

    print("\n=== Fila de Preparo ===")
    for idx, item in enumerate(fila_preparo, 1):
        print(f"{idx}. {item['prato']} | Status: {item['status']}")

    escolha = input("Digite os números dos pratos prontos para entrega (ex: 1,3): ").strip()
    indices = escolha.split(",")

    removidos = []
    for i in sorted(set(indices), reverse=True):  
        try:
            idx = int(i) - 1
            if 0 <= idx < len(fila_preparo):
                prato = fila_preparo[idx]['prato']
                removidos.append(prato)
                fila_preparo.pop(idx)
        except ValueError:
            print(f"Valor inválido: {i}")

    salvar_dados("fila_preparo.json", fila_preparo)

    if removidos:
        print(f" Pratos entregues e removidos da fila: {', '.join(removidos)}")
    else:
        print("Nenhum prato foi removido.")


def sistema_pagamentos(): # Função para o sistema de pagamentos
    print("\n=== PAGAMENTO ===")
    numero = input("Número da Mesa (ex: Brasil, Itália): ").strip().title()
    mesa = next((m for m in mesas if m['nome'] == numero), None)
    if not mesa:
        print("Mesa não encontrada.")
        return

    if not mesa['pedidos']:
        print("Nenhum pedido registrado para esta mesa.")
        return

    total_original = sum(p['total'] for p in mesa['pedidos'])
    print(f"Total bruto para a Mesa {mesa['nome']}: R$ {total_original:.2f}")

    ajuste_opcao = input("Deseja aplicar alguma taxa ou desconto? (s/n): ").strip().lower()
    ajuste_tipo = None
    ajuste_valor = 0
    total_geral = total_original

    if ajuste_opcao == "s":
        tipo = input("Digite 'taxa' para adicionar taxa ou 'desconto' para aplicar desconto: ").strip().lower()
        try:
            percentual = float(input("Percentual (%): ").strip())
        except ValueError:
            print("Valor inválido.")
            return

        if tipo == "taxa":
            ajuste_tipo = "Taxa"
            ajuste_valor = (percentual / 100) * total_original
            total_geral += ajuste_valor
        elif tipo == "desconto":
            ajuste_tipo = "Desconto"
            ajuste_valor = (percentual / 100) * total_original
            total_geral -= ajuste_valor
        else:
            print("Tipo inválido.")
            return

        print(f"{ajuste_tipo} de R$ {ajuste_valor:.2f} aplicado.")
        print(f"Total final com {ajuste_tipo.lower()}: R$ {total_geral:.2f}")
    else:
        print(f"Total a pagar: R$ {total_geral:.2f}")

    print("\nFormas de pagamento disponíveis:")
    print("1. Cartao")
    print("2. Dinheiro")
    print("3. Pix")
    forma_pagamento = input("Escolha a forma de pagamento: ")

    if forma_pagamento not in ["1", "2", "3"]:
        print("Forma de pagamento inválida.")
        return

    forma_pagamento_texto = {
        "1": "Cartao",
        "2": "Dinheiro",
        "3": "Pix"
    }[forma_pagamento]

    if forma_pagamento == "1":  
        print("\nEscolha o tipo de pagamento no cartao:")
        print("1. Débito")
        print("2. Crédito")
        tipo_cartao = input("Escolha a opção: ")

        if tipo_cartao == "1":
            forma_pagamento_texto = "Cartao Debito"
        elif tipo_cartao == "2":
            forma_pagamento_texto = "Cartao Credito"

            if total_geral <= 100:
                print("Valor abaixo de R$100,00. Pagamento não pode ser parcelado.")
                parcelas = 1
            elif total_geral <= 300:
                parcelas = int(input("Escolha o número de parcelas (até 4 vezes): "))
                if parcelas > 4:
                    print("O máximo de parcelas no crédito é 4.")
                    return
            else:
                parcelas = int(input("Escolha o número de parcelas (até 8 vezes): "))
                if parcelas > 8:
                    print("O máximo de parcelas no crédito é 8.")
                    return

            valor_parcela = calcular_parcela(total_geral, parcelas)
            print(f"Pagamento no cartão de crédito em {parcelas}x de R$ {valor_parcela:.2f}")
        else:
            print("Opção de pagamento inválida.")
            return

    elif forma_pagamento == "2":  
        dividir_pessoas = input("Deseja dividir o valor entre pessoas? (s/n): ").strip().lower()
        if dividir_pessoas == "s":
            num_pessoas = int(input("Quantas pessoas irão dividir a conta? "))
            valor_por_pessoa = total_geral / num_pessoas
            print(f"Cada pessoa deverá pagar R$ {valor_por_pessoa:.2f}")

        valor_pago = float(input("Digite o valor entregue pelo cliente: R$ "))
        if valor_pago < total_geral:
            print(" Valor insuficiente. Pagamento não pode ser concluído.")
            return
        troco = valor_pago - total_geral
        print(f"Troco a devolver: R$ {troco:.2f}")

    elif forma_pagamento == "3":  
        dividir_pessoas = input("Deseja dividir o valor entre pessoas? (s/n): ").strip().lower()
        if dividir_pessoas == "s":
            num_pessoas = int(input("Quantas pessoas irão dividir a conta? "))
            valor_por_pessoa = total_geral / num_pessoas
            print(f"Cada pessoa deverá pagar R$ {valor_por_pessoa:.2f}")
    venda = {
        "mesa": mesa['nome'],
        "total_bruto": total_original,
        "ajuste": {
            "tipo": ajuste_tipo,
            "valor": ajuste_valor
        } if ajuste_opcao == "s" else None,
        "total_final": total_geral,
        "forma_pagamento": forma_pagamento_texto,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "pedido": [pedido['itens'] for pedido in mesa['pedidos']]
    }

    vendas.append(venda)

    mesa['pedidos'] = []
    mesa['status'] = "livre"
    if "comanda" in mesa:
        del mesa["comanda"]

    salvar_dados("mesas.json", mesas)
    salvar_dados("vendas.json", vendas)

    print(f" Pagamento registrado com sucesso para a Mesa {mesa['nome']}!")

def calcular_parcela(valor_total, parcelas):
    if parcelas == 1:
        return valor_total
    elif parcelas <= 4:
        return valor_total / parcelas
    else:
        juros = 0.05 * (parcelas - 4)  
        valor_com_juros = valor_total * (1 + juros)
        return valor_com_juros / parcelas
    
def sistema_relatorios(): # Função de relatórios financeiros
    while True:
        print("\n=== RELATÓRIOS FINANCEIROS ===")
        print("1. Relatório de Vendas")
        print("2. Voltar ao Menu Principal")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            gerar_relatorio_vendas()
        elif opcao == "2":
            break
        else:
            print("Opção inválida.")

def gerar_relatorio_vendas(): 
    print("\n=== Relatório de Vendas ===")
    vendas = carregar_dados('vendas.json')
    if not vendas:
        print("Nenhuma venda realizada.")
        return

    total_geral = 0
    total_por_dia = defaultdict(float)
    contagem_itens = Counter()
    total_por_mesa = defaultdict(float)
    contagem_mesas = Counter()
    formas_pagamento = Counter()
    quantidade_vendas = 0

    maior_venda = {"valor": 0}

    for venda in vendas:
        mesa = venda.get('mesa')
        total = venda.get('total_final') or venda.get('total', 0)
        forma_pagamento = venda.get('forma_pagamento', 'Desconhecida')
        data = venda.get('data', 'Data não informada')

        try:
            data_formatada = datetime.strptime(data, "%d/%m/%Y %H:%M:%S").date()
        except:
            data_formatada = data  

        print(f"\nMesa: {mesa} | Total: R$ {total:.2f} | Pagamento: {forma_pagamento} | Data: {data_formatada}")
        
        if 'pedido' in venda:
            print("Itens do Pedido:")
            for item in venda['pedido']:
                for produto in item:
                    print(f"- {produto}")
                    contagem_itens[produto] += 1

        total_geral += total
        total_por_dia[str(data_formatada)] += total
        total_por_mesa[mesa] += total
        contagem_mesas[mesa] += 1
        formas_pagamento[forma_pagamento] += 1
        quantidade_vendas += 1

        if total > maior_venda["valor"]:
            maior_venda = {
                "valor": total,
                "mesa": mesa,
                "forma_pagamento": forma_pagamento,
                "data": data,
                "itens": venda.get('pedido', [])
            }
    print("\n=== RESUMO FINANCEIRO ===")
    print(f"Total Geral de Vendas: R$ {total_geral:.2f}")
    if quantidade_vendas > 0:
        print(f"Valor Médio por Venda: R$ {total_geral / quantidade_vendas:.2f}")
    else:
        print("Sem vendas registradas.")

    print("\nTotal por Dia:")
    for dia, total in sorted(total_por_dia.items()):
        print(f"- {dia}: R$ {total:.2f}")

    print("\nGasto por Mesa:")
    for mesa, valor in total_por_mesa.items():
        print(f"- Mesa {mesa}: R$ {valor:.2f}")

    if contagem_itens:
        mais_vendido = contagem_itens.most_common(1)[0]
        print(f"\n Item Mais Vendido: {mais_vendido[0]} ({mais_vendido[1]} vezes)")

    if contagem_mesas:
        mesa_top = contagem_mesas.most_common(1)[0]
        print(f"Mesa com Mais Vendas: {mesa_top[0]} ({mesa_top[1]} vendas | R$ {total_por_mesa[mesa_top[0]]:.2f})")

    if formas_pagamento:
        pagamento_top = formas_pagamento.most_common(1)[0]
        print(f"Forma de Pagamento Mais Usada: {pagamento_top[0]} ({pagamento_top[1]} vezes)")

    if maior_venda["valor"] > 0:
        print("\ Venda de Maior Valor:")
        print(f"- Valor: R$ {maior_venda['valor']:.2f}")
        print(f"- Mesa: {maior_venda['mesa']}")
        print(f"- Forma de Pagamento: {maior_venda['forma_pagamento']}")
        print(f"- Data: {maior_venda['data']}")
        print("- Itens:")
        for item in maior_venda["itens"]:
            for produto in item:
                print(f"  • {produto}")
                
menu_principal()

