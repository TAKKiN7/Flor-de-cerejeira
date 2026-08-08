import os
import json
import uuid
from datetime import datetime

class PedidosService:
    """Gerenciador de persistência e regras de negócio para os Pedidos."""
    
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(base_dir, "data")
        self.data_file = os.path.join(self.data_dir, "pedidos.json")
        self.garantir_arquivo_dados()

    def garantir_arquivo_dados(self):
        """Cria o diretório e o arquivo JSON inicial com dados de exemplo caso não existam."""
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.data_file):
            dados_iniciais = [
                {
                    "id": "PED-1001",
                    "data_pedido": "04/08/2026",
                    "nome_cliente": "Camila Oliveira",
                    "produto": "Quadro Floral Aquarela 30x40",
                    "valor_produto": "180.00",
                    "data_entrega": "12/08/2026"
                },
                {
                    "id": "PED-1002",
                    "data_pedido": "03/08/2026",
                    "nome_cliente": "Beatriz Lima",
                    "produto": "Convite de Casamento Botânico (Kit 50 un)",
                    "valor_produto": "350.00",
                    "data_entrega": "20/08/2026"
                },
                {
                    "id": "PED-1003",
                    "data_pedido": "01/08/2026",
                    "nome_cliente": "Juliana Santos",
                    "produto": "Caneca Personalizada Ilustração Hanna",
                    "valor_produto": "65.00",
                    "data_entrega": "08/08/2026"
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

    def adicionar_pedido(self, data_pedido, nome_cliente, produto, valor_produto, data_entrega):
        """Adiciona um novo pedido e persiste no arquivo JSON."""
        pedidos = self.carregar_pedidos()
        novo_id = f"PED-{1001 + len(pedidos):04d}"
        
        # Garantir unicidade caso já exista o ID
        ids_existentes = {p["id"] for p in pedidos}
        while novo_id in ids_existentes:
            novo_id = f"PED-{int(novo_id.split('-')[1]) + 1:04d}"

        novo_pedido = {
            "id": novo_id,
            "data_pedido": data_pedido,
            "nome_cliente": nome_cliente,
            "produto": produto,
            "valor_produto": str(valor_produto),
            "data_entrega": data_entrega
        }
        pedidos.append(novo_pedido)
        self.salvar_pedidos(pedidos)
        return novo_pedido

    def atualizar_pedido(self, pedido_id, data_pedido, nome_cliente, produto, valor_produto, data_entrega):
        """Atualiza os dados de um pedido existente pelo ID."""
        pedidos = self.carregar_pedidos()
        atualizado = False
        for p in pedidos:
            if p["id"] == pedido_id:
                p["data_pedido"] = data_pedido
                p["nome_cliente"] = nome_cliente
                p["produto"] = produto
                p["valor_produto"] = str(valor_produto)
                p["data_entrega"] = data_entrega
                atualizado = True
                break
        if atualizado:
            self.salvar_pedidos(pedidos)
        return atualizado

    def remover_pedido(self, pedido_id):
        """Remove um pedido pelo ID e atualiza o JSON."""
        pedidos = self.carregar_pedidos()
        pedidos_filtrados = [p for p in pedidos if p["id"] != pedido_id]
        if len(pedidos_filtrados) < len(pedidos):
            self.salvar_pedidos(pedidos_filtrados)
            return True
        return False
