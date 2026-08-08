import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from config.settings import PALETTE, get_color
from services.financeiro_service import FinanceiroService
from services.pdf_service import PDFService
from components.financeiro_form_modal import FinanceiroFormModal

class FinanceiroView(ctk.CTkFrame):
    """Módulo de Gestão Financeira com Lançamentos Mensais e Relatório Anual Consolidado."""
    
    def __init__(self, master, base_dir=None, **kwargs):
        super().__init__(master, fg_color=PALETTE["main_bg"], corner_radius=0, **kwargs)
        
        self.base_dir = base_dir
        self.service = FinanceiroService(base_dir=base_dir)
        self.lancamentos_cache = []
        
        # Mês e Ano padrão (mês/ano atual)
        hoje = datetime.now()
        self.mes_atual_idx = hoje.month - 1  # 0-indexed
        self.ano_atual_str = str(hoje.year)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 1. Cabeçalho do Módulo
        self.criar_cabecalho()
        
        # 2. Container de Abas (CTkTabview)
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=PALETTE["main_bg"],
            segmented_button_selected_color=PALETTE["active_pill"],
            segmented_button_selected_hover_color=PALETTE["active_pill_hover"],
            segmented_button_unselected_color=PALETTE["sidebar_bg"],
            segmented_button_unselected_hover_color=PALETTE["inactive_hover"],
            text_color=PALETTE["brand_title"]
        )
        self.tabview._segmented_button.configure(
            border_width=1,
            fg_color=PALETTE["card_border"],
            font=ctk.CTkFont(family="Georgia", size=14, weight="bold")
        )
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=40, pady=(0, 20))
        
        self.tab_mensal = self.tabview.add("📊 Lançamentos do Mês")
        self.tab_anual = self.tabview.add("📅 Relatório Anual Consolidado")
        
        # Construir as telas dentro de cada aba
        self.construir_aba_mensal(self.tab_mensal)
        self.construir_aba_anual(self.tab_anual)
        
        # Carregar dados iniciais
        self.atualizar_tabela_mensal()
        self.atualizar_relatorio_anual()

    def criar_cabecalho(self):
        """Cria o cabeçalho superior do módulo financeiro."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(24, 4))
        header_frame.grid_columnconfigure(0, weight=1)
        
        lbl_title = ctk.CTkLabel(
            header_frame,
            text="Gestão Financeira",
            font=ctk.CTkFont(family="Georgia", size=28, weight="bold"),
            text_color=PALETTE["title_text"],
            anchor="w"
        )
        lbl_title.pack(anchor="w")
        
        lbl_sub = ctk.CTkLabel(
            header_frame,
            text="Acompanhe receitas, despesas, saldo mensal e o relatório consolidado do ano.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=PALETTE["subtitle_text"],
            anchor="w"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

    # =========================================================================
    # ABA 1: LANÇAMENTOS DO MÊS (MODELO DA PLANILHA)
    # =========================================================================

    def construir_aba_mensal(self, tab):
        """Constrói a interface de Lançamentos Mensais com tabela, filtros e totais."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)
        
        # Toolbar (Seleção de Mês/Ano, Busca e Ações)
        tools_frame = ctk.CTkFrame(tab, fg_color="transparent")
        tools_frame.grid(row=0, column=0, sticky="ew", pady=(12, 12))
        tools_frame.grid_columnconfigure(2, weight=1)
        
        # Seleção de Mês
        ctk.CTkLabel(tools_frame, text="Mês:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=(0, 4))
        self.combo_mes = ctk.CTkOptionMenu(
            tools_frame,
            values=self.service.MESES_NOME,
            width=130,
            height=38,
            corner_radius=10,
            fg_color=PALETTE["card_bg"],
            button_color=PALETTE["active_pill"],
            button_hover_color=PALETTE["active_pill_hover"],
            text_color=PALETTE["title_text"],
            command=lambda e: self.atualizar_tabela_mensal()
        )
        self.combo_mes.grid(row=0, column=1, padx=(0, 14))
        self.combo_mes.set(self.service.MESES_NOME[self.mes_atual_idx])
        
        # Campo de Pesquisa
        self.entry_pesquisa_mensal = ctk.CTkEntry(
            tools_frame,
            placeholder_text="🔍 Pesquisar descrição, categoria ou pagamento...",
            height=38,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=13)
        )
        self.entry_pesquisa_mensal.grid(row=0, column=2, sticky="ew", padx=(0, 14))
        self.entry_pesquisa_mensal.bind("<KeyRelease>", self.filtrar_tabela_mensal)
        
        # Botões de Ação
        actions_frame = ctk.CTkFrame(tools_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=3, sticky="e")
        
        btn_excluir = ctk.CTkButton(
            actions_frame,
            text="🗑️ Excluir",
            height=38,
            corner_radius=10,
            fg_color="transparent",
            border_color="#E57373",
            border_width=1,
            text_color="#C62828",
            hover_color="#FFEBEE",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.acao_excluir_lancamento
        )
        btn_excluir.pack(side="left", padx=4)
        
        btn_editar = ctk.CTkButton(
            actions_frame,
            text="✏️ Editar",
            height=38,
            corner_radius=10,
            fg_color="transparent",
            border_color=PALETTE["card_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.acao_editar_lancamento
        )
        btn_editar.pack(side="left", padx=4)
        
        btn_pdf_mensal = ctk.CTkButton(
            actions_frame,
            text="📄 PDF",
            height=38,
            corner_radius=10,
            fg_color="transparent",
            border_color=PALETTE["card_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.acao_exportar_pdf_mensal
        )
        btn_pdf_mensal.pack(side="left", padx=4)

        btn_novo = ctk.CTkButton(
            actions_frame,
            text="+ Novo Lançamento",
            height=38,
            corner_radius=10,
            fg_color=PALETTE["active_pill"],
            hover_color=PALETTE["active_pill_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.acao_adicionar_lancamento
        )
        btn_novo.pack(side="left", padx=(4, 0))

        # Tabela Treeview dos Lançamentos do Mês
        table_container = ctk.CTkFrame(
            tab,
            fg_color=PALETTE["card_bg"],
            border_color=PALETTE["card_border"],
            border_width=1,
            corner_radius=16
        )
        table_container.grid(row=2, column=0, sticky="nsew", pady=(0, 12))
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)
        
        colunas = ("data", "descricao", "categoria", "entrada", "saida", "forma_pagamento")
        
        self.atualizar_estilo_tema_ttk()
        
        self.tree_mensal = ttk.Treeview(
            table_container,
            columns=colunas,
            show="headings",
            style="Financeiro.Treeview",
            selectmode="browse"
        )
        
        self.tree_mensal.heading("data", text="Data", anchor="w")
        self.tree_mensal.heading("descricao", text="Descrição", anchor="w")
        self.tree_mensal.heading("categoria", text="Categoria", anchor="w")
        self.tree_mensal.heading("entrada", text="Entrada (R$)", anchor="w")
        self.tree_mensal.heading("saida", text="Saída (R$)", anchor="w")
        self.tree_mensal.heading("forma_pagamento", text="Forma de Pagamento", anchor="w")
        
        self.tree_mensal.column("data", width=100, minwidth=85, anchor="w")
        self.tree_mensal.column("descricao", width=220, minwidth=150, anchor="w")
        self.tree_mensal.column("categoria", width=140, minwidth=110, anchor="w")
        self.tree_mensal.column("entrada", width=130, minwidth=100, anchor="w")
        self.tree_mensal.column("saida", width=130, minwidth=100, anchor="w")
        self.tree_mensal.column("forma_pagamento", width=160, minwidth=120, anchor="w")
        
        scrollbar = ctk.CTkScrollbar(
            table_container,
            orientation="vertical",
            command=self.tree_mensal.yview,
            button_color=PALETTE["active_pill"],
            button_hover_color=PALETTE["active_pill_hover"]
        )
        self.tree_mensal.configure(yscrollcommand=scrollbar.set)
        
        self.tree_mensal.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=16)
        
        self.tree_mensal.bind("<Double-1>", lambda e: self.acao_editar_lancamento())
        
        # Painel de Resumo / Totais do Mês (idêntico à planilha do usuário)
        panel_totais = ctk.CTkFrame(tab, fg_color=PALETTE["sidebar_bg"], border_color=PALETTE["sidebar_border"], border_width=1, corner_radius=14)
        panel_totais.grid(row=3, column=0, sticky="ew", pady=(0, 6))
        panel_totais.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Total Entradas
        f_ent = ctk.CTkFrame(panel_totais, fg_color="transparent")
        f_ent.grid(row=0, column=0, padx=16, pady=10, sticky="ew")
        ctk.CTkLabel(f_ent, text="Total Entradas:", font=ctk.CTkFont(size=12, weight="bold"), text_color=PALETTE["inactive_text"]).pack(anchor="w")
        self.lbl_tot_entradas = ctk.CTkLabel(f_ent, text="R$ 0,00", font=ctk.CTkFont(family="Georgia", size=16, weight="bold"), text_color="#2E7D32")
        self.lbl_tot_entradas.pack(anchor="w")
        
        # Total Saídas
        f_sai = ctk.CTkFrame(panel_totais, fg_color="transparent")
        f_sai.grid(row=0, column=1, padx=16, pady=10, sticky="ew")
        ctk.CTkLabel(f_sai, text="Total Saídas:", font=ctk.CTkFont(size=12, weight="bold"), text_color=PALETTE["inactive_text"]).pack(anchor="w")
        self.lbl_tot_saidas = ctk.CTkLabel(f_sai, text="R$ 0,00", font=ctk.CTkFont(family="Georgia", size=16, weight="bold"), text_color="#C62828")
        self.lbl_tot_saidas.pack(anchor="w")
        
        # Total do Mês (Saldo Líquido)
        f_sal = ctk.CTkFrame(panel_totais, fg_color="transparent")
        f_sal.grid(row=0, column=2, padx=16, pady=10, sticky="ew")
        ctk.CTkLabel(f_sal, text="Total do Mês (Saldo):", font=ctk.CTkFont(size=12, weight="bold"), text_color=PALETTE["inactive_text"]).pack(anchor="w")
        self.lbl_tot_saldo = ctk.CTkLabel(f_sal, text="R$ 0,00", font=ctk.CTkFont(family="Georgia", size=18, weight="bold"), text_color=PALETTE["brand_title"])
        self.lbl_tot_saldo.pack(anchor="w")

    def atualizar_tabela_mensal(self):
        """Carrega os lançamentos do mês selecionado e atualiza a tabela e os totais."""
        mes_nome = self.combo_mes.get()
        mes_idx = self.service.MESES_NOME.index(mes_nome) + 1 if mes_nome in self.service.MESES_NOME else 7
        ano_num = int(self.ano_atual_str)
        
        self.lancamentos_cache = self.service.obter_lancamentos_por_mes(mes_idx, ano_num)
        self.renderizar_linhas_mensal(self.lancamentos_cache)
        
        # Calcular totais
        totais = self.service.calcular_totais_mes(mes_idx, ano_num)
        
        ent_fmt = f"R$ {totais['total_entradas']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        sai_fmt = f"R$ {totais['total_saidas']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        sal_fmt = f"R$ {totais['saldo_mes']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        self.lbl_tot_entradas.configure(text=ent_fmt)
        self.lbl_tot_saidas.configure(text=sai_fmt)
        self.lbl_tot_saldo.configure(
            text=sal_fmt,
            text_color="#2E7D32" if totais['saldo_mes'] >= 0 else "#C62828"
        )
        
        # Atualizar também o relatório anual para manter sincronizado
        self.atualizar_relatorio_anual()

    def renderizar_linhas_mensal(self, lista):
        """Redesenha as linhas na tabela mensal."""
        for item in self.tree_mensal.get_children():
            self.tree_mensal.delete(item)
            
        for item in lista:
            ent = float(item.get("valor_entrada", 0))
            sai = float(item.get("valor_saida", 0))
            
            ent_str = f"R$ {ent:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if ent > 0 else "-"
            sai_str = f"R$ {sai:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if sai > 0 else "-"
            
            self.tree_mensal.insert(
                "",
                "end",
                iid=item["id"],
                values=(
                    item.get("data", "-"),
                    item.get("descricao", "-"),
                    item.get("categoria", "-"),
                    ent_str,
                    sai_str,
                    item.get("forma_pagamento", "-")
                )
            )

    def filtrar_tabela_mensal(self, event=None):
        """Filtra a tabela mensal conforme o texto digitado."""
        termo = self.entry_pesquisa_mensal.get().strip().lower()
        if not termo:
            self.renderizar_linhas_mensal(self.lancamentos_cache)
            return
            
        filtrados = [
            item for item in self.lancamentos_cache
            if termo in item.get("descricao", "").lower()
            or termo in item.get("categoria", "").lower()
            or termo in item.get("forma_pagamento", "").lower()
            or termo in item.get("data", "").lower()
        ]
        self.renderizar_linhas_mensal(filtrados)

    def acao_adicionar_lancamento(self):
        """Abre modal para adicionar novo lançamento financeiro."""
        def on_save(dados):
            self.service.adicionar_lancamento(
                tipo=dados["tipo"],
                data=dados["data"],
                descricao=dados["descricao"],
                categoria=dados["categoria"],
                valor=dados["valor"],
                forma_pagamento=dados["forma_pagamento"]
            )
            self.atualizar_tabela_mensal()
            messagebox.showinfo("Sucesso", "Lançamento adicionado com sucesso!", parent=self)

        modal = FinanceiroFormModal(self, title="Novo Lançamento Financial", on_save=on_save)

    def acao_editar_lancamento(self):
        """Abre modal para editar lançamento financeiro selecionado."""
        selecionado = self.tree_mensal.selection()
        if not selecionado:
            messagebox.showwarning("Seleção Necessária", "Por favor, selecione um lançamento na tabela para editar.", parent=self)
            return
            
        item_id = selecionado[0]
        item_atual = next((i for i in self.lancamentos_cache if i["id"] == item_id), None)
        
        if not item_atual:
            return

        def on_save(dados):
            self.service.atualizar_lancamento(
                item_id=item_id,
                tipo=dados["tipo"],
                data=dados["data"],
                descricao=dados["descricao"],
                categoria=dados["categoria"],
                valor=dados["valor"],
                forma_pagamento=dados["forma_pagamento"]
            )
            self.atualizar_tabela_mensal()
            messagebox.showinfo("Sucesso", "Lançamento atualizado com sucesso!", parent=self)

        modal = FinanceiroFormModal(self, title=f"Editar Lançamento {item_id}", item_data=item_atual, on_save=on_save)

    def acao_excluir_lancamento(self):
        """Exclui o lançamento financeiro selecionado."""
        selecionado = self.tree_mensal.selection()
        if not selecionado:
            messagebox.showwarning("Seleção Necessária", "Por favor, selecione um lançamento na tabela para excluir.", parent=self)
            return
            
        item_id = selecionado[0]
        confirmar = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja remover o lançamento {item_id}?", parent=self)
        if confirmar:
            if self.service.remover_lancamento(item_id):
                self.atualizar_tabela_mensal()
                messagebox.showinfo("Sucesso", "Lançamento removido com sucesso!", parent=self)

    # =========================================================================
    # ABA 2: RELATÓRIO ANUAL CONSOLIDADO
    # =========================================================================

    def construir_aba_anual(self, tab):
        """Constrói o relatório financeiro consolidado do ano com cards e tabela dos 12 meses."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)
        
        # 1. Cards de Resumo Anual
        cards_frame = ctk.CTkFrame(tab, fg_color="transparent")
        cards_frame.grid(row=0, column=0, sticky="ew", pady=(12, 16))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Card 1: Faturamento Anual (Entradas)
        c1 = ctk.CTkFrame(cards_frame, fg_color=PALETTE["card_bg"], border_color=PALETTE["card_border"], border_width=1, corner_radius=14)
        c1.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        ctk.CTkLabel(c1, text="📈 Faturamento Anual (Entradas)", font=ctk.CTkFont(size=12, weight="bold"), text_color=PALETTE["inactive_text"]).pack(anchor="w", padx=16, pady=(12, 2))
        self.lbl_card_anual_entradas = ctk.CTkLabel(c1, text="R$ 0,00", font=ctk.CTkFont(family="Georgia", size=20, weight="bold"), text_color="#2E7D32")
        self.lbl_card_anual_entradas.pack(anchor="w", padx=16, pady=(0, 12))
        
        # Card 2: Despesas Anuais (Saídas)
        c2 = ctk.CTkFrame(cards_frame, fg_color=PALETTE["card_bg"], border_color=PALETTE["card_border"], border_width=1, corner_radius=14)
        c2.grid(row=0, column=1, padx=4, sticky="ew")
        ctk.CTkLabel(c2, text="📉 Despesas Anuais (Saídas)", font=ctk.CTkFont(size=12, weight="bold"), text_color=PALETTE["inactive_text"]).pack(anchor="w", padx=16, pady=(12, 2))
        self.lbl_card_anual_saidas = ctk.CTkLabel(c2, text="R$ 0,00", font=ctk.CTkFont(family="Georgia", size=20, weight="bold"), text_color="#C62828")
        self.lbl_card_anual_saidas.pack(anchor="w", padx=16, pady=(0, 12))
        
        # Card 3: Lucro Líquido Anual
        c3 = ctk.CTkFrame(cards_frame, fg_color=PALETTE["sidebar_bg"], border_color=PALETTE["sidebar_border"], border_width=1, corner_radius=14)
        c3.grid(row=0, column=2, padx=(8, 0), sticky="ew")
        ctk.CTkLabel(c3, text="🏆 Lucro Líquido Anual", font=ctk.CTkFont(size=12, weight="bold"), text_color=PALETTE["inactive_text"]).pack(anchor="w", padx=16, pady=(12, 2))
        self.lbl_card_anual_lucro = ctk.CTkLabel(c3, text="R$ 0,00", font=ctk.CTkFont(family="Georgia", size=20, weight="bold"), text_color=PALETTE["brand_title"])
        self.lbl_card_anual_lucro.pack(anchor="w", padx=16, pady=(0, 12))

        # Toolbar do Relatório Anual
        tools_anual = ctk.CTkFrame(tab, fg_color="transparent")
        tools_anual.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        tools_anual.grid_columnconfigure(0, weight=1)

        btn_pdf_anual = ctk.CTkButton(
            tools_anual,
            text="📄 Exportar Relatório Anual em PDF",
            height=38,
            corner_radius=10,
            fg_color=PALETTE["active_pill"],
            hover_color=PALETTE["active_pill_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.acao_exportar_pdf_anual
        )
        btn_pdf_anual.pack(side="right")

        # 2. Tabela Consolidada dos 12 Meses
        table_container = ctk.CTkFrame(
            tab,
            fg_color=PALETTE["card_bg"],
            border_color=PALETTE["card_border"],
            border_width=1,
            corner_radius=16
        )
        table_container.grid(row=2, column=0, sticky="nsew", pady=(0, 12))
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)
        
        colunas = ("mes", "entradas", "saidas", "saldo", "status")
        
        self.tree_anual = ttk.Treeview(
            table_container,
            columns=colunas,
            show="headings",
            style="FinanceiroAnual.Treeview",
            selectmode="browse"
        )
        
        self.tree_anual.heading("mes", text="Mês", anchor="w")
        self.tree_anual.heading("entradas", text="Total Entradas (R$)", anchor="w")
        self.tree_anual.heading("saidas", text="Total Saídas (R$)", anchor="w")
        self.tree_anual.heading("saldo", text="Saldo Líquido (R$)", anchor="w")
        self.tree_anual.heading("status", text="Desempenho / Status", anchor="w")
        
        self.tree_anual.column("mes", width=140, minwidth=110, anchor="w")
        self.tree_anual.column("entradas", width=160, minwidth=120, anchor="w")
        self.tree_anual.column("saidas", width=160, minwidth=120, anchor="w")
        self.tree_anual.column("saldo", width=160, minwidth=120, anchor="w")
        self.tree_anual.column("status", width=180, minwidth=140, anchor="w")
        
        scrollbar = ctk.CTkScrollbar(
            table_container,
            orientation="vertical",
            command=self.tree_anual.yview,
            button_color=PALETTE["active_pill"],
            button_hover_color=PALETTE["active_pill_hover"]
        )
        self.tree_anual.configure(yscrollcommand=scrollbar.set)
        
        self.tree_anual.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=16)

    def atualizar_relatorio_anual(self):
        """Atualiza a exibição consolidada dos 12 meses e dos cards do ano."""
        ano_num = int(self.ano_atual_str)
        rel_dados = self.service.obter_relatorio_anual(ano_num)
        
        ent_fmt = f"R$ {rel_dados['total_entradas']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        sai_fmt = f"R$ {rel_dados['total_saidas']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        luc_fmt = f"R$ {rel_dados['lucro_liquido']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        self.lbl_card_anual_entradas.configure(text=ent_fmt)
        self.lbl_card_anual_saidas.configure(text=sai_fmt)
        self.lbl_card_anual_lucro.configure(
            text=luc_fmt,
            text_color="#2E7D32" if rel_dados['lucro_liquido'] >= 0 else "#C62828"
        )
        
        for item in self.tree_anual.get_children():
            self.tree_anual.delete(item)
            
        for m in rel_dados["meses"]:
            ent = m["entradas"]
            sai = m["saidas"]
            sal = m["saldo"]
            
            ent_str = f"R$ {ent:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if ent > 0 else "-"
            sai_str = f"R$ {sai:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if sai > 0 else "-"
            sal_str = f"R$ {sal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if (ent > 0 or sai > 0) else "-"
            
            status = "Sem Movimento"
            if ent > 0 or sai > 0:
                status = "🟢 Lucro" if sal >= 0 else "🔴 Prejuízo"
                
            self.tree_anual.insert(
                "",
                "end",
                iid=f"MES-{m['mes_num']}",
                values=(
                    m["mes_nome"],
                    ent_str,
                    sai_str,
                    sal_str,
                    status
                )
            )

    def atualizar_estilo_tema_ttk(self, modo=None):
        """Atualiza o estilo visual das tabelas TTK de acordo com o tema."""
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
        
        for s_name in ["Financeiro.Treeview", "FinanceiroAnual.Treeview"]:
            style.configure(
                f"{s_name}.Heading",
                background=sb_bg,
                foreground=br_title,
                font=("Segoe UI", 11, "bold"),
                rowheight=38,
                relief="flat"
            )
            style.map(f"{s_name}.Heading", background=[('active', in_hover)])
            
            style.configure(
                s_name,
                background=card_bg,
                fieldbackground=card_bg,
                foreground=t_text,
                font=("Segoe UI", 11),
                rowheight=36,
                borderwidth=0
            )
            style.map(
                s_name,
                background=[('selected', act_pill), ('focus', act_pill)],
                foreground=[('selected', '#FFFFFF'), ('focus', '#FFFFFF')]
            )

    def atualizar_estilo_tema(self, modo=None):
        """Método público chamado ao alternar o tema do sistema."""
        self.atualizar_estilo_tema_ttk(modo)

    def acao_exportar_pdf_mensal(self):
        """Exporta os lançamentos do mês exibidos na tabela para PDF."""
        if not self.lancamentos_cache:
            messagebox.showwarning("Sem Dados", "Não há lançamentos financeiros para exportar no mês selecionado.", parent=self)
            return

        mes_nome = self.combo_mes.get()
        colunas = ["Data", "Descrição", "Categoria", "Entrada (R$)", "Saída (R$)", "Forma de Pagamento"]
        linhas = []

        mes_idx = self.service.MESES_NOME.index(mes_nome) + 1 if mes_nome in self.service.MESES_NOME else 7
        totais = self.service.calcular_totais_mes(mes_idx, int(self.ano_atual_str))

        for item in self.lancamentos_cache:
            ent = float(item.get("valor_entrada", 0))
            sai = float(item.get("valor_saida", 0))
            ent_str = f"R$ {ent:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if ent > 0 else "-"
            sai_str = f"R$ {sai:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if sai > 0 else "-"

            linhas.append([
                item.get("data", "-"),
                item.get("descricao", "-"),
                item.get("categoria", "-"),
                ent_str,
                sai_str,
                item.get("forma_pagamento", "-")
            ])

        totais_info = {
            "Total de Entradas": f"R$ {totais['total_entradas']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Total de Saídas": f"R$ {totais['total_saidas']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Saldo Líquido do Mês": f"R$ {totais['saldo_mes']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        }

        PDFService.exportar_tabela_pdf(
            titulo_documento=f"Lancamentos_Financeiros_{mes_nome}_{self.ano_atual_str}",
            colunas_titulos=colunas,
            dados_linhas=linhas,
            totais_info=totais_info,
            base_dir=self.base_dir,
            parent_window=self,
            orientacao_paisagem=True
        )

    def acao_exportar_pdf_anual(self):
        """Exporta o relatório consolidado dos 12 meses para PDF."""
        ano_num = int(self.ano_atual_str)
        rel_dados = self.service.obter_relatorio_anual(ano_num)

        colunas = ["Mês", "Total Entradas (R$)", "Total Saídas (R$)", "Saldo Líquido (R$)", "Desempenho"]
        linhas = []

        for m in rel_dados["meses"]:
            ent = m["entradas"]
            sai = m["saidas"]
            sal = m["saldo"]
            ent_str = f"R$ {ent:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if ent > 0 else "-"
            sai_str = f"R$ {sai:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if sai > 0 else "-"
            sal_str = f"R$ {sal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if (ent > 0 or sai > 0) else "-"

            status = "Sem Movimento"
            if ent > 0 or sai > 0:
                status = "Lucro" if sal >= 0 else "Prejuízo"

            linhas.append([
                m["mes_nome"],
                ent_str,
                sai_str,
                sal_str,
                status
            ])

        totais_info = {
            "Faturamento Anual (Total Entradas)": f"R$ {rel_dados['total_entradas']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Despesas Anuais (Total Saídas)": f"R$ {rel_dados['total_saidas']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Lucro Líquido Anual": f"R$ {rel_dados['lucro_liquido']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        }

        PDFService.exportar_tabela_pdf(
            titulo_documento=f"Relatorio_Financeiro_Anual_{ano_num}",
            colunas_titulos=colunas,
            dados_linhas=linhas,
            totais_info=totais_info,
            base_dir=self.base_dir,
            parent_window=self,
            orientacao_paisagem=True
        )
