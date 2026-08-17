import os
import json

class ClientesService:
    """Gerenciador de persistência e regras de negócio para os Clientes."""
    
    def __init__(self, base_dir=None):
        if base_dir is None:
            from config.settings import get_base_dir
            base_dir = get_base_dir()
        self.data_dir = os.path.join(base_dir, "data")
        self.data_file = os.path.join(self.data_dir, "clientes.json")
        self.garantir_arquivo_dados()

    def garantir_arquivo_dados(self):
        """Cria o diretório e o arquivo JSON inicial caso não existam."""
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.data_file) or os.path.getsize(self.data_file) <= 2:
            self.salvar_clientes([])

    def carregar_clientes(self):
        """Carrega a lista de clientes do arquivo JSON."""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao ler arquivo de clientes: {e}")
            return []

    def salvar_clientes(self, clientes):
        """Salva a lista inteira de clientes no arquivo JSON."""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(clientes, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar clientes: {e}")
            return False

    def adicionar_cliente(self, nome_cliente, endereco, data_ultimo_pedido, contato):
        """Adiciona um novo cliente e persiste no arquivo JSON."""
        clientes = self.carregar_clientes()
        novo_id = f"CLI-{1001 + len(clientes):04d}"
        
        ids_existentes = {c["id"] for c in clientes}
        while novo_id in ids_existentes:
            novo_id = f"CLI-{int(novo_id.split('-')[1]) + 1:04d}"

        novo_cliente = {
            "id": novo_id,
            "nome_cliente": nome_cliente,
            "endereco": endereco,
            "data_ultimo_pedido": data_ultimo_pedido,
            "contato": contato
        }
        clientes.append(novo_cliente)
        self.salvar_clientes(clientes)
        return novo_cliente

    def atualizar_cliente(self, cliente_id, nome_cliente, endereco, data_ultimo_pedido, contato):
        """Atualiza os dados de um cliente existente pelo ID."""
        clientes = self.carregar_clientes()
        atualizado = False
        for c in clientes:
            if c["id"] == cliente_id:
                c["nome_cliente"] = nome_cliente
                c["endereco"] = endereco
                c["data_ultimo_pedido"] = data_ultimo_pedido
                c["contato"] = contato
                atualizado = True
                break
        if atualizado:
            self.salvar_clientes(clientes)
        return atualizado

    def remover_cliente(self, cliente_id):
        """Remove um cliente pelo ID e atualiza o JSON."""
        clientes = self.carregar_clientes()
        clientes_filtrados = [c for c in clientes if c["id"] != cliente_id]
        if len(clientes_filtrados) < len(clientes):
            self.salvar_clientes(clientes_filtrados)
            return True
        return False
