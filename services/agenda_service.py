import os
import json
from datetime import datetime, date
from services.pedidos_service import PedidosService

class AgendaService:
    """Serviço que gerencia notas da agenda e sincroniza automaticamente com as entregas de pedidos."""
    
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, "data")
        self.data_file = os.path.join(self.data_dir, "agenda_notas.json")
        self.pedidos_service = PedidosService(base_dir=base_dir)
        self.garantir_arquivo_dados()

    def garantir_arquivo_dados(self):
        """Cria o diretório e o arquivo JSON inicial com notas de exemplo caso não existam."""
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.data_file):
            hoje = datetime.now().strftime("%d/%m/%Y")
            notas_iniciais = [
                {
                    "id": "NOT-1001",
                    "data": hoje,
                    "titulo": "🎨 Organizar paletas de cores do atelier",
                    "horario": "10:00",
                    "tipo": "nota"
                },
                {
                    "id": "NOT-1002",
                    "data": "15/08/2026",
                    "titulo": "📦 Enviar orçamento para novos clientes",
                    "horario": "15:30",
                    "tipo": "nota"
                }
            ]
            self.salvar_notas(notas_iniciais)

    def carregar_notas(self):
        """Carrega a lista de notas do arquivo JSON."""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao ler notas da agenda: {e}")
            return []

    def salvar_notas(self, notas):
        """Salva a lista de notas no arquivo JSON."""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(notas, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar notas da agenda: {e}")
            return False

    def adicionar_nota(self, data_str, titulo, horario="09:00"):
        """Adiciona uma nova nota pessoal para uma data específica."""
        notas = self.carregar_notas()
        novo_id = f"NOT-{1001 + len(notas):04d}"
        
        ids_existentes = {n["id"] for n in notas}
        while novo_id in ids_existentes:
            novo_id = f"NOT-{int(novo_id.split('-')[1]) + 1:04d}"

        nova_nota = {
            "id": novo_id,
            "data": data_str,
            "titulo": titulo,
            "horario": horario if horario else "09:00",
            "tipo": "nota"
        }
        notas.append(nova_nota)
        self.salvar_notas(notas)
        return nova_nota

    def remover_nota(self, nota_id):
        """Remove uma nota pelo ID."""
        notas = self.carregar_notas()
        notas_filtradas = [n for n in notas if n["id"] != nota_id]
        if len(notas_filtradas) < len(notas):
            self.salvar_notas(notas_filtradas)
            return True
        return False

    def obter_eventos_por_data(self, data_str):
        """Retorna todos os eventos (Entregas automáticas de pedidos + Notas pessoais) para uma data."""
        eventos = []
        
        # 1. Carregar Entregas automáticas dos Pedidos
        pedidos = self.pedidos_service.carregar_pedidos()
        for p in pedidos:
            dt_ent = p.get("data_entrega", "").strip()
            if dt_ent == data_str:
                eventos.append({
                    "id": f"ENTREGA-{p['id']}",
                    "data": data_str,
                    "titulo": f"📦 Entrega: {p['nome_cliente']} - {p['produto']}",
                    "horario": "Data Limite",
                    "tipo": "entrega",
                    "detalhes": p
                })
                
        # 2. Carregar Notas pessoais da Agenda
        notas = self.carregar_notas()
        for n in notas:
            if n.get("data", "").strip() == data_str:
                eventos.append(n)
                
        return eventos

    def obter_resumo_mes(self, ano, mes):
        """Retorna um dicionário dos dias do mês com contagem de entregas e notas."""
        pedidos = self.pedidos_service.carregar_pedidos()
        notas = self.carregar_notas()
        
        resumo = {}
        prefixo_mes = f"/{mes:02d}/{ano}"
        
        # Entregas
        for p in pedidos:
            dt = p.get("data_entrega", "").strip()
            if dt.endswith(prefixo_mes):
                if dt not in resumo:
                    resumo[dt] = {"tem_entrega": False, "tem_nota": False, "qtd": 0}
                resumo[dt]["tem_entrega"] = True
                resumo[dt]["qtd"] += 1
                
        # Notas
        for n in notas:
            dt = n.get("data", "").strip()
            if dt.endswith(prefixo_mes):
                if dt not in resumo:
                    resumo[dt] = {"tem_entrega": False, "tem_nota": False, "qtd": 0}
                resumo[dt]["tem_nota"] = True
                resumo[dt]["qtd"] += 1
                
        return resumo
