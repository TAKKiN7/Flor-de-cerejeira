import os
import json
from services.estoque_service import EstoqueService

class PedidosService:
    """Gerenciador de persistência e regras de negócio para os Pedidos e integração com Estoque."""
    
    def __init__(self, base_dir=None, estoque_service=None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, "data")
        self.data_file = os.path.join(self.data_dir, "pedidos.json")
        self.estoque_service = estoque_service or EstoqueService(base_dir=base_dir)
        self.garantir_arquivo_dados()

    def garantir_arquivo_dados(self):
        """Cria o diretório e o arquivo JSON inicial com dados de exemplo caso não existam."""
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.data_file) or os.path.getsize(self.data_file) <= 2:
            dados_iniciais = [
                {
                    "id": "PED-1001",
                    "data_pedido": "04/08/2026",
                    "nome_cliente": "Camila Oliveira",
                    "produto": "Quadro Floral Aquarela 30x40",
                    "valor_produto": "98.50",
                    "data_entrega": "12/08/2026",
                    "itens_usados": [
                        {"item_id": "EST-1001", "nome": "Papel Canson Aquarela 300g (Folha A3)", "quantidade": 1.0, "preco_unitario": 8.50, "subtotal": 8.50},
                        {"item_id": "EST-1003", "nome": "Moldura de Madeira 30x40cm", "quantidade": 2.0, "preco_unitario": 45.00, "subtotal": 90.00}
                    ]
                },
                {
                    "id": "PED-1002",
                    "data_pedido": "03/08/2026",
                    "nome_cliente": "Beatriz Lima",
                    "produto": "Convite de Casamento Botânico (Kit 50 un)",
                    "valor_produto": "42.50",
                    "data_entrega": "20/08/2026",
                    "itens_usados": [
                        {"item_id": "EST-1001", "nome": "Papel Canson Aquarela 300g (Folha A3)", "quantidade": 5.0, "preco_unitario": 8.50, "subtotal": 42.50}
                    ]
                },
                {
                    "id": "PED-1003",
                    "data_pedido": "01/08/2026",
                    "nome_cliente": "Juliana Santos",
                    "produto": "Caneca Personalizada Ilustração Hanna",
                    "valor_produto": "18.00",
                    "data_entrega": "08/08/2026",
                    "itens_usados": [
                        {"item_id": "EST-1005", "nome": "Caneca Porcelana Branca 325ml", "quantidade": 1.0, "preco_unitario": 18.00, "subtotal": 18.00}
                    ]
                }
            ]
            self.salvar_pedidos(dados_iniciais)

    def carregar_pedidos(self):
        """Carrega a lista de pedidos do arquivo JSON."""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao ler arquivo de pedidos: {e}")
            return []

    def salvar_pedidos(self, pedidos):
        """Salva a lista inteira de pedidos no arquivo JSON."""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(pedidos, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar pedidos: {e}")
            return False

    def adicionar_pedido(self, data_pedido, nome_cliente, produto, valor_produto, data_entrega, itens_usados=None):
        """
        Adiciona um novo pedido, debita os materiais do estoque e persiste no arquivo JSON.
        """
        if itens_usados is None:
            itens_usados = []

        # 1. Debitar itens do estoque
        if itens_usados:
            sucesso, msg = self.estoque_service.debitar_estoque(itens_usados)
            if not sucesso:
                raise ValueError(msg)

        pedidos = self.carregar_pedidos()
        novo_id = f"PED-{1001 + len(pedidos):04d}"
        
        ids_existentes = {p["id"] for p in pedidos}
        while novo_id in ids_existentes:
            novo_id = f"PED-{int(novo_id.split('-')[1]) + 1:04d}"

        novo_pedido = {
            "id": novo_id,
            "data_pedido": data_pedido,
            "nome_cliente": nome_cliente,
            "produto": produto,
            "valor_produto": str(valor_produto),
            "data_entrega": data_entrega,
            "itens_usados": itens_usados
        }
        pedidos.append(novo_pedido)
        self.salvar_pedidos(pedidos)
        return novo_pedido

    def atualizar_pedido(self, pedido_id, data_pedido, nome_cliente, produto, valor_produto, data_entrega, itens_usados=None):
        """
        Atualiza os dados de um pedido existente, ajustando o estoque (estornando os antigos e debitando os novos).
        """
        if itens_usados is None:
            itens_usados = []

        pedidos = self.carregar_pedidos()
        pedido_antigo = next((p for p in pedidos if p["id"] == pedido_id), None)
        if not pedido_antigo:
            return False

        # 1. Estornar os itens antigos do estoque
        itens_antigos = pedido_antigo.get("itens_usados", [])
        self.estoque_service.estornar_estoque(itens_antigos)

        # 2. Tentar debitar os novos itens
        if itens_usados:
            sucesso, msg = self.estoque_service.debitar_estoque(itens_usados)
            if not sucesso:
                # Re-debitar os antigos caso os novos falhem para manter a consistência
                self.estoque_service.debitar_estoque(itens_antigos)
                raise ValueError(msg)

        # 3. Atualizar o objeto do pedido
        pedido_antigo["data_pedido"] = data_pedido
        pedido_antigo["nome_cliente"] = nome_cliente
        pedido_antigo["produto"] = produto
        pedido_antigo["valor_produto"] = str(valor_produto)
        pedido_antigo["data_entrega"] = data_entrega
        pedido_antigo["itens_usados"] = itens_usados

        self.salvar_pedidos(pedidos)
        return True

    def remover_pedido(self, pedido_id):
        """Remove um pedido pelo ID, devolve os materiais ao estoque e atualiza o JSON."""
        pedidos = self.carregar_pedidos()
        pedido_alvo = next((p for p in pedidos if p["id"] == pedido_id), None)
        if not pedido_alvo:
            return False

        # Estornar materiais de volta ao estoque
        itens_antigos = pedido_alvo.get("itens_usados", [])
        self.estoque_service.estornar_estoque(itens_antigos)

        pedidos_filtrados = [p for p in pedidos if p["id"] != pedido_id]
        self.salvar_pedidos(pedidos_filtrados)
        return True
