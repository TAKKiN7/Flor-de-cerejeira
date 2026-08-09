import customtkinter as ctk
from tkinter import messagebox
from config.settings import PALETTE, get_color
from services.cursos_service import CursosService
from components.curso_form_modal import CursoFormModal
from components.curso_modulos_modal import CursoModulosModal

class CursosView(ctk.CTkFrame):
    """Módulo completo de Gerenciamento de Cursos com cards visuais e progresso de módulos em tempo real."""
    
    def __init__(self, master, base_dir=None, **kwargs):
        super().__init__(master, fg_color=PALETTE["main_bg"], corner_radius=0, **kwargs)
        
        self.base_dir = base_dir
        self.service = CursosService(base_dir=base_dir)
        self.cursos_cache = []
        self.filtro_status = "Todos"
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # 1. Cabeçalho do Módulo
        self.criar_cabecalho()
        
        # 2. Barra de Ferramentas (Pesquisa, Filtros de Status e Botão Novo)
        self.criar_barra_ferramentas()
        
        # 3. Área Scrollável de Cards
        self.criar_area_cards()
        
        # Carregar dados iniciais
        self.atualizar_tabela()

    def atualizar_tabela(self):
        """Método padrão chamado pela JanelaPrincipal ao selecionar a aba."""
        self.carregar_e_renderizar_cursos()

    def criar_cabecalho(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(28, 6))
        header_frame.grid_columnconfigure(0, weight=1)
        
        lbl_title = ctk.CTkLabel(
            header_frame,
            text="Meus Cursos e Capacitação",
            font=ctk.CTkFont(family="Georgia", size=28, weight="bold"),
            text_color=PALETTE["title_text"],
            anchor="w"
        )
        lbl_title.pack(anchor="w")
        
        lbl_sub = ctk.CTkLabel(
            header_frame,
            text="Acompanhe o andamento e a evolução dos módulos de cada curso diretamente pelos cards.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=PALETTE["subtitle_text"],
            anchor="w"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

    def criar_barra_ferramentas(self):
        tools_frame = ctk.CTkFrame(self, fg_color="transparent")
        tools_frame.grid(row=1, column=0, sticky="ew", padx=40, pady=(16, 16))
        tools_frame.grid_columnconfigure(0, weight=1)
        
        # Campo de Pesquisa
        self.entry_pesquisa = ctk.CTkEntry(
            tools_frame,
            placeholder_text="🔍 Pesquisar por nome do curso ou categoria...",
            height=42,
            corner_radius=12,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=13)
        )
        self.entry_pesquisa.grid(row=0, column=0, sticky="ew", padx=(0, 16))
        self.entry_pesquisa.bind("<KeyRelease>", lambda e: self.renderizar_cards())
        
        # Container Direita: Filtro de Status + Botão Novo
        actions_frame = ctk.CTkFrame(tools_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=1, sticky="e")
        
        # Segmented Button de Filtro com cores padronizadas da paleta Flor de Cerejeira
        self.seg_filter = ctk.CTkSegmentedButton(
            actions_frame,
            values=["Todos", "Em Andamento", "Concluídos"],
            height=38,
            corner_radius=10,
            fg_color=PALETTE["card_border"],
            selected_color=PALETTE["active_pill"],
            selected_hover_color=PALETTE["active_pill_hover"],
            unselected_color=PALETTE["sidebar_bg"],
            unselected_hover_color=PALETTE["inactive_hover"],
            text_color=PALETTE["brand_title"],
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.alterar_filtro_status
        )
        self.seg_filter.set("Todos")
        self.seg_filter.pack(side="left", padx=(0, 16))
        
        # Botão Novo Curso
        btn_novo = ctk.CTkButton(
            actions_frame,
            text="➕ Novo Curso",
            height=42,
            corner_radius=12,
            fg_color=PALETTE["active_pill"],
            hover_color=PALETTE["active_pill_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.abrir_modal_novo_curso
        )
        btn_novo.pack(side="left")

    def alterar_filtro_status(self, valor):
        self.filtro_status = valor
        self.renderizar_cards()

    def criar_area_cards(self):
        self.scroll_cards = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.scroll_cards.grid(row=2, column=0, sticky="nsew", padx=40, pady=(0, 24))
        self.scroll_cards.grid_columnconfigure(0, weight=1)
        self.scroll_cards.grid_columnconfigure(1, weight=1)

    def carregar_e_renderizar_cursos(self):
        self.cursos_cache = self.service.carregar_cursos()
        self.renderizar_cards()

    def renderizar_cards(self):
        # Desfocar foco ativo para evitar TclError em callbacks pendentes de widgets destruídos
        try:
            self.focus_set()
        except Exception:
            pass

        # Limpar cards antigos
        for child in list(self.scroll_cards.winfo_children()):
            try:
                child.destroy()
            except Exception:
                pass
            
        termo = self.entry_pesquisa.get().strip().lower()
        
        # Filtrar cursos
        cursos_filtrados = []
        for c in self.cursos_cache:
            titulo = c.get("titulo", "").lower()
            cat = c.get("categoria", "").lower()
            desc = c.get("descricao", "").lower()
            
            # Checar pesquisa por texto
            if termo and not (termo in titulo or termo in cat or termo in desc):
                continue
                
            # Checar filtro de status
            prog = self.service.calcular_progresso(c)
            if self.filtro_status == "Em Andamento" and (prog["total"] == 0 or prog["percentual"] == 100):
                continue
            if self.filtro_status == "Concluídos" and (prog["total"] == 0 or prog["percentual"] < 100):
                continue
                
            cursos_filtrados.append(c)

        if not cursos_filtrados:
            msg = "Nenhum curso encontrado." if termo or self.filtro_status != "Todos" else "Nenhum curso cadastrado ainda.\nClique no botão '➕ Novo Curso' para começar!"
            lbl_vazio = ctk.CTkLabel(
                self.scroll_cards,
                text=msg,
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=PALETTE["subtitle_text"],
                justify="center"
            )
            lbl_vazio.grid(row=0, column=0, columnspan=2, pady=60)
            return

        # Renderizar em 2 colunas
        for idx, curso in enumerate(cursos_filtrados):
            row = idx // 2
            col = idx % 2
            self.criar_card_curso(curso, row, col)

    def criar_card_curso(self, curso, row, col):
        curso_id = curso.get("id")
        prog = self.service.calcular_progresso(curso)
        
        card = ctk.CTkFrame(
            self.scroll_cards,
            fg_color=PALETTE["card_bg"],
            border_color=PALETTE["card_border"],
            border_width=1,
            corner_radius=14
        )
        card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        card.grid_columnconfigure(0, weight=1)
        
        # 1. Topo do Card: Badge de Categoria + Ações (Editar, Excluir)
        top_frame = ctk.CTkFrame(card, fg_color="transparent")
        top_frame.pack(fill="x", padx=16, pady=(14, 6))
        top_frame.grid_columnconfigure(0, weight=1)
        
        # Badge da Categoria
        badge_cat = ctk.CTkLabel(
            top_frame,
            text=f"  {curso.get('categoria', 'Geral')}  ",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#FFFFFF",
            fg_color=PALETTE["active_pill"],
            corner_radius=8,
            height=22
        )
        badge_cat.grid(row=0, column=0, sticky="w")
        
        # Ações
        actions_box = ctk.CTkFrame(top_frame, fg_color="transparent")
        actions_box.grid(row=0, column=1, sticky="e")
        
        btn_edit = ctk.CTkButton(
            actions_box,
            text="✏️",
            width=30,
            height=28,
            corner_radius=6,
            fg_color="transparent",
            hover_color=PALETTE["inactive_hover"],
            text_color=PALETTE["inactive_text"],
            font=ctk.CTkFont(size=12),
            command=lambda c=curso: self.abrir_modal_editar_curso(c)
        )
        btn_edit.pack(side="left", padx=2)
        
        btn_del = ctk.CTkButton(
            actions_box,
            text="🗑️",
            width=30,
            height=28,
            corner_radius=6,
            fg_color="transparent",
            hover_color="#FFEBEE",
            text_color="#C62828",
            font=ctk.CTkFont(size=12),
            command=lambda c_id=curso_id, t=curso.get("titulo"): self.excluir_curso(c_id, t)
        )
        btn_del.pack(side="left", padx=2)
        
        # 2. Título & Descrição
        lbl_titulo = ctk.CTkLabel(
            card,
            text=curso.get("titulo", "Sem título"),
            font=ctk.CTkFont(family="Georgia", size=17, weight="bold"),
            text_color=PALETTE["title_text"],
            anchor="w",
            wraplength=380
        )
        lbl_titulo.pack(anchor="w", padx=16, pady=(4, 2))
        
        if curso.get("descricao"):
            lbl_desc = ctk.CTkLabel(
                card,
                text=curso.get("descricao"),
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=PALETTE["subtitle_text"],
                anchor="w",
                justify="left",
                wraplength=380
            )
            lbl_desc.pack(anchor="w", padx=16, pady=(0, 10))

        # 3. Seção de Progresso Geral
        prog_frame = ctk.CTkFrame(card, fg_color="transparent")
        prog_frame.pack(fill="x", padx=16, pady=(6, 8))
        prog_frame.grid_columnconfigure(0, weight=1)
        
        # Label de Progresso (%) e Contagem
        lbl_prog_txt = ctk.CTkLabel(
            prog_frame,
            text=prog["texto"],
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=PALETTE["brand_title"],
            anchor="w"
        )
        lbl_prog_txt.grid(row=0, column=0, sticky="w")
        
        # Badge de Status (Concluído / Em Andamento / Não Iniciado)
        if prog["total"] > 0 and prog["percentual"] == 100:
            st_text = "✓ Concluído"
            st_bg = "#E8F5E9"
            st_fg = "#2E7D32"
        elif prog["concluidos"] > 0:
            st_text = "⚡ Em Andamento"
            st_bg = "#FFF3E0"
            st_fg = "#E65100"
        else:
            st_text = "📝 Não Iniciado"
            st_bg = "#ECEFF1"
            st_fg = "#546E7A"
            
        badge_status = ctk.CTkLabel(
            prog_frame,
            text=f" {st_text} ",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=st_fg,
            fg_color=st_bg,
            corner_radius=6,
            height=20
        )
        badge_status.grid(row=0, column=1, sticky="e")
        
        # Barra de Progresso
        pbar = ctk.CTkProgressBar(
            card,
            height=10,
            corner_radius=5,
            progress_color=PALETTE["active_pill"]
        )
        pbar.pack(fill="x", padx=16, pady=(4, 12))
        pbar.set(prog["fator"])
        
        # 4. Resumo Inline de Módulos (Checklist direto no Card!)
        modulos = curso.get("modulos", [])
        if modulos:
            mod_box = ctk.CTkFrame(
                card,
                fg_color=PALETTE["sidebar_bg"],
                border_color=PALETTE["card_border"],
                border_width=1,
                corner_radius=10
            )
            mod_box.pack(fill="x", padx=16, pady=(0, 12))
            
            lbl_mod_header = ctk.CTkLabel(
                mod_box,
                text="📋 Módulos do Curso:",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=PALETTE["brand_title"]
            )
            lbl_mod_header.pack(anchor="w", padx=10, pady=(6, 4))
            
            # Exibir até 4 módulos diretamente no card com checkbox interativo
            for mod in modulos[:5]:
                m_id = mod.get("id")
                m_tit = mod.get("titulo", "")
                m_concl = mod.get("concluido", False)
                
                row_item = ctk.CTkFrame(mod_box, fg_color="transparent")
                row_item.pack(fill="x", padx=8, pady=2)
                row_item.grid_columnconfigure(1, weight=1)
                
                var_c = ctk.BooleanVar(value=m_concl)
                chk_item = ctk.CTkCheckBox(
                    row_item,
                    text="",
                    variable=var_c,
                    width=18,
                    checkbox_width=18,
                    checkbox_height=18,
                    fg_color=PALETTE["active_pill"],
                    hover_color=PALETTE["active_pill_hover"],
                    command=lambda c_id=curso_id, m_id=m_id: self.toggle_modulo_direto(c_id, m_id)
                )
                chk_item.grid(row=0, column=0, padx=(0, 6), pady=2)
                
                lbl_m_tit = ctk.CTkLabel(
                    row_item,
                    text=f"{'✓ ' if m_concl else ''}{m_tit}",
                    font=ctk.CTkFont(family="Segoe UI", size=12),
                    text_color=PALETTE["subtitle_text"] if m_concl else PALETTE["title_text"],
                    anchor="w"
                )
                lbl_m_tit.grid(row=0, column=1, sticky="ew", pady=2)
                
            if len(modulos) > 5:
                lbl_more = ctk.CTkLabel(
                    mod_box,
                    text=f"+ {len(modulos) - 5} outros módulos...",
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    text_color=PALETTE["subtitle_text"]
                )
                lbl_more.pack(anchor="w", padx=10, pady=(2, 6))

        # 5. Botão de Ação Inferior: Gerenciar Módulos
        btn_modulos = ctk.CTkButton(
            card,
            text="📚 Gerenciar Módulos & Aulas",
            height=38,
            corner_radius=10,
            fg_color="transparent",
            border_color=PALETTE["card_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=lambda c=curso: self.abrir_modal_modulos(c)
        )
        btn_modulos.pack(fill="x", padx=16, pady=(0, 14))

    def toggle_modulo_direto(self, curso_id, modulo_id):
        if self.service.toggle_modulo(curso_id, modulo_id):
            self.after(50, self.carregar_e_renderizar_cursos)

    def abrir_modal_novo_curso(self):
        def on_save(dados):
            if self.service.adicionar_curso(dados["titulo"], dados["categoria"], dados["descricao"]):
                self.carregar_e_renderizar_cursos()

        CursoFormModal(self, title="Novo Curso", on_save=on_save)

    def abrir_modal_editar_curso(self, curso):
        def on_save(dados):
            if self.service.atualizar_curso(curso.get("id"), dados["titulo"], dados["categoria"], dados["descricao"]):
                self.carregar_e_renderizar_cursos()

        CursoFormModal(self, title="Editar Curso", curso_data=curso, on_save=on_save)

    def abrir_modal_modulos(self, curso):
        CursoModulosModal(self, curso=curso, service=self.service, on_update=self.carregar_e_renderizar_cursos)

    def excluir_curso(self, curso_id, titulo):
        if messagebox.askyesno("Excluir Curso", f"Deseja realmente excluir o curso '{titulo}' e todos os seus módulos?", parent=self):
            if self.service.excluir_curso(curso_id):
                self.carregar_e_renderizar_cursos()
