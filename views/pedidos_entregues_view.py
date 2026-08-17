import os
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from config.settings import PALETTE, get_color
from services.pedidos_service import PedidosService

class PedidosEntreguesView(ctk.CTkFrame):
    """Módulo completo de Visualização de Pedidos Entregues com Busca, Navegação Mensal e Relatórios PDF."""
    
    def __init__(self, master, base_dir=None, **kwargs):
        super().__init__(master, fg_color=PALETTE["main_bg"], corner_radius=0, **kwargs)
        
        self.base_dir = base_dir
        self.service = PedidosService(base_dir=base_dir)
        self.pedidos_cache = []
        
        # Estado de controle de mês/ano
        self.hoje = datetime.now()
        self.mes_atual = self.hoje.month
        self.ano_atual = self.hoje.year
        self.mes_selecionado = self.mes_atual
        self.ano_selecionado = self.ano_atual
        
        self.MESES = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # 1. Cabeçalho do Módulo
        self.criar_cabecalho()
        
        # 2. Barra de Ferramentas (Pesquisa e Botões de Ação)
        self.criar_barra_ferramentas()
        
        # 3. Tabela de Pedidos (Treeview Estilizado)
        self.criar_tabela_pedidos()
        
        # Carregar dados iniciais
        self.atualizar_tabela()

    def criar_cabecalho(self):
        """Cria o cabeçalho superior do módulo de pedidos entregues."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(28, 6))
        header_frame.grid_columnconfigure(0, weight=1)
        
        lbl_title = ctk.CTkLabel(
            header_frame,
            text="Pedidos Entregues",
            font=ctk.CTkFont(family="Georgia", size=28, weight="bold"),
            text_color=PALETTE["title_text"],
            anchor="w"
        )
        lbl_title.pack(anchor="w")
        
        lbl_sub = ctk.CTkLabel(
            header_frame,
            text="Consulte o histórico de encomendas entregues e gere relatórios de faturamento consolidado.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=PALETTE["subtitle_text"],
            anchor="w"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

    def criar_barra_ferramentas(self):
        """Cria os controles de busca, navegação de meses e botões de Ação."""
        tools_frame = ctk.CTkFrame(self, fg_color="transparent")
        tools_frame.grid(row=1, column=0, sticky="ew", padx=40, pady=(16, 16))
        tools_frame.grid_columnconfigure(0, weight=1)
        tools_frame.grid_columnconfigure(1, weight=0)
        tools_frame.grid_columnconfigure(2, weight=0)
        
        # Campo de Pesquisa
        self.entry_pesquisa = ctk.CTkEntry(
            tools_frame,
            placeholder_text="🔍 Pesquisar por cliente ou produto entregue...",
            height=42,
            corner_radius=12,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=13)
        )
        self.entry_pesquisa.grid(row=0, column=0, sticky="ew", padx=(0, 16))
        self.entry_pesquisa.bind("<KeyRelease>", self.filtrar_pedidos)
        
        # Container de Navegação de Meses
        month_nav_frame = ctk.CTkFrame(tools_frame, fg_color="transparent")
        month_nav_frame.grid(row=0, column=1, padx=(0, 16), sticky="w")
        
        # Botão Anterior
        self.btn_mes_anterior = ctk.CTkButton(
            month_nav_frame,
            text="◀",
            width=36,
            height=42,
            corner_radius=12,
            fg_color="transparent",
            border_color=PALETTE["card_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.mes_anterior
        )
        self.btn_mes_anterior.pack(side="left", padx=2)
        
        # Label do Mês Selecionado
        self.lbl_mes_selecionado = ctk.CTkLabel(
            month_nav_frame,
            text="",
            height=42,
            width=140,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=PALETTE["title_text"],
            fg_color="transparent"
        )
        self.lbl_mes_selecionado.pack(side="left", padx=4)
        
        # Botão Próximo
        self.btn_mes_proximo = ctk.CTkButton(
            month_nav_frame,
            text="▶",
            width=36,
            height=42,
            corner_radius=12,
            fg_color="transparent",
            border_color=PALETTE["card_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.mes_proximo
        )
        self.btn_mes_proximo.pack(side="left", padx=2)
        
        # Inicializar a exibição da label de mês
        self.atualizar_label_mes()
        
        # Container de Botões
        actions_frame = ctk.CTkFrame(tools_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=2, sticky="e")
        
        # Botão Reverter
        btn_reverter = ctk.CTkButton(
            actions_frame,
            text="↩️ Reverter",
            height=42,
            corner_radius=12,
            fg_color="transparent",
            border_color=PALETTE["card_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.acao_reverter_entrega
        )
        btn_reverter.pack(side="left", padx=4)
        
        # Botão Gerar Relatório
        self.btn_relatorio = ctk.CTkButton(
            actions_frame,
            text="📊 Gerar Relatório",
            height=42,
            corner_radius=12,
            fg_color=PALETTE["active_pill"],
            hover_color=PALETTE["active_pill_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.acao_gerar_relatorio
        )
        self.btn_relatorio.pack(side="left", padx=(4, 0))

    def criar_tabela_pedidos(self):
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
        
        self.atualizar_estilo_tema()
        
        colunas = ("id", "data_pedido", "nome_cliente", "produto", "valor_produto", "data_entrega")
        
        self.tree = ttk.Treeview(
            table_container,
            columns=colunas,
            show="headings",
            style="PedidosEntregues.Treeview",
            selectmode="browse"
        )
        
        self.tree.heading("id", text="ID Pedido", anchor="w")
        self.tree.heading("data_pedido", text="Data do Pedido", anchor="w")
        self.tree.heading("nome_cliente", text="Nome do Cliente", anchor="w")
        self.tree.heading("produto", text="Produto", anchor="w")
        self.tree.heading("valor_produto", text="Valor do Produto", anchor="w")
        self.tree.heading("data_entrega", text="Data de Entrega", anchor="w")
        
        self.tree.column("id", width=90, minwidth=80, anchor="w")
        self.tree.column("data_pedido", width=120, minwidth=100, anchor="w")
        self.tree.column("nome_cliente", width=200, minwidth=140, anchor="w")
        self.tree.column("produto", width=250, minwidth=180, anchor="w")
        self.tree.column("valor_produto", width=140, minwidth=110, anchor="w")
        self.tree.column("data_entrega", width=130, minwidth=110, anchor="w")
        
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
            "PedidosEntregues.Treeview.Heading",
            background=sb_bg,
            foreground=br_title,
            font=("Segoe UI", 11, "bold"),
            rowheight=38,
            relief="flat"
        )
        style.map("PedidosEntregues.Treeview.Heading", background=[('active', in_hover)])
        
        style.configure(
            "PedidosEntregues.Treeview",
            background=card_bg,
            fieldbackground=card_bg,
            foreground=t_text,
            font=("Segoe UI", 11),
            rowheight=36,
            borderwidth=0
        )
        style.map(
            "PedidosEntregues.Treeview",
            background=[('selected', act_pill), ('focus', act_pill)],
            foreground=[('selected', '#FFFFFF'), ('focus', '#FFFFFF')]
        )

    def mes_anterior(self):
        if self.mes_selecionado == 1:
            self.mes_selecionado = 12
            self.ano_selecionado -= 1
        else:
            self.mes_selecionado -= 1
        self.atualizar_label_mes()
        self.atualizar_tabela()

    def mes_proximo(self):
        if self.mes_selecionado == 12:
            self.mes_selecionado = 1
            self.ano_selecionado += 1
        else:
            self.mes_selecionado += 1
        self.atualizar_label_mes()
        self.atualizar_tabela()

    def atualizar_label_mes(self):
        mes_nome = self.MESES[self.mes_selecionado - 1]
        self.lbl_mes_selecionado.configure(text=f"{mes_nome} {self.ano_selecionado}")

    def filtrar_por_mes_selecionado(self, lista_pedidos):
        filtrados = []
        for p in lista_pedidos:
            if p.get("entregue", False):
                data_str = p.get("data_pedido", "")
                try:
                    partes = data_str.split("/")
                    if len(partes) == 3:
                        mes_p = int(partes[1])
                        ano_p = int(partes[2])
                        if mes_p == self.mes_selecionado and ano_p == self.ano_selecionado:
                            filtrados.append(p)
                except (ValueError, IndexError):
                    pass
        return filtrados

    def atualizar_tabela(self):
        """Carrega os dados do serviço e redesenha as linhas na tabela."""
        self.pedidos_cache = self.service.carregar_pedidos()
        pedidos_filtrados = self.filtrar_por_mes_selecionado(self.pedidos_cache)
        self.renderizar_linhas(pedidos_filtrados)

    def renderizar_linhas(self, lista_pedidos):
        """Limpa a tabela e insere as linhas fornecidas."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for p in lista_pedidos:
            try:
                val_num = float(p.get("valor_produto", 0))
                val_str = f"R$ {val_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except (ValueError, TypeError):
                val_str = f"R$ {p.get('valor_produto', '0,00')}"
                
            self.tree.insert(
                "",
                "end",
                iid=p["id"],
                values=(
                    p.get("id", ""),
                    p.get("data_pedido", "-"),
                    p.get("nome_cliente", "-"),
                    p.get("produto", "-"),
                    val_str,
                    p.get("data_entrega", "-")
                )
            )

    def filtrar_pedidos(self, event=None):
        """Filtra as linhas exibidas conforme a busca e o mês selecionado."""
        termo = self.entry_pesquisa.get().strip().lower()
        pedidos_mes = self.filtrar_por_mes_selecionado(self.pedidos_cache)
        
        if not termo:
            self.renderizar_linhas(pedidos_mes)
            return
            
        filtrados = [
            p for p in pedidos_mes
            if termo in p.get("nome_cliente", "").lower()
            or termo in p.get("produto", "").lower()
            or termo in p.get("id", "").lower()
        ]
        self.renderizar_linhas(filtrados)

    def acao_reverter_entrega(self):
        """Reverte o pedido selecionado de entregue para pendente."""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Seleção Necessária", "Por favor, selecione um pedido para reverter.", parent=self)
            return
            
        pedido_id = selecionado[0]
        confirmar = messagebox.askyesno("Confirmar Reversão", f"Tem certeza que deseja reverter o pedido {pedido_id} para pendente?", parent=self)
        if confirmar:
            if self.service.reverter_entrega(pedido_id):
                self.atualizar_tabela()
                messagebox.showinfo("Sucesso", "Pedido movido de volta para pendentes!", parent=self)

    def acao_gerar_relatorio(self):
        """Gera um PDF contendo o relatório financeiro e o número de pedidos entregues."""
        pedidos_mes = self.filtrar_por_mes_selecionado(self.pedidos_cache)
        if not pedidos_mes:
            messagebox.showwarning("Sem Dados", "Não há pedidos entregues para exportar no mês selecionado.", parent=self)
            return

        colunas = ["ID Pedido", "Data Pedido", "Nome do Cliente", "Produto / Encomenda", "Valor (R$)", "Data Entrega"]
        linhas = []
        total_val = 0.0

        for p in pedidos_mes:
            try:
                val_num = float(p.get("valor_produto", 0))
            except (ValueError, TypeError):
                val_num = 0.0
            total_val += val_num

            val_str = f"R$ {val_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            linhas.append([
                p.get("id", ""),
                p.get("data_pedido", "-"),
                p.get("nome_cliente", "-"),
                p.get("produto", "-"),
                val_str,
                p.get("data_entrega", "-")
            ])

        mes_nome = self.MESES[self.mes_selecionado - 1]
        totais_info = {
            "Quantidade de Pedidos Entregues": len(linhas),
            "Faturamento Total Acumulado": f"R$ {total_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        }

        from services.pdf_service import PDFService
        PDFService.exportar_tabela_pdf(
            titulo_documento=f"Pedidos Entregues - {mes_nome} de {self.ano_selecionado}",
            colunas_titulos=colunas,
            dados_linhas=linhas,
            totais_info=totais_info,
            base_dir=self.base_dir,
            parent_window=self,
            orientacao_paisagem=True
        )
