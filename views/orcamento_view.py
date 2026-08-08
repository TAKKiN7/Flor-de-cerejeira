import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from config.settings import PALETTE
from services.clientes_service import ClientesService
from services.estoque_service import EstoqueService
from services.pdf_service import PDFService
from components.cliente_form_modal import ClienteFormModal

class OrcamentoView(ctk.CTkFrame):
    """Módulo para elaboração de Orçamentos e geração de PDF de Proposta Comercial sem salvar como pedido permanente."""
    
    def __init__(self, master, base_dir=None, **kwargs):
        super().__init__(master, fg_color=PALETTE["main_bg"], corner_radius=0, **kwargs)
        
        self.base_dir = base_dir
        self.clientes_service = ClientesService(base_dir=base_dir)
        self.estoque_service = EstoqueService(base_dir=base_dir)
        
        self.todos_clientes = []
        self.itens_usados = []
        self.valor_total_calculado = 0.0
        
        # Carregar materiais do estoque
        self.estoque_lista = self.estoque_service.carregar_estoque()
        self.mapa_estoque = {f"{item['nome']} (Estoque: {item['quantidade']} {item['unidade']} | R$ {item['preco_unitario']:.2f})": item for item in self.estoque_lista}
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 1. Cabeçalho do Módulo
        self.criar_cabecalho()
        
        # 2. Container Principal (Scrollable)
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=PALETTE["active_pill"],
            scrollbar_button_hover_color=PALETTE["active_pill_hover"]
        )
        scroll_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=(0, 20))
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Card Container do Formulário
        card_form = ctk.CTkFrame(
            scroll_frame,
            fg_color=PALETTE["card_bg"],
            border_color=PALETTE["card_border"],
            border_width=1,
            corner_radius=16
        )
        card_form.pack(fill="x", pady=10)
        card_form.grid_columnconfigure(0, weight=1)
        
        form_inner = ctk.CTkFrame(card_form, fg_color="transparent")
        form_inner.pack(fill="x", padx=24, pady=20)
        form_inner.grid_columnconfigure(0, weight=1)

        # Campo 1: Seleção / Busca de Cliente
        ctk.CTkLabel(
            form_inner,
            text="Cliente (Busca Inteligente por Nome ou Contato)",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        row_cli = ctk.CTkFrame(form_inner, fg_color="transparent")
        row_cli.pack(fill="x", pady=(0, 14))
        row_cli.grid_columnconfigure(0, weight=1)
        
        self.combo_cliente = ctk.CTkComboBox(
            row_cli,
            values=["(Nenhum cliente cadastrado)"],
            height=38,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            fg_color=PALETTE["sidebar_bg"],
            button_color=PALETTE["active_pill"],
            button_hover_color=PALETTE["active_pill_hover"],
            text_color=PALETTE["title_text"],
            font=ctk.CTkFont(size=13),
            dropdown_font=ctk.CTkFont(size=12)
        )
        self.combo_cliente.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.combo_cliente.bind("<KeyRelease>", self.filtrar_clientes_combo)
        
        btn_add_cli = ctk.CTkButton(
            row_cli,
            text="+ Novo Cliente",
            height=38,
            corner_radius=10,
            fg_color="transparent",
            border_color=PALETTE["active_pill"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.cadastrar_cliente_rapido
        )
        btn_add_cli.grid(row=0, column=1, sticky="e")
        
        self.carregar_opcoes_clientes()

        # Campo 2: Data de Emissão e Produto / Encomenda
        row_detalhes = ctk.CTkFrame(form_inner, fg_color="transparent")
        row_detalhes.pack(fill="x", pady=(0, 14))
        row_detalhes.grid_columnconfigure(1, weight=1)
        
        # Data Emissão
        col_dt = ctk.CTkFrame(row_detalhes, fg_color="transparent")
        col_dt.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkLabel(col_dt, text="Data de Emissão", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=PALETTE["inactive_text"]).pack(anchor="w", pady=(0, 4))
        
        self.entry_data_emissao = ctk.CTkEntry(col_dt, width=150, height=38, corner_radius=10, border_color=PALETTE["card_border"], font=ctk.CTkFont(size=13))
        self.entry_data_emissao.pack(fill="x")
        self.entry_data_emissao.insert(0, datetime.now().strftime("%d/%m/%Y"))

        # Descrição Encomenda
        col_prod = ctk.CTkFrame(row_detalhes, fg_color="transparent")
        col_prod.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ctk.CTkLabel(col_prod, text="Descrição do Produto / Encomenda", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=PALETTE["inactive_text"]).pack(anchor="w", pady=(0, 4))
        
        self.entry_produto = ctk.CTkEntry(col_prod, placeholder_text="Ex: Bordado Personalizado 20cm em Bastidor de Madeira", height=38, corner_radius=10, border_color=PALETTE["card_border"], font=ctk.CTkFont(size=13))
        self.entry_produto.pack(fill="x")

        # --- SEÇÃO DE SIMULAÇÃO DE ESTOQUE E CÁLCULO ---
        ctk.CTkFrame(form_inner, height=1, fg_color=PALETTE["card_border"]).pack(fill="x", pady=12)
        
        ctk.CTkLabel(
            form_inner,
            text="📦 Simulação de Materiais do Estoque (Cálculo de Margem)",
            font=ctk.CTkFont(family="Georgia", size=15, weight="bold"),
            text_color=PALETTE["brand_title"]
        ).pack(anchor="w", pady=(0, 8))
        
        panel_add_mat = ctk.CTkFrame(form_inner, fg_color=PALETTE["sidebar_bg"], border_color=PALETTE["sidebar_border"], border_width=1, corner_radius=12)
        panel_add_mat.pack(fill="x", pady=(0, 10))
        
        opcoes_estoque = list(self.mapa_estoque.keys()) if self.mapa_estoque else ["(Nenhum material no estoque)"]
        
        self.combo_materiais = ctk.CTkOptionMenu(
            panel_add_mat,
            values=opcoes_estoque,
            height=38,
            corner_radius=8,
            fg_color=PALETTE["card_bg"],
            button_color=PALETTE["active_pill"],
            button_hover_color=PALETTE["active_pill_hover"],
            text_color=PALETTE["title_text"],
            font=ctk.CTkFont(size=12)
        )
        self.combo_materiais.pack(fill="x", padx=12, pady=(10, 8))
        if opcoes_estoque:
            self.combo_materiais.set(opcoes_estoque[0])
            
        row_qtd = ctk.CTkFrame(panel_add_mat, fg_color="transparent")
        row_qtd.pack(fill="x", padx=12, pady=(0, 10))
        
        self.entry_qtd_usada = ctk.CTkEntry(
            row_qtd,
            placeholder_text="Qtd. usada (ex: 1)",
            height=36,
            corner_radius=8,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=12)
        )
        self.entry_qtd_usada.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        btn_add_mat = ctk.CTkButton(
            row_qtd,
            text="+ Adicionar Item",
            height=36,
            corner_radius=8,
            fg_color=PALETTE["active_pill"],
            hover_color=PALETTE["active_pill_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.adicionar_material_lista
        )
        btn_add_mat.pack(side="right")

        self.frame_lista_materiais = ctk.CTkFrame(form_inner, fg_color="transparent")
        self.frame_lista_materiais.pack(fill="x", pady=(0, 12))
        
        # --- PAINEL DE VALOR FINAL E MARGEM ---
        panel_valor = ctk.CTkFrame(form_inner, fg_color=PALETTE["sidebar_bg"], border_color=PALETTE["sidebar_border"], border_width=1, corner_radius=12)
        panel_valor.pack(fill="x", pady=(0, 16))
        
        # Custo Materiais
        r1 = ctk.CTkFrame(panel_valor, fg_color="transparent")
        r1.pack(fill="x", padx=16, pady=(10, 2))
        ctk.CTkLabel(r1, text="Custo dos Materiais:", font=ctk.CTkFont(size=12), text_color=PALETTE["subtitle_text"]).pack(side="left")
        self.lbl_custo_mat_val = ctk.CTkLabel(r1, text="R$ 0,00", font=ctk.CTkFont(size=12, weight="bold"), text_color=PALETTE["inactive_text"])
        self.lbl_custo_mat_val.pack(side="right")
        
        # Margem
        r2 = ctk.CTkFrame(panel_valor, fg_color="transparent")
        r2.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(r2, text="Fórmula de Margem do Atelier: Custo / (1 - 25%)", font=ctk.CTkFont(size=11, slant="italic"), text_color=PALETTE["subtitle_text"]).pack(side="left")
        
        ctk.CTkFrame(panel_valor, height=1, fg_color=PALETTE["card_border"]).pack(fill="x", padx=16, pady=4)

        # Valor do Orçamento (Editável se o usuário preferir)
        r3 = ctk.CTkFrame(panel_valor, fg_color="transparent")
        r3.pack(fill="x", padx=16, pady=(2, 10))
        ctk.CTkLabel(r3, text="Valor Final do Orçamento (R$):", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=PALETTE["title_text"]).pack(side="left")
        
        self.entry_valor_final = ctk.CTkEntry(
            r3,
            placeholder_text="Ex: 250.00",
            width=150,
            height=38,
            corner_radius=8,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(family="Georgia", size=16, weight="bold"),
            text_color=PALETTE["brand_title"]
        )
        self.entry_valor_final.pack(side="right")
        
        self.renderizar_materiais_usados()

        # --- BOTÕES INFERIORES DE AÇÃO ---
        row_actions = ctk.CTkFrame(form_inner, fg_color="transparent")
        row_actions.pack(fill="x", pady=(10, 4))
        row_actions.grid_columnconfigure((0, 1), weight=1)
        
        btn_limpar = ctk.CTkButton(
            row_actions,
            text="🧹 Limpar Formulário",
            height=44,
            corner_radius=10,
            fg_color="transparent",
            border_color=PALETTE["card_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(weight="bold"),
            command=self.limpar_formulario
        )
        btn_limpar.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        btn_gerar_pdf = ctk.CTkButton(
            row_actions,
            text="📄 Gerar PDF de Orçamento",
            height=44,
            corner_radius=10,
            fg_color=PALETTE["active_pill"],
            hover_color=PALETTE["active_pill_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.acao_gerar_pdf
        )
        btn_gerar_pdf.grid(row=0, column=1, padx=(8, 0), sticky="ew")

    def criar_cabecalho(self):
        """Cria o cabeçalho superior do módulo de Orçamento."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(24, 8))
        header_frame.grid_columnconfigure(0, weight=1)
        
        lbl_title = ctk.CTkLabel(
            header_frame,
            text="Elaboração de Orçamento",
            font=ctk.CTkFont(family="Georgia", size=28, weight="bold"),
            text_color=PALETTE["title_text"],
            anchor="w"
        )
        lbl_title.pack(anchor="w")
        
        lbl_sub = ctk.CTkLabel(
            header_frame,
            text="Preencha os dados da proposta comercial para gerar o PDF personalizado (o orçamento não fica salvo como pedido permanente).",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=PALETTE["subtitle_text"],
            anchor="w"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

    def carregar_opcoes_clientes(self, selecionar_novo=None):
        """Carrega os clientes cadastrados no ComboBox de busca de orçamento."""
        self.todos_clientes = self.clientes_service.carregar_clientes()
        if not self.todos_clientes:
            self.combo_cliente.configure(values=["(Nenhum cliente cadastrado)"])
            self.combo_cliente.set("(Nenhum cliente cadastrado)")
            return

        nomes = [c["nome_cliente"] for c in self.todos_clientes]
        self.combo_cliente.configure(values=nomes)
        
        if selecionar_novo and selecionar_novo in nomes:
            self.combo_cliente.set(selecionar_novo)
        else:
            self.combo_cliente.set(nomes[0])

    def filtrar_clientes_combo(self, event=None):
        """Filtra dinamicamente as opções do ComboBox enquanto o usuário digita."""
        termo = self.combo_cliente.get().strip().lower()
        if not hasattr(self, "todos_clientes") or not self.todos_clientes:
            return

        if not termo:
            nomes = [c["nome_cliente"] for c in self.todos_clientes]
            self.combo_cliente.configure(values=nomes)
            return

        filtrados = [
            c["nome_cliente"] for c in self.todos_clientes
            if termo in c["nome_cliente"].lower()
            or termo in c.get("contato", "").lower()
            or termo in c.get("id", "").lower()
        ]

        if filtrados:
            self.combo_cliente.configure(values=filtrados)
        else:
            self.combo_cliente.configure(values=["(Nenhum cliente encontrado)"])

    def cadastrar_cliente_rapido(self):
        """Abre a modal de cadastro rápido de cliente para usar no orçamento."""
        texto_digitado = self.combo_cliente.get().strip()
        if texto_digitado in ["(Nenhum cliente cadastrado)", "(Nenhum cliente encontrado)"]:
            texto_digitado = ""

        def on_cliente_salvo(dados):
            novo_cliente = self.clientes_service.adicionar_cliente(
                nome_cliente=dados["nome_cliente"],
                endereco=dados["endereco"],
                data_ultimo_pedido=dados["data_ultimo_pedido"],
                contato=dados["contato"]
            )
            self.carregar_opcoes_clientes(selecionar_novo=novo_cliente["nome_cliente"])
            messagebox.showinfo("Sucesso", f"Cliente '{novo_cliente['nome_cliente']}' cadastrado e selecionado!", parent=self)

        modal = ClienteFormModal(
            self,
            title="Cadastro Rápido de Cliente",
            on_save=on_cliente_salvo,
            nome_inicial=texto_digitado
        )

    def adicionar_material_lista(self):
        """Adiciona material do estoque à lista de simulação do orçamento."""
        opcao_selecionada = self.combo_materiais.get()
        if opcao_selecionada not in self.mapa_estoque:
            messagebox.showwarning("Seleção Inválida", "Por favor, selecione um material válido do estoque.", parent=self)
            return
            
        item_estoque = self.mapa_estoque[opcao_selecionada]
        qtd_str = self.entry_qtd_usada.get().strip().replace(",", ".")
        
        if not qtd_str:
            messagebox.showwarning("Quantidade Necessária", "Informe a quantidade do material utilizada.", parent=self)
            return
            
        try:
            qtd_usada = float(qtd_str)
            if qtd_usada <= 0:
                raise ValueError("Quantidade deve ser positiva")
        except ValueError:
            messagebox.showerror("Quantidade Inválida", "Digite um valor numérico válido para a quantidade.", parent=self)
            return

        item_id = item_estoque["id"]
        preco_unit = float(item_estoque["preco_unitario"])
        
        item_existente = next((m for m in self.itens_usados if m["item_id"] == item_id), None)
        if item_existente:
            item_existente["quantidade"] += qtd_usada
            item_existente["subtotal"] = round(item_existente["quantidade"] * item_existente["preco_unitario"], 2)
        else:
            self.itens_usados.append({
                "item_id": item_id,
                "nome": item_estoque["nome"],
                "quantidade": qtd_usada,
                "preco_unitario": preco_unit,
                "subtotal": round(qtd_usada * preco_unit, 2)
            })

        self.entry_qtd_usada.delete(0, "end")
        self.renderizar_materiais_usados()

    def remover_material_lista(self, index):
        """Remove um material da simulação de orçamento."""
        if 0 <= index < len(self.itens_usados):
            self.itens_usados.pop(index)
            self.renderizar_materiais_usados()

    def renderizar_materiais_usados(self):
        """Redesenha a lista de materiais e atualiza a sugestão do valor final (Custo / (1 - 25%))."""
        for child in self.frame_lista_materiais.winfo_children():
            child.destroy()

        custo_materiais = 0.0

        if not self.itens_usados:
            lbl_vazio = ctk.CTkLabel(
                self.frame_lista_materiais,
                text="Nenhum material do estoque adicionado à simulação.",
                font=ctk.CTkFont(size=12, slant="italic"),
                text_color=PALETTE["subtitle_text"]
            )
            lbl_vazio.pack(anchor="w", pady=4)
        else:
            for idx, item in enumerate(self.itens_usados):
                subtotal = float(item.get("subtotal", item.get("quantidade", 0) * item.get("preco_unitario", 0)))
                custo_materiais += subtotal
                
                row_item = ctk.CTkFrame(
                    self.frame_lista_materiais,
                    fg_color=PALETTE["card_bg"],
                    border_color=PALETTE["card_border"],
                    border_width=1,
                    corner_radius=8
                )
                row_item.pack(fill="x", pady=2)
                row_item.grid_columnconfigure(0, weight=1)
                
                lbl_desc = ctk.CTkLabel(
                    row_item,
                    text=f"• {item['nome']} (x{item['quantidade']})",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=PALETTE["title_text"],
                    anchor="w"
                )
                lbl_desc.pack(side="left", padx=10, pady=6)
                
                lbl_price = ctk.CTkLabel(
                    row_item,
                    text=f"R$ {subtotal:.2f}",
                    font=ctk.CTkFont(size=12),
                    text_color=PALETTE["brand_subtitle"]
                )
                lbl_price.pack(side="left", padx=10, pady=6)
                
                btn_del = ctk.CTkButton(
                    row_item,
                    text="❌",
                    width=28,
                    height=28,
                    fg_color="transparent",
                    hover_color="#FFEBEE",
                    text_color="#C62828",
                    command=lambda i=idx: self.remover_material_lista(i)
                )
                btn_del.pack(side="right", padx=6, pady=4)

        if custo_materiais > 0:
            valor_final = custo_materiais / (1.0 - 0.25)
        else:
            valor_final = 0.0

        custo_fmt = f"R$ {custo_materiais:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.lbl_custo_mat_val.configure(text=custo_fmt)
        
        self.entry_valor_final.delete(0, "end")
        if valor_final > 0:
            self.entry_valor_final.insert(0, f"{valor_final:.2f}")

    def limpar_formulario(self):
        """Limpa todos os campos para um novo orçamento."""
        self.carregar_opcoes_clientes()
        self.entry_data_emissao.delete(0, "end")
        self.entry_data_emissao.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_produto.delete(0, "end")
        self.entry_valor_final.delete(0, "end")
        self.itens_usados.clear()
        self.renderizar_materiais_usados()

    def acao_gerar_pdf(self):
        """Valida os dados e aciona o gerador de PDF de orçamento."""
        cliente = self.combo_cliente.get().strip()
        data_em = self.entry_data_emissao.get().strip()
        valor_str = self.entry_valor_final.get().strip().replace(",", ".")

        if not cliente or cliente in ["(Nenhum cliente cadastrado)", "(Nenhum cliente encontrado)"]:
            messagebox.showwarning("Cliente Necessário", "Por favor, selecione ou digite o nome do cliente do orçamento.", parent=self)
            return

        if not valor_str:
            messagebox.showwarning("Valor Necessário", "Por favor, informe ou calcule o valor final do orçamento.", parent=self)
            return

        try:
            val_num = float(valor_str)
            if val_num <= 0:
                raise ValueError("Valor deve ser positivo")
            valor_fmt = f"R$ {val_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except ValueError:
            messagebox.showerror("Valor Inválido", "Insira um valor numérico válido para o orçamento (ex: 250.00).", parent=self)
            return

        PDFService.gerar_pdf_orcamento(
            nome_cliente=cliente,
            data_emissao=data_em if data_em else datetime.now().strftime("%d/%m/%Y"),
            valor_orcamento=valor_fmt,
            base_dir=self.base_dir,
            parent_window=self
        )
