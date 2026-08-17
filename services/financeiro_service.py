import os
import json
from datetime import datetime

class FinanceiroService:
    """Gerenciador de persistência e regras de negócio para a Gestão Financeira."""
    
    MESES_NOME = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]

    def __init__(self, base_dir=None):
        if base_dir is None:
            from config.settings import get_base_dir
            base_dir = get_base_dir()
        self.data_dir = os.path.join(base_dir, "data")
        self.data_file = os.path.join(self.data_dir, "financeiro.json")
        self.garantir_arquivo_dados()

    def garantir_arquivo_dados(self):
        """Cria o diretório e o arquivo JSON inicial caso não existam."""
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.data_file) or os.path.getsize(self.data_file) <= 2:
            self.salvar_lancamentos([])

    def carregar_lancamentos(self):
        """Carrega a lista de lançamentos financeiros do arquivo JSON."""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao ler arquivo de lançamentos financeiros: {e}")
            return []

    def salvar_lancamentos(self, lancamentos):
        """Salva a lista inteira de lançamentos no arquivo JSON."""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(lancamentos, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar lançamentos financeiros: {e}")
            return False

    def adicionar_lancamento(self, tipo, data, descricao, categoria, valor, forma_pagamento):
        """Adiciona um novo lançamento (Entrada ou Saída) e persiste no arquivo JSON."""
        lancamentos = self.carregar_lancamentos()
        novo_id = f"FIN-{1001 + len(lancamentos):04d}"
        
        ids_existentes = {item["id"] for item in lancamentos}
        while novo_id in ids_existentes:
            novo_id = f"FIN-{int(novo_id.split('-')[1]) + 1:04d}"

        val = float(valor)
        val_entrada = val if tipo == "Entrada" else 0.0
        val_saida = val if tipo == "Saída" else 0.0

        novo_item = {
            "id": novo_id,
            "tipo": tipo,
            "data": data,
            "descricao": descricao,
            "categoria": categoria,
            "valor_entrada": val_entrada,
            "valor_saida": val_saida,
            "forma_pagamento": forma_pagamento
        }
        lancamentos.append(novo_item)
        self.salvar_lancamentos(lancamentos)
        return novo_item

    def atualizar_lancamento(self, item_id, tipo, data, descricao, categoria, valor, forma_pagamento):
        """Atualiza um lançamento financeiro existente."""
        lancamentos = self.carregar_lancamentos()
        atualizado = False
        val = float(valor)
        val_entrada = val if tipo == "Entrada" else 0.0
        val_saida = val if tipo == "Saída" else 0.0

        for item in lancamentos:
            if item["id"] == item_id:
                item["tipo"] = tipo
                item["data"] = data
                item["descricao"] = descricao
                item["categoria"] = categoria
                item["valor_entrada"] = val_entrada
                item["valor_saida"] = val_saida
                item["forma_pagamento"] = forma_pagamento
                atualizado = True
                break

        if atualizado:
            self.salvar_lancamentos(lancamentos)
        return atualizado

    def remover_lancamento(self, item_id):
        """Remove um lançamento pelo ID."""
        lancamentos = self.carregar_lancamentos()
        filtrados = [item for item in lancamentos if item["id"] != item_id]
        if len(filtrados) < len(lancamentos):
            self.salvar_lancamentos(filtrados)
            return True
        return False

    def obter_lancamentos_por_mes(self, mes_num, ano_num):
        """Filtra os lançamentos pertencentes a um determinado mês (1-12) e ano."""
        todos = self.carregar_lancamentos()
        filtrados = []
        for item in todos:
            try:
                partes = item["data"].split("/")
                if len(partes) == 3:
                    m = int(partes[1])
                    a = int(partes[2])
                    if m == mes_num and a == ano_num:
                        filtrados.append(item)
            except Exception:
                pass
        return filtrados

    def calcular_totais_mes(self, mes_num, ano_num):
        """Calcula o total de entradas, total de saídas e o saldo líquido do mês."""
        lancamentos = self.obter_lancamentos_por_mes(mes_num, ano_num)
        total_entradas = sum(float(i.get("valor_entrada", 0)) for i in lancamentos)
        total_saidas = sum(float(i.get("valor_saida", 0)) for i in lancamentos)
        saldo_mes = total_entradas - total_saidas
        return {
            "total_entradas": round(total_entradas, 2),
            "total_saidas": round(total_saidas, 2),
            "saldo_mes": round(saldo_mes, 2)
        }

    def obter_relatorio_anual(self, ano_num):
        """Gera o relatório mensal de janeiro a dezembro para o ano especificado."""
        todos = self.carregar_lancamentos()
        meses_dados = {m: {"entradas": 0.0, "saidas": 0.0} for m in range(1, 13)}

        for item in todos:
            try:
                partes = item["data"].split("/")
                if len(partes) == 3:
                    m = int(partes[1])
                    a = int(partes[2])
                    if a == ano_num and 1 <= m <= 12:
                        meses_dados[m]["entradas"] += float(item.get("valor_entrada", 0))
                        meses_dados[m]["saidas"] += float(item.get("valor_saida", 0))
            except Exception:
                pass

        relatorio = []
        total_anual_entradas = 0.0
        total_anual_saidas = 0.0

        for m_num in range(1, 13):
            ent = round(meses_dados[m_num]["entradas"], 2)
            sai = round(meses_dados[m_num]["saidas"], 2)
            sal = round(ent - sai, 2)
            total_anual_entradas += ent
            total_anual_saidas += sai

            relatorio.append({
                "mes_num": m_num,
                "mes_nome": self.MESES_NOME[m_num - 1],
                "entradas": ent,
                "saidas": sai,
                "saldo": sal
            })

        return {
            "ano": ano_num,
            "meses": relatorio,
            "total_entradas": round(total_anual_entradas, 2),
            "total_saidas": round(total_anual_saidas, 2),
            "lucro_liquido": round(total_anual_entradas - total_anual_saidas, 2)
        }
