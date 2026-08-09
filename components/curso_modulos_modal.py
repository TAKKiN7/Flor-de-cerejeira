import customtkinter as ctk
from tkinter import messagebox
from config.settings import PALETTE, centralizar_janela
from services.cursos_service import CursosService

class CursoModulosModal(ctk.CTkToplevel):
    """Modal interativa para visualização e gerenciamento detalhado dos módulos de um curso."""
    
    def __init__(self, parent, curso, service=None, on_update=None):
        super().__init__(parent)
        
        self.parent = parent
        self.curso_id = curso.get("id")
        self.service = service or CursosService()
        self.on_update = on_update
        
        self.title(f"Módulos - {curso.get('titulo')}")
        self.geometry("640x620")
        self.minsize(580, 500)
        self.configure(fg_color=PALETTE["main_bg"])
        
        centralizar_janela(self, 640, 620, parent)
        self.transient(parent)
        self.grab_set()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # 1. Cabeçalho da Modal com Info do Curso
        self.criar_cabecalho(curso)
        
        # 2. Formulário de Novo Módulo
        self.criar_form_novo_modulo()
        
        # 3. Lista Scrollável de Módulos
        self.criar_lista_modulos()
        
        # Carregar Módulos
        self.recarregar_dados()

    def recarregar_dados(self):
        """Busca os dados mais recentes do curso no serviço e redesenha a lista."""
        cursos = self.service.carregar_cursos()
        curso_atual = next((c for c in cursos if c.get("id") == self.curso_id), None)
        
        if not curso_atual:
            self.destroy()
            return
            
        self.curso = curso_atual
        
        # Atualizar cabeçalho e barra de progresso
        prog = self.service.calcular_progresso(self.curso)
        self.lbl_subtitulo.configure(text=f"Categoria: {self.curso.get('categoria', 'Geral')} • {prog['texto']}")
        self.progress_bar.set(prog["fator"])
        self.lbl_percentual.configure(text=f"{int(prog['percentual'])}%")
        
        # Renderizar itens da lista
        self.renderizar_modulos()
        
        # Disparar callback de atualização para a view principal
        if self.on_update:
            self.on_update()

    def criar_cabecalho(self, curso):
        header_frame = ctk.CTkFrame(self, fg_color=PALETTE["sidebar_bg"], corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(fill="x", padx=24, pady=(18, 12))
        
        lbl_title = ctk.CTkLabel(
            title_box,
            text=curso.get("titulo", "Curso"),
            font=ctk.CTkFont(family="Georgia", size=20, weight="bold"),
            text_color=PALETTE["brand_title"],
            anchor="w"
        )
        lbl_title.pack(anchor="w")
        
        self.lbl_subtitulo = ctk.CTkLabel(
            title_box,
            text="Carregando progresso...",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=PALETTE["subtitle_text"],
            anchor="w"
        )
        self.lbl_subtitulo.pack(anchor="w", pady=(2, 0))
        
        # Container da Barra de Progresso
        prog_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        prog_box.pack(fill="x", padx=24, pady=(0, 16))
        prog_box.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ctk.CTkProgressBar(
            prog_box,
            height=12,
            corner_radius=6,
            progress_color=PALETTE["active_pill"]
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        
        self.lbl_percentual = ctk.CTkLabel(
            prog_box,
            text="0%",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=PALETTE["brand_title"],
            width=45
        )
        self.lbl_percentual.grid(row=0, column=1)

    def criar_form_novo_modulo(self):
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.grid(row=1, column=0, sticky="ew", padx=24, pady=(16, 8))
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.entry_novo_mod = ctk.CTkEntry(
            input_frame,
            placeholder_text="➕ Digite o nome do novo módulo/aula...",
            height=42,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=13)
        )
        self.entry_novo_mod.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.entry_novo_mod.bind("<Return>", lambda e: self.adicionar_modulo())
        
        btn_add = ctk.CTkButton(
            input_frame,
            text="Adicionar Módulo",
            height=42,
            corner_radius=10,
            fg_color=PALETTE["active_pill"],
            hover_color=PALETTE["active_pill_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.adicionar_modulo
        )
        btn_add.grid(row=0, column=1)

    def criar_lista_modulos(self):
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.scroll_frame.grid(row=2, column=0, sticky="nsew", padx=24, pady=(8, 16))
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def renderizar_modulos(self):
        # Limpar scroll_frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        modulos = self.curso.get("modulos", [])
        
        if not modulos:
            lbl_vazio = ctk.CTkLabel(
                self.scroll_frame,
                text="Nenhum módulo cadastrado ainda.\nUse o campo acima para adicionar o primeiro módulo do curso!",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=PALETTE["subtitle_text"],
                justify="center"
            )
            lbl_vazio.pack(pady=40)
            return

        for idx, mod in enumerate(modulos):
            mod_id = mod.get("id")
            titulo = mod.get("titulo", f"Módulo {idx + 1}")
            concluido = mod.get("concluido", False)
            
            card = ctk.CTkFrame(
                self.scroll_frame,
                fg_color=PALETTE["card_bg"],
                border_color=PALETTE["card_border"],
                border_width=1,
                corner_radius=10
            )
            card.pack(fill="x", pady=4)
            card.grid_columnconfigure(1, weight=1)
            
            # Checkbox de conclusão
            var_chk = ctk.BooleanVar(value=concluido)
            chk = ctk.CTkCheckBox(
                card,
                text="",
                variable=var_chk,
                width=24,
                checkbox_width=22,
                checkbox_height=22,
                fg_color=PALETTE["active_pill"],
                hover_color=PALETTE["active_pill_hover"],
                command=lambda m_id=mod_id: self.toggle_modulo(m_id)
            )
            chk.grid(row=0, column=0, padx=(12, 8), pady=12)
            
            # Título do Módulo com fonte normal ou riscada (strikethrough visual via estilo/cor)
            cor_texto = PALETTE["subtitle_text"] if concluido else PALETTE["title_text"]
            lbl_mod = ctk.CTkLabel(
                card,
                text=f"{'✓ ' if concluido else ''}{titulo}",
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold" if not concluido else "normal"),
                text_color=cor_texto,
                anchor="w"
            )
            lbl_mod.grid(row=0, column=1, sticky="ew", padx=4, pady=12)
            
            # Botão Excluir Módulo
            btn_del = ctk.CTkButton(
                card,
                text="🗑️",
                width=34,
                height=32,
                corner_radius=8,
                fg_color="transparent",
                hover_color="#FFEBEE",
                text_color="#C62828",
                font=ctk.CTkFont(size=13),
                command=lambda m_id=mod_id, t=titulo: self.excluir_modulo(m_id, t)
            )
            btn_del.grid(row=0, column=2, padx=(4, 10), pady=8)

    def adicionar_modulo(self):
        nome_mod = self.entry_novo_mod.get().strip()
        if not nome_mod:
            return
            
        if self.service.adicionar_modulo(self.curso_id, nome_mod):
            self.entry_novo_mod.delete(0, "end")
            self.recarregar_dados()

    def toggle_modulo(self, modulo_id):
        if self.service.toggle_modulo(self.curso_id, modulo_id):
            self.recarregar_dados()

    def excluir_modulo(self, modulo_id, titulo):
        if messagebox.askyesno("Excluir Módulo", f"Deseja remover o módulo '{titulo}'?", parent=self):
            if self.service.excluir_modulo(self.curso_id, modulo_id):
                self.recarregar_dados()
