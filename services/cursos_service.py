import os
import json
from datetime import datetime

class CursosService:
    """Gerenciador de persistência e regras de negócio para Cursos e Módulos."""
    
    CATEGORIAS_PADRAO = ["Costura", "Bordado", "Modelagem", "Pintura", "Artesanato", "Empreendedorismo", "Outro"]

    def __init__(self, base_dir=None):
        if base_dir is None:
            from config.settings import get_base_dir
            base_dir = get_base_dir()
        self.data_dir = os.path.join(base_dir, "data")
        self.data_file = os.path.join(self.data_dir, "cursos.json")
        self.garantir_arquivo_dados()

    def garantir_arquivo_dados(self):
        """Cria o diretório e o arquivo JSON inicial com cursos de exemplo caso não existam."""
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.data_file) or os.path.getsize(self.data_file) <= 2:
            dados_iniciais = [
                {
                    "id": "CRS-1001",
                    "titulo": "Costura Criativa para Iniciantes",
                    "categoria": "Costura",
                    "descricao": "Aprenda o manuseio da máquina, tipos de tecidos e confeccione bolsas e necessaires.",
                    "data_criacao": datetime.now().strftime("%d/%m/%Y"),
                    "modulos": [
                        {"id": "MOD-1", "titulo": "Módulo 1: Conhecendo a Máquina e Linhas", "concluido": True},
                        {"id": "MOD-2", "titulo": "Módulo 2: Leitura de Moldes e Corte do Tecido", "concluido": True},
                        {"id": "MOD-3", "titulo": "Módulo 3: Montagem de Necessaires", "concluido": False},
                        {"id": "MOD-4", "titulo": "Módulo 4: Colocação de Zíper e Acabamentos", "concluido": False}
                    ]
                },
                {
                    "id": "CRS-1002",
                    "titulo": "Bordado Livre e Ponto Avançado",
                    "categoria": "Bordado",
                    "descricao": "Pontos decorativos em bastidor e aplicação de detalhes florais em tecidos nobres.",
                    "data_criacao": datetime.now().strftime("%d/%m/%Y"),
                    "modulos": [
                        {"id": "MOD-1", "titulo": "Módulo 1: Pontos Básicos (Haste, Nó Francês)", "concluido": True},
                        {"id": "MOD-2", "titulo": "Módulo 2: Matiz e Sombreamento", "concluido": True},
                        {"id": "MOD-3", "titulo": "Módulo 3: Finalização de Bastidor", "concluido": True}
                    ]
                }
            ]
            self.salvar_cursos(dados_iniciais)

    def carregar_cursos(self):
        """Carrega a lista de cursos do arquivo JSON."""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao ler arquivo de cursos: {e}")
            return []

    def salvar_cursos(self, cursos):
        """Salva a lista inteira de cursos no arquivo JSON."""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(cursos, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar cursos: {e}")
            return False

    def gerar_novo_id(self, cursos):
        """Gera um ID único sequencial para o curso."""
        numeros = []
        for c in cursos:
            raw_id = c.get("id", "")
            if raw_id.startswith("CRS-"):
                try:
                    numeros.append(int(raw_id.split("-")[1]))
                except ValueError:
                    pass
        proximo = max(numeros) + 1 if numeros else 1001
        return f"CRS-{proximo}"

    def calcular_progresso(self, curso):
        """Calcula o total, concluídos, percentual e texto de status de um curso."""
        modulos = curso.get("modulos", [])
        total = len(modulos)
        if total == 0:
            return {
                "total": 0,
                "concluidos": 0,
                "percentual": 0.0,
                "fator": 0.0,
                "texto": "Nenhum módulo"
            }
        concluidos = sum(1 for m in modulos if m.get("concluido", False))
        percentual = round((concluidos / total) * 100, 1)
        fator = concluidos / total
        return {
            "total": total,
            "concluidos": concluidos,
            "percentual": percentual,
            "fator": fator,
            "texto": f"{concluidos} de {total} Módulos ({int(percentual)}%)"
        }

    def adicionar_curso(self, titulo, categoria, descricao=""):
        """Adiciona um novo curso."""
        cursos = self.carregar_cursos()
        novo_curso = {
            "id": self.gerar_novo_id(cursos),
            "titulo": titulo.strip(),
            "categoria": categoria.strip() or "Geral",
            "descricao": descricao.strip(),
            "data_criacao": datetime.now().strftime("%d/%m/%Y"),
            "modulos": []
        }
        cursos.insert(0, novo_curso)
        if self.salvar_cursos(cursos):
            return novo_curso
        return None

    def atualizar_curso(self, curso_id, titulo, categoria, descricao):
        """Atualiza os dados de um curso existente."""
        cursos = self.carregar_cursos()
        for c in cursos:
            if c.get("id") == curso_id:
                c["titulo"] = titulo.strip()
                c["categoria"] = categoria.strip()
                c["descricao"] = descricao.strip()
                self.salvar_cursos(cursos)
                return True
        return False

    def excluir_curso(self, curso_id):
        """Exclui um curso por ID."""
        cursos = self.carregar_cursos()
        novos_cursos = [c for c in cursos if c.get("id") != curso_id]
        if len(novos_cursos) < len(cursos):
            return self.salvar_cursos(novos_cursos)
        return False

    def adicionar_modulo(self, curso_id, titulo_modulo):
        """Adiciona um novo módulo a um curso existente."""
        cursos = self.carregar_cursos()
        for c in cursos:
            if c.get("id") == curso_id:
                modulos = c.get("modulos", [])
                novo_mod_id = f"MOD-{len(modulos) + 1}"
                modulos.append({
                    "id": novo_mod_id,
                    "titulo": titulo_modulo.strip(),
                    "concluido": False
                })
                c["modulos"] = modulos
                self.salvar_cursos(cursos)
                return True
        return False

    def toggle_modulo(self, curso_id, modulo_id):
        """Alterna a conclusão de um módulo (true/false)."""
        cursos = self.carregar_cursos()
        for c in cursos:
            if c.get("id") == curso_id:
                for m in c.get("modulos", []):
                    if m.get("id") == modulo_id:
                        m["concluido"] = not m.get("concluido", False)
                        self.salvar_cursos(cursos)
                        return True
        return False

    def atualizar_modulo(self, curso_id, modulo_id, novo_titulo, concluido):
        """Atualiza título e/ou status de conclusão de um módulo."""
        cursos = self.carregar_cursos()
        for c in cursos:
            if c.get("id") == curso_id:
                for m in c.get("modulos", []):
                    if m.get("id") == modulo_id:
                        m["titulo"] = novo_titulo.strip()
                        m["concluido"] = bool(concluido)
                        self.salvar_cursos(cursos)
                        return True
        return False

    def excluir_modulo(self, curso_id, modulo_id):
        """Remove um módulo de um curso."""
        cursos = self.carregar_cursos()
        for c in cursos:
            if c.get("id") == curso_id:
                modulos = c.get("modulos", [])
                c["modulos"] = [m for m in modulos if m.get("id") != modulo_id]
                self.salvar_cursos(cursos)
                return True
        return False
