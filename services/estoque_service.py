import os
import json

class EstoqueService:
    """Gerenciador de persistência e regras de negócio para o Estoque de insumos/materiais."""
    
    def __init__(self, base_dir=None):
        if base_dir is None:
            from config.settings import get_base_dir
            base_dir = get_base_dir()
        self.data_dir = os.path.join(base_dir, "data")
        self.data_file = os.path.join(self.data_dir, "estoque.json")
        self.garantir_arquivo_dados()

    def garantir_arquivo_dados(self):
        """Cria o diretório e o arquivo JSON inicial caso não existam."""
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.data_file):
            self.salvar_estoque([])

    def carregar_estoque(self):
        """Carrega a lista de itens do estoque do arquivo JSON."""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao ler arquivo de estoque: {e}")
            return []

    def salvar_estoque(self, estoque):
        """Salva a lista inteira de itens no arquivo JSON."""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(estoque, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar estoque: {e}")
            return False

    def adicionar_item(self, nome, categoria, quantidade, unidade, preco_unitario):
        """Adiciona um novo item ao estoque e persiste no arquivo JSON."""
        estoque = self.carregar_estoque()
        novo_id = f"EST-{1001 + len(estoque):04d}"
        
        ids_existentes = {item["id"] for item in estoque}
        while novo_id in ids_existentes:
            novo_id = f"EST-{int(novo_id.split('-')[1]) + 1:04d}"

        novo_item = {
            "id": novo_id,
            "nome": nome,
            "categoria": categoria,
            "quantidade": float(quantidade),
            "unidade": unidade,
            "preco_unitario": float(preco_unitario)
        }
        estoque.append(novo_item)
        self.salvar_estoque(estoque)
        return novo_item

    def atualizar_item(self, item_id, nome, categoria, quantidade, unidade, preco_unitario):
        """Atualiza os dados de um item existente pelo ID."""
        estoque = self.carregar_estoque()
        atualizado = False
        for item in estoque:
            if item["id"] == item_id:
                item["nome"] = nome
                item["categoria"] = categoria
                item["quantidade"] = float(quantidade)
                item["unidade"] = unidade
                item["preco_unitario"] = float(preco_unitario)
                atualizado = True
                break
        if atualizado:
            self.salvar_estoque(estoque)
        return atualizado

    def remover_item(self, item_id):
        """Remove um item do estoque pelo ID."""
        estoque = self.carregar_estoque()
        estoque_filtrado = [item for item in estoque if item["id"] != item_id]
        if len(estoque_filtrado) < len(estoque):
            self.salvar_estoque(estoque_filtrado)
            return True
        return False

    def debitar_estoque(self, itens_usados):
        """
        Debita as quantidades dos itens usados do estoque.
        itens_usados: lista de dicionários [{'item_id': 'EST-1001', 'quantidade': 2.0}, ...]
        Retorna (sucesso, mensagem_ou_erro)
        """
        estoque = self.carregar_estoque()
        mapa_estoque = {item["id"]: item for item in estoque}
        
        # 1. Verificar disponibilidade de todos os itens antes de debitar
        for item_usado in itens_usados:
            item_id = item_usado.get("item_id")
            qtd_pedida = float(item_usado.get("quantidade", 0))
            if item_id in mapa_estoque:
                qtd_disponivel = float(mapa_estoque[item_id]["quantidade"])
                if qtd_pedida > qtd_disponivel:
                    nome_item = mapa_estoque[item_id]["nome"]
                    return False, f"Estoque insuficiente para '{nome_item}'. Disponível: {qtd_disponivel:.1f}, Requerido: {qtd_pedida:.1f}."

        # 2. Realizar os débitos
        for item_usado in itens_usados:
            item_id = item_usado.get("item_id")
            qtd_pedida = float(item_usado.get("quantidade", 0))
            if item_id in mapa_estoque:
                mapa_estoque[item_id]["quantidade"] = round(mapa_estoque[item_id]["quantidade"] - qtd_pedida, 2)

        self.salvar_estoque(estoque)
        return True, "Estoque atualizado com sucesso!"

    def estornar_estoque(self, itens_usados):
        """
        Devolve ao estoque as quantidades dos itens de um pedido cancelado ou editado.
        itens_usados: lista de dicionários [{'item_id': 'EST-1001', 'quantidade': 2.0}, ...]
        """
        if not itens_usados:
            return True
            
        estoque = self.carregar_estoque()
        mapa_estoque = {item["id"]: item for item in estoque}
        
        for item_usado in itens_usados:
            item_id = item_usado.get("item_id")
            qtd_devolver = float(item_usado.get("quantidade", 0))
            if item_id in mapa_estoque:
                mapa_estoque[item_id]["quantidade"] = round(mapa_estoque[item_id]["quantidade"] + qtd_devolver, 2)

        self.salvar_estoque(estoque)
        return True
