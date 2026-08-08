import customtkinter as ctk
from tkinter import ttk, messagebox
from config.settings import PALETTE, get_color
from services.estoque_service import EstoqueService
from services.pdf_service import PDFService
from components.estoque_form_modal import EstoqueFormModal

class EstoqueView(ctk.CTkFrame):
    """Módulo completo de Gerenciamento de Estoque com Tabela, CRUD e Persistência em JSON."""
    
    def __init__(self, master, base_dir=None, **kwargs):
        super().__init__(master, fg_color=PALETTE["main_bg"], corner_radius=0, **kwargs)
        
        self.base_dir = base_dir
        self.service = EstoqueService(base_dir=base_dir)
        self.estoque_cache = []
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # 1. Cabeçalho do Módulo
        self.criar_cabecalho()
        
        # 2. Barra de Ferramentas (Pesquisa e Botões de Ação)
        self.criar_barra_ferramentas()
        
        # 3. Tabela de Estoque (Treeview Estilizado)
        self.criar_tabela_estoque()
        
        # Carregar dados iniciais
        self.atualizar_tabela()

    def criar_cabecalho(self):
        """Cria o cabeçalho superior do módulo de estoque."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(28, 6))
        header_frame.grid_columnconfigure(0, weight=1)
        
        lbl_title = ctk.CTkLabel(
            header_frame,
            text="Controle de Estoque",
            font=ctk.CTkFont(family="Georgia", size=28, weight="bold"),
            text_color=PALETTE["title_text"],
            anchor="w"
        )
        lbl_title.pack(anchor="w")
        
        lbl_sub = ctk.CTkLabel(
            header_frame,
            text="Gerencie tintas, papéis, molduras e insumos criativos com preços unitários e saldos.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=PALETTE["subtitle_text"],
            anchor="w"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

    def criar_barra_ferramentas(self):
        """Cria os controles de busca e botões de Novo Item, Editar e Excluir."""
        tools_frame = ctk.CTkFrame(self, fg_color="transparent")
        tools_frame.grid(row=1, column=0, sticky="ew", padx=40, pady=(16, 16))
        tools_frame.grid_columnconfigure(0, weight=1)
        
        # Campo de Pesquisa
        self.entry_pesquisa = ctk.CTkEntry(
            tools_frame,
            placeholder_text="🔍 Pesquisar material, categoria ou ID...",
            height=42,
            corner_radius=12,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=13)
        )
        self.entry_pesquisa.grid(row=0, column=0, sticky="ew", padx=(0, 16))
        self.entry_pesquisa.bind("<KeyRelease>", self.filtrar_estoque)
        
        # Container de Botões
        actions_frame = ctk.CTkFrame(tools_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=1, sticky="e")
        
        # Botão Excluir
        btn_excluir = ctk.CTkButton(
            actions_frame,
            text="🗑️ Excluir",
            height=42,
            corner_radius=12,
            fg_color="transparent",
            border_color="#E57373",
            border_width=1,
            text_color="#C62828",
            hover_color="#FFEBEE",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.acao_excluir
        )
        btn_excluir.pack(side="left", padx=4)
        
        # Botão Editar
        btn_editar = ctk.CTkButton(
            actions_frame,
            text="✏️ Editar",
            height=42,
            corner_radius=12,
            fg_color="transparent",
            border_color=PALETTE["card_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.acao_editar
        )
        btn_editar.pack(side="left", padx=4)
        
        # Botão Exportar PDF
        btn_pdf = ctk.CTkButton(
            actions_frame,
            text="📄 PDF",
            height=42,
            corner_radius=12,
            fg_color="transparent",
            border_color=PALETTE["card_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.acao_exportar_pdf
        )
        btn_pdf.pack(side="left", padx=4)

        # Botão Adicionar Item
        btn_novo = ctk.CTkButton(
            actions_frame,
            text="+ Novo Item",
            height=42,
            corner_radius=12,
            fg_color=PALETTE["active_pill"],
            hover_color=PALETTE["active_pill_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.acao_adicionar
        )
        btn_novo.pack(side="left", padx=(4, 0))

    def criar_tabela_estoque(self):
        """Cria e estiliza a tabela ttk.Treeview com barras de rolagem."""
        table_container = ctk.CTkFrame(
            self,
            fg_color=PALETTE["card_bg"],
            border_color=PALETTE["card_border"],
            border_width=1,
            corner_radius=16
        )
        table_container.grid(row=2, column=0, sticky="nsew", padx=40, pady=(0, 30))
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)
        
        # Estilização do Treeview
        self.atualizar_estilo_tema()
        
        colunas = ("id", "nome", "categoria", "quantidade", "unidade", "preco_unitario", "valor_total")
        
        self.tree = ttk.Treeview(
            table_container,
            columns=colunas,
            show="headings",
            style="Estoque.Treeview",
            selectmode="browse"
        )
        
        # Definição das colunas
        self.tree.heading("id", text="ID Item", anchor="w")
        self.tree.heading("nome", text="Nome do Material", anchor="w")
        self.tree.heading("categoria", text="Categoria", anchor="w")
        self.tree.heading("quantidade", text="Qtd. Disponível", anchor="w")
        self.tree.heading("unidade", text="Unidade", anchor="w")
        self.tree.heading("preco_unitario", text="Preço Unit. (R$)", anchor="w")
        self.tree.heading("valor_total", text="Valor Total em Estoque", anchor="w")
        
        self.tree.column("id", width=90, minwidth=80, anchor="w")
        self.tree.column("nome", width=260, minwidth=180, anchor="w")
        self.tree.column("categoria", width=140, minwidth=110, anchor="w")
        self.tree.column("quantidade", width=120, minwidth=100, anchor="w")
        self.tree.column("unidade", width=90, minwidth=70, anchor="w")
        self.tree.column("preco_unitario", width=130, minwidth=100, anchor="w")
        self.tree.column("valor_total", width=150, minwidth=120, anchor="w")
        
        # Tag para indicar estoque baixo
        self.tree.tag_configure("estoque_baixo", foreground="#D32F2F")
        
        # Scrollbar vertical
        scrollbar = ctk.CTkScrollbar(
            table_container,
            orientation="vertical",
            command=self.tree.yview,
            button_color=PALETTE["active_pill"],
            button_hover_color=PALETTE["active_pill_hover"]
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=16)
        
        # Evento de duplo clique para editar
        self.tree.bind("<Double-1>", lambda e: self.acao_editar())

    def atualizar_estilo_tema(self, modo=None):
        """Atualiza as cores da tabela TTK de acordo com o modo claro/escuro."""
        if modo is None:
            modo = ctk.get_appearance_mode()
            
        style = ttk.Style()
        style.theme_use("default")
        
        sb_bg = get_color(PALETTE["sidebar_bg"], modo)
        br_title = get_color(PALETTE["brand_title"], modo)
        t_text = get_color(PALETTE["title_text"], modo)
        in_hover = get_color(PALETTE["inactive_hover"], modo)
        card_bg = get_color(PALETTE["card_bg"], modo)
        act_pill = get_color(PALETTE["active_pill"], modo)
        
        style.configure(
            "Estoque.Treeview.Heading",
            background=sb_bg,
            foreground=br_title,
            font=("Segoe UI", 11, "bold"),
            rowheight=38,
            relief="flat"
        )
        style.map("Estoque.Treeview.Heading", background=[('active', in_hover)])
        
        style.configure(
            "Estoque.Treeview",
            background=card_bg,
            fieldbackground=card_bg,
            foreground=t_text,
            font=("Segoe UI", 11),
            rowheight=36,
            borderwidth=0
        )
        style.map(
            "Estoque.Treeview",
            background=[('selected', act_pill), ('focus', act_pill)],
            foreground=[('selected', '#FFFFFF'), ('focus', '#FFFFFF')]
        )

    def atualizar_tabela(self):
        """Carrega os dados do serviço de estoque e redesenha as linhas na tabela."""
        self.estoque_cache = self.service.carregar_estoque()
        self.renderizar_linhas(self.estoque_cache)

    def renderizar_linhas(self, lista_estoque):
        """Limpa a tabela e insere as linhas fornecidas."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for item in lista_estoque:
            qtd = float(item.get("quantidade", 0))
            preco = float(item.get("preco_unitario", 0))
            val_total = qtd * preco
            
            preco_str = f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            total_str = f"R$ {val_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            qtd_str = f"{qtd:.1f}".rstrip('0').rstrip('.') if qtd % 1 != 0 else f"{int(qtd)}"
            
            tags = ()
            if qtd <= 5:
                tags = ("estoque_baixo",)

            self.tree.insert(
                "",
                "end",
                iid=item["id"],
                values=(
                    item.get("id", ""),
                    item.get("nome", "-"),
                    item.get("categoria", "-"),
                    qtd_str,
                    item.get("unidade", "un"),
                    preco_str,
                    total_str
                ),
                tags=tags
            )

    def filtrar_estoque(self, event=None):
        """Filtra as linhas exibidas conforme a busca."""
        termo = self.entry_pesquisa.get().strip().lower()
        if not termo:
            self.renderizar_linhas(self.estoque_cache)
            return
            
        filtrados = [
            item for item in self.estoque_cache
            if termo in item.get("nome", "").lower()
            or termo in item.get("categoria", "").lower()
            or termo in item.get("id", "").lower()
        ]
        self.renderizar_linhas(filtrados)

    def acao_adicionar(self):
        """Abre o formulário modal para cadastrar um novo item no estoque."""
        def on_save(dados):
            self.service.adicionar_item(
                nome=dados["nome"],
                categoria=dados["categoria"],
                quantidade=dados["quantidade"],
                unidade=dados["unidade"],
                preco_unitario=dados["preco_unitario"]
            )
            self.atualizar_tabela()
            messagebox.showinfo("Sucesso", "Material adicionado ao estoque!", parent=self)

        modal = EstoqueFormModal(self, title="Adicionar Novo Material", on_save=on_save)

    def acao_editar(self):
        """Abre o formulário modal para editar o item do estoque selecionado."""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Seleção Necessária", "Por favor, selecione um item na tabela para editar.", parent=self)
            return
            
        item_id = selecionado[0]
        item_atual = next((item for item in self.estoque_cache if item["id"] == item_id), None)
        
        if not item_atual:
            return

        def on_save(dados):
            self.service.atualizar_item(
                item_id=item_id,
                nome=dados["nome"],
                categoria=dados["categoria"],
                quantidade=dados["quantidade"],
                unidade=dados["unidade"],
                preco_unitario=dados["preco_unitario"]
            )
            self.atualizar_tabela()
            messagebox.showinfo("Sucesso", "Item do estoque atualizado com sucesso!", parent=self)

        modal = EstoqueFormModal(self, title=f"Editar Item {item_id}", item_data=item_atual, on_save=on_save)

    def acao_excluir(self):
        """Confirma e remove o item do estoque selecionado."""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Seleção Necessária", "Por favor, selecione um item na tabela para excluir.", parent=self)
            return
            
        item_id = selecionado[0]
        confirmar = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja remover o item {item_id} do estoque?", parent=self)
        if confirmar:
            if self.service.remover_item(item_id):
                self.atualizar_tabela()
                messagebox.showinfo("Sucesso", "Item removido do estoque!", parent=self)

    def acao_exportar_pdf(self):
        """Exporta a lista atual do estoque para PDF com caixa de seleção de arquivo."""
        if not self.estoque_cache:
            messagebox.showwarning("Sem Dados", "Não há itens no estoque para exportar no momento.", parent=self)
            return

        colunas = ["ID Item", "Nome do Material", "Categoria", "Qtd. Disponível", "Unidade", "Preço Unit. (R$)", "Valor Total (R$)"]
        linhas = []
        total_estoque_val = 0.0

        for item in self.estoque_cache:
            qtd = float(item.get("quantidade", 0))
            preco = float(item.get("preco_unitario", 0))
            val_tot = qtd * preco
            total_estoque_val += val_tot

            preco_str = f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            total_str = f"R$ {val_tot:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            qtd_str = f"{qtd:.1f}".rstrip('0').rstrip('.') if qtd % 1 != 0 else f"{int(qtd)}"

            linhas.append([
                item.get("id", ""),
                item.get("nome", "-"),
                item.get("categoria", "-"),
                qtd_str,
                item.get("unidade", "un"),
                preco_str,
                total_str
            ])

        totais_info = {
            "Total de Itens Cadastrados": len(linhas),
            "Valor Total Investido em Estoque": f"R$ {total_estoque_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        }

        PDFService.exportar_tabela_pdf(
            titulo_documento="Relatorio_de_Estoque",
            colunas_titulos=colunas,
            dados_linhas=linhas,
            totais_info=totais_info,
            base_dir=self.base_dir,
            parent_window=self,
            orientacao_paisagem=True
        )
