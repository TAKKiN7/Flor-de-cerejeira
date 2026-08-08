import customtkinter as ctk
from tkinter import ttk, messagebox
from config.settings import PALETTE, get_color
from services.clientes_service import ClientesService
from components.cliente_form_modal import ClienteFormModal

class ClientesView(ctk.CTkFrame):
    """Módulo completo de Gerenciamento de Clientes com Tabela, CRUD e Persistência em JSON."""
    
    def __init__(self, master, base_dir=None, **kwargs):
        super().__init__(master, fg_color=PALETTE["main_bg"], corner_radius=0, **kwargs)
        
        self.service = ClientesService(base_dir=base_dir)
        self.clientes_cache = []
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # 1. Cabeçalho do Módulo
        self.criar_cabecalho()
        
        # 2. Barra de Ferramentas (Pesquisa e Botões de Ação)
        self.criar_barra_ferramentas()
        
        # 3. Tabela de Clientes (Treeview Estilizado)
        self.criar_tabela_clientes()
        
        # Carregar dados iniciais
        self.atualizar_tabela()

    def criar_cabecalho(self):
        """Cria o cabeçalho superior do módulo de clientes."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(28, 6))
        header_frame.grid_columnconfigure(0, weight=1)
        
        lbl_title = ctk.CTkLabel(
            header_frame,
            text="Cadastro de Clientes",
            font=ctk.CTkFont(family="Georgia", size=28, weight="bold"),
            text_color=PALETTE["title_text"],
            anchor="w"
        )
        lbl_title.pack(anchor="w")
        
        lbl_sub = ctk.CTkLabel(
            header_frame,
            text="Consulte e organize a lista de clientes, contatos e histórico de pedidos.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=PALETTE["subtitle_text"],
            anchor="w"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

    def criar_barra_ferramentas(self):
        """Cria os controles de busca e botões de Novo, Editar e Excluir."""
        tools_frame = ctk.CTkFrame(self, fg_color="transparent")
        tools_frame.grid(row=1, column=0, sticky="ew", padx=40, pady=(16, 16))
        tools_frame.grid_columnconfigure(0, weight=1)
        
        # Campo de Pesquisa
        self.entry_pesquisa = ctk.CTkEntry(
            tools_frame,
            placeholder_text="🔍 Pesquisar por nome, contato ou endereço...",
            height=42,
            corner_radius=12,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=13)
        )
        self.entry_pesquisa.grid(row=0, column=0, sticky="ew", padx=(0, 16))
        self.entry_pesquisa.bind("<KeyRelease>", self.filtrar_clientes)
        
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
        
        # Botão Adicionar
        btn_novo = ctk.CTkButton(
            actions_frame,
            text="+ Novo Cliente",
            height=42,
            corner_radius=12,
            fg_color=PALETTE["active_pill"],
            hover_color=PALETTE["active_pill_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.acao_adicionar
        )
        btn_novo.pack(side="left", padx=(4, 0))

    def criar_tabela_clientes(self):
        """Cria e estiliza a tabela ttk.Treeview para exibição dos clientes."""
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
        
        # Estilização do Treeview usando cores puras via get_color
        self.atualizar_estilo_tema()
        
        colunas = ("id", "nome_cliente", "endereco", "data_ultimo_pedido", "contato")
        
        self.tree = ttk.Treeview(
            table_container,
            columns=colunas,
            show="headings",
            style="Clientes.Treeview",
            selectmode="browse"
        )
        
        # Definição das colunas com alinhamento à esquerda (anchor="w")
        self.tree.heading("id", text="ID Cliente", anchor="w")
        self.tree.heading("nome_cliente", text="Nome do Cliente", anchor="w")
        self.tree.heading("endereco", text="Endereço", anchor="w")
        self.tree.heading("data_ultimo_pedido", text="Data do Último Pedido", anchor="w")
        self.tree.heading("contato", text="Contato", anchor="w")
        
        self.tree.column("id", width=90, minwidth=80, anchor="w")
        self.tree.column("nome_cliente", width=180, minwidth=140, anchor="w")
        self.tree.column("endereco", width=280, minwidth=200, anchor="w")
        self.tree.column("data_ultimo_pedido", width=160, minwidth=130, anchor="w")
        self.tree.column("contato", width=180, minwidth=140, anchor="w")
        
        # Scrollbar vertical estilizada em rosa
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
            "Clientes.Treeview.Heading",
            background=sb_bg,
            foreground=br_title,
            font=("Segoe UI", 11, "bold"),
            rowheight=38,
            relief="flat"
        )
        style.map("Clientes.Treeview.Heading", background=[('active', in_hover)])
        
        style.configure(
            "Clientes.Treeview",
            background=card_bg,
            fieldbackground=card_bg,
            foreground=t_text,
            font=("Segoe UI", 11),
            rowheight=36,
            borderwidth=0
        )
        style.map(
            "Clientes.Treeview",
            background=[('selected', act_pill), ('focus', act_pill)],
            foreground=[('selected', '#FFFFFF'), ('focus', '#FFFFFF')]
        )

    def atualizar_tabela(self):
        """Carrega os dados do serviço e redesenha as linhas na tabela."""
        self.clientes_cache = self.service.carregar_clientes()
        self.renderizar_linhas(self.clientes_cache)

    def renderizar_linhas(self, lista_clientes):
        """Limpa a tabela e insere as linhas fornecidas."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for c in lista_clientes:
            self.tree.insert(
                "",
                "end",
                iid=c["id"],
                values=(
                    c.get("id", ""),
                    c.get("nome_cliente", "-"),
                    c.get("endereco", "-"),
                    c.get("data_ultimo_pedido", "-"),
                    c.get("contato", "-")
                )
            )

    def filtrar_clientes(self, event=None):
        """Filtra as linhas exibidas conforme a busca."""
        termo = self.entry_pesquisa.get().strip().lower()
        if not termo:
            self.renderizar_linhas(self.clientes_cache)
            return
            
        filtrados = [
            c for c in self.clientes_cache
            if termo in c.get("nome_cliente", "").lower()
            or termo in c.get("contato", "").lower()
            or termo in c.get("endereco", "").lower()
            or termo in c.get("id", "").lower()
        ]
        self.renderizar_linhas(filtrados)

    def acao_adicionar(self):
        """Abre o formulário modal para cadastrar um novo cliente."""
        def on_save(dados):
            self.service.adicionar_cliente(
                nome_cliente=dados["nome_cliente"],
                endereco=dados["endereco"],
                data_ultimo_pedido=dados["data_ultimo_pedido"],
                contato=dados["contato"]
            )
            self.atualizar_tabela()
            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!", parent=self)

        modal = ClienteFormModal(self, title="Adicionar Novo Cliente", on_save=on_save)

    def acao_editar(self):
        """Abre o formulário modal para editar o cliente selecionado."""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Seleção Necessária", "Por favor, selecione um cliente na tabela para editar.", parent=self)
            return
            
        cliente_id = selecionado[0]
        cliente_atual = next((c for c in self.clientes_cache if c["id"] == cliente_id), None)
        
        if not cliente_atual:
            return

        def on_save(dados):
            self.service.atualizar_cliente(
                cliente_id=cliente_id,
                nome_cliente=dados["nome_cliente"],
                endereco=dados["endereco"],
                data_ultimo_pedido=dados["data_ultimo_pedido"],
                contato=dados["contato"]
            )
            self.atualizar_tabela()
            messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!", parent=self)

        modal = ClienteFormModal(self, title=f"Editar Cliente {cliente_id}", cliente_data=cliente_atual, on_save=on_save)

    def acao_excluir(self):
        """Confirma e remove o cliente selecionado."""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Seleção Necessária", "Por favor, selecione um cliente na tabela para excluir.", parent=self)
            return
            
        cliente_id = selecionado[0]
        confirmar = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja remover o cliente {cliente_id}?", parent=self)
        if confirmar:
            if self.service.remover_cliente(cliente_id):
                self.atualizar_tabela()
                messagebox.showinfo("Sucesso", "Cliente removido com sucesso!", parent=self)
