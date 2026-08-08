import customtkinter as ctk
from tkinter import ttk, messagebox
from config.settings import PALETTE, get_color, centralizar_janela

class ClientePedidosModal(ctk.CTkToplevel):
    """Janela modal exibindo o histórico e pedidos em aberto de um determinado cliente."""
    
    def __init__(self, parent, cliente_data, pedidos_service, on_novo_pedido=None):
        super().__init__(parent)
        
        self.cliente_data = cliente_data
        self.pedidos_service = pedidos_service
        self.on_novo_pedido = on_novo_pedido
        
        nome_cliente = cliente_data.get("nome_cliente", "Cliente")
        
        self.title(f"Pedidos de {nome_cliente}")
        self.geometry("640x540")
        self.resizable(False, False)
        self.configure(fg_color=PALETTE["main_bg"])
        
        # Centralizar em relação à janela pai
        centralizar_janela(self, 640, 540, parent)
        self.transient(parent)
        self.grab_set()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 1. Cabeçalho da Modal
        header_frame = ctk.CTkFrame(self, fg_color=PALETTE["sidebar_bg"], height=85, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.pack_propagate(False)
        
        lbl_header = ctk.CTkLabel(
            header_frame,
            text=f"📋 Encomendas de {nome_cliente}",
            font=ctk.CTkFont(family="Georgia", size=20, weight="bold"),
            text_color=PALETTE["brand_title"]
        )
        lbl_header.pack(anchor="w", padx=24, pady=(16, 2))
        
        contato = cliente_data.get("contato", "-")
        endereco = cliente_data.get("endereco", "-")
        lbl_sub = ctk.CTkLabel(
            header_frame,
            text=f"Contato: {contato} | Endereço: {endereco}",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=PALETTE["subtitle_text"]
        )
        lbl_sub.pack(anchor="w", padx=24)
        
        # 2. Container da Tabela de Pedidos
        body_frame = ctk.CTkFrame(self, fg_color="transparent")
        body_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
        body_frame.grid_columnconfigure(0, weight=1)
        body_frame.grid_rowconfigure(0, weight=1)
        
        self.criar_tabela_pedidos(body_frame)
        
        # 3. Rodapé com resumo e botões de ação
        footer_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 16))
        footer_frame.grid_columnconfigure(0, weight=1)
        
        self.lbl_resumo_total = ctk.CTkLabel(
            footer_frame,
            text="Total em Pedidos: R$ 0,00",
            font=ctk.CTkFont(family="Georgia", size=15, weight="bold"),
            text_color=PALETTE["brand_title"]
        )
        self.lbl_resumo_total.pack(side="left", padx=4)
        
        actions_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        actions_frame.pack(side="right")
        
        btn_fechar = ctk.CTkButton(
            actions_frame,
            text="Fechar",
            height=38,
            corner_radius=10,
            fg_color="transparent",
            border_color=PALETTE["sidebar_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(weight="bold"),
            command=self.destroy
        )
        btn_fechar.pack(side="left", padx=(0, 8))
        
        btn_novo_ped = ctk.CTkButton(
            actions_frame,
            text="+ Novo Pedido para este Cliente",
            height=38,
            corner_radius=10,
            fg_color=PALETTE["active_pill"],
            hover_color=PALETTE["active_pill_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(weight="bold"),
            command=self.criar_novo_pedido
        )
        btn_novo_ped.pack(side="left")

        # Carregar dados dos pedidos do cliente
        self.carregar_pedidos_cliente()

    def criar_tabela_pedidos(self, container):
        """Cria e estiliza a tabela Treeview para listar os pedidos do cliente."""
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
            "ClientePedidos.Treeview.Heading",
            background=sb_bg,
            foreground=br_title,
            font=("Segoe UI", 10, "bold"),
            rowheight=34,
            relief="flat"
        )
        style.map("ClientePedidos.Treeview.Heading", background=[('active', in_hover)])
        
        style.configure(
            "ClientePedidos.Treeview",
            background=card_bg,
            fieldbackground=card_bg,
            foreground=t_text,
            font=("Segoe UI", 10),
            rowheight=32,
            borderwidth=0
        )
        style.map(
            "ClientePedidos.Treeview",
            background=[('selected', act_pill), ('focus', act_pill)],
            foreground=[('selected', '#FFFFFF'), ('focus', '#FFFFFF')]
        )
        
        colunas = ("id", "data_pedido", "produto", "valor", "data_entrega")
        
        self.tree = ttk.Treeview(
            container,
            columns=colunas,
            show="headings",
            style="ClientePedidos.Treeview",
            selectmode="browse"
        )
        
        self.tree.heading("id", text="ID Pedido", anchor="w")
        self.tree.heading("data_pedido", text="Data Pedido", anchor="w")
        self.tree.heading("produto", text="Produto / Encomenda", anchor="w")
        self.tree.heading("valor", text="Valor", anchor="w")
        self.tree.heading("data_entrega", text="Data Entrega", anchor="w")
        
        self.tree.column("id", width=80, minwidth=70, anchor="w")
        self.tree.column("data_pedido", width=100, minwidth=90, anchor="w")
        self.tree.column("produto", width=220, minwidth=150, anchor="w")
        self.tree.column("valor", width=100, minwidth=90, anchor="w")
        self.tree.column("data_entrega", width=100, minwidth=90, anchor="w")
        
        scrollbar = ctk.CTkScrollbar(
            container,
            orientation="vertical",
            command=self.tree.yview,
            button_color=PALETTE["active_pill"],
            button_hover_color=PALETTE["active_pill_hover"]
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def carregar_pedidos_cliente(self):
        """Carrega e filtra todos os pedidos vinculados a este cliente."""
        todos_pedidos = self.pedidos_service.carregar_pedidos()
        nome_alvo = self.cliente_data.get("nome_cliente", "").strip().lower()
        id_alvo = self.cliente_data.get("id", "").strip().lower()
        
        pedidos_cliente = [
            p for p in todos_pedidos
            if p.get("nome_cliente", "").strip().lower() == nome_alvo
            or p.get("cliente_id", "").strip().lower() == id_alvo
        ]
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        total_acumulado = 0.0
        
        for p in pedidos_cliente:
            try:
                val_num = float(p.get("valor_produto", 0))
            except (ValueError, TypeError):
                val_num = 0.0
            total_acumulado += val_num
            
            val_str = f"R$ {val_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            self.tree.insert(
                "",
                "end",
                iid=p["id"],
                values=(
                    p.get("id", ""),
                    p.get("data_pedido", "-"),
                    p.get("produto", "-"),
                    val_str,
                    p.get("data_entrega", "-")
                )
            )
            
        fmt_total = f"R$ {total_acumulado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.lbl_resumo_total.configure(text=f"Total ({len(pedidos_cliente)} pedidos): {fmt_total}")

    def criar_novo_pedido(self):
        """Dispara a criação de um novo pedido especificamente para este cliente."""
        self.destroy()
        if self.on_novo_pedido:
            self.on_novo_pedido(self.cliente_data)
