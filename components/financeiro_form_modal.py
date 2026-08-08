import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from config.settings import PALETTE, centralizar_janela

class FinanceiroFormModal(ctk.CTkToplevel):
    """Janela modal para criação e edição de lançamentos financeiros (Entradas / Saídas)."""
    
    CATEGORIAS_PADRAO = ["Entrada", "Restante", "Aviamento", "Papelaria", "Insumos", "Embalagens", "Mão de Obra", "Outros"]
    FORMAS_PAGAMENTO = ["Pix", "Débito", "Crédito", "Dinheiro", "Boleto", "Outro"]

    def __init__(self, parent, title="Novo Lançamento", item_data=None, on_save=None):
        super().__init__(parent)
        
        self.on_save = on_save
        self.item_data = item_data
        
        self.title(title)
        self.geometry("480x600")
        self.resizable(False, False)
        self.configure(fg_color=PALETTE["main_bg"])
        
        # Centralizar em relação à janela principal
        centralizar_janela(self, 480, 600, parent)
        self.transient(parent)
        self.grab_set()
        
        self.grid_columnconfigure(0, weight=1)
        
        # Cabeçalho da Modal
        header_frame = ctk.CTkFrame(self, fg_color=PALETTE["sidebar_bg"], height=65, corner_radius=0)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        
        lbl_header = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(family="Georgia", size=22, weight="bold"),
            text_color=PALETTE["brand_title"]
        )
        lbl_header.pack(expand=True, pady=16)
        
        # Form Container
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=32, pady=20)
        form_frame.grid_columnconfigure(0, weight=1)
        
        # 1. Tipo de Lançamento (Entrada vs Saída com bordas finas de 1px e cores dedicadas)
        ctk.CTkLabel(
            form_frame,
            text="Tipo de Movimentação",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 6))
        
        self.tipo_selecionado = item_data.get("tipo", "Saída") if item_data else "Saída"
        
        row_tipo = ctk.CTkFrame(form_frame, fg_color="transparent")
        row_tipo.pack(fill="x", pady=(0, 14))
        row_tipo.grid_columnconfigure((0, 1), weight=1)
        
        self.btn_tipo_entrada = ctk.CTkButton(
            row_tipo,
            text="🟢 Entrada (Receita)",
            height=38,
            corner_radius=10,
            border_width=1,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: self.selecionar_tipo("Entrada")
        )
        self.btn_tipo_entrada.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.btn_tipo_saida = ctk.CTkButton(
            row_tipo,
            text="🔴 Saída (Despesa)",
            height=38,
            corner_radius=10,
            border_width=1,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: self.selecionar_tipo("Saída")
        )
        self.btn_tipo_saida.grid(row=0, column=1, padx=(6, 0), sticky="ew")

        self.atualizar_estilo_botoes_tipo()

        # 2. Data e Valor (Lado a Lado)
        row_dt_val = ctk.CTkFrame(form_frame, fg_color="transparent")
        row_dt_val.pack(fill="x", pady=(0, 14))
        row_dt_val.grid_columnconfigure((0, 1), weight=1)
        
        # Data
        col_dt = ctk.CTkFrame(row_dt_val, fg_color="transparent")
        col_dt.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(
            col_dt,
            text="Data (DD/MM/AAAA)",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        dt_inicial = item_data.get("data", data_hoje) if item_data else data_hoje
        self.entry_data = ctk.CTkEntry(col_dt, height=40, corner_radius=10, border_color=PALETTE["card_border"], font=ctk.CTkFont(size=14))
        self.entry_data.pack(fill="x")
        self.entry_data.insert(0, dt_inicial)
        
        # Valor (R$)
        col_val = ctk.CTkFrame(row_dt_val, fg_color="transparent")
        col_val.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(
            col_val,
            text="Valor (R$)",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        val_inicial = ""
        if item_data:
            if item_data.get("tipo") == "Entrada":
                val_inicial = str(item_data.get("valor_entrada", ""))
            else:
                val_inicial = str(item_data.get("valor_saida", ""))
                
        self.entry_valor = ctk.CTkEntry(col_val, placeholder_text="Ex: 50.00", height=40, corner_radius=10, border_color=PALETTE["card_border"], font=ctk.CTkFont(size=14))
        self.entry_valor.pack(fill="x")
        if val_inicial and val_inicial != "0.0":
            self.entry_valor.insert(0, val_inicial)

        # 3. Descrição
        ctk.CTkLabel(
            form_frame,
            text="Descrição",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.entry_descricao = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: Ponta de Agulha, Grafitte, Bordado...",
            height=40,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_descricao.pack(fill="x", pady=(0, 14))
        if item_data and "descricao" in item_data:
            self.entry_descricao.insert(0, item_data["descricao"])
            
        # 4. Categoria e Forma de Pagamento (Lado a Lado)
        row_cat_pag = ctk.CTkFrame(form_frame, fg_color="transparent")
        row_cat_pag.pack(fill="x", pady=(0, 20))
        row_cat_pag.grid_columnconfigure((0, 1), weight=1)
        
        # Categoria
        col_cat = ctk.CTkFrame(row_cat_pag, fg_color="transparent")
        col_cat.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(
            col_cat,
            text="Categoria",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        cat_inicial = item_data.get("categoria", self.CATEGORIAS_PADRAO[0]) if item_data else self.CATEGORIAS_PADRAO[0]
        self.combo_categoria = ctk.CTkOptionMenu(
            col_cat,
            values=self.CATEGORIAS_PADRAO,
            height=40,
            corner_radius=10,
            fg_color=PALETTE["card_bg"],
            button_color=PALETTE["active_pill"],
            button_hover_color=PALETTE["active_pill_hover"],
            text_color=PALETTE["title_text"],
            font=ctk.CTkFont(size=13)
        )
        self.combo_categoria.pack(fill="x")
        self.combo_categoria.set(cat_inicial)
        
        # Forma de Pagamento
        col_pag = ctk.CTkFrame(row_cat_pag, fg_color="transparent")
        col_pag.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(
            col_pag,
            text="Forma de Pagamento",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        pag_inicial = item_data.get("forma_pagamento", self.FORMAS_PAGAMENTO[0]) if item_data else self.FORMAS_PAGAMENTO[0]
        self.combo_pagamento = ctk.CTkOptionMenu(
            col_pag,
            values=self.FORMAS_PAGAMENTO,
            height=40,
            corner_radius=10,
            fg_color=PALETTE["card_bg"],
            button_color=PALETTE["active_pill"],
            button_hover_color=PALETTE["active_pill_hover"],
            text_color=PALETTE["title_text"],
            font=ctk.CTkFont(size=13)
        )
        self.combo_pagamento.pack(fill="x")
        self.combo_pagamento.set(pag_inicial)
        
        # Botões de Ação
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom")
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        btn_cancel = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            height=42,
            corner_radius=10,
            fg_color="transparent",
            border_color=PALETTE["sidebar_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(weight="bold"),
            command=self.destroy
        )
        btn_cancel.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        
        btn_save = ctk.CTkButton(
            btn_frame,
            text="Salvar Lançamento",
            height=42,
            corner_radius=10,
            fg_color=PALETTE["active_pill"],
            hover_color=PALETTE["active_pill_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(weight="bold"),
            command=self.salvar
        )
        btn_save.grid(row=0, column=1, padx=(8, 0), sticky="ew")

    def selecionar_tipo(self, tipo):
        """Seleciona o tipo de movimentação (Entrada ou Saída) e atualiza os botões."""
        self.tipo_selecionado = tipo
        self.atualizar_estilo_botoes_tipo()

    def atualizar_estilo_botoes_tipo(self):
        """Atualiza o estilo das bordas (1px) e as cores destacadas de Entrada (verde) e Saída (vermelho)."""
        if self.tipo_selecionado == "Entrada":
            self.btn_tipo_entrada.configure(
                fg_color="#2E7D32",
                hover_color="#1B5E20",
                text_color="#FFFFFF",
                border_color="#2E7D32"
            )
            self.btn_tipo_saida.configure(
                fg_color="transparent",
                hover_color=PALETTE["inactive_hover"],
                text_color=PALETTE["inactive_text"],
                border_color=PALETTE["card_border"]
            )
        else:
            self.btn_tipo_entrada.configure(
                fg_color="transparent",
                hover_color=PALETTE["inactive_hover"],
                text_color=PALETTE["inactive_text"],
                border_color=PALETTE["card_border"]
            )
            self.btn_tipo_saida.configure(
                fg_color="#C62828",
                hover_color="#B71C1C",
                text_color="#FFFFFF",
                border_color="#C62828"
            )

    def salvar(self):
        """Valida os campos e aciona o callback de salvamento."""
        tipo = self.tipo_selecionado
        data_val = self.entry_data.get().strip()
        descricao = self.entry_descricao.get().strip()
        categoria = self.combo_categoria.get()
        valor_str = self.entry_valor.get().strip().replace(",", ".")
        forma_pagamento = self.combo_pagamento.get()
        
        if not descricao or not valor_str or not data_val:
            messagebox.showwarning("Campos Obrigatórios", "Por favor, preencha a data, descrição e o valor do lançamento.", parent=self)
            return
            
        try:
            valor = float(valor_str)
            if valor <= 0:
                raise ValueError("Valor deve ser positivo")
        except ValueError:
            messagebox.showerror("Valor Inválido", "Por favor, insira um valor numérico válido (ex: 50.00).", parent=self)
            return

        dados = {
            "tipo": tipo,
            "data": data_val,
            "descricao": descricao,
            "categoria": categoria,
            "valor": valor,
            "forma_pagamento": forma_pagamento
        }
        
        if self.item_data and "id" in self.item_data:
            dados["id"] = self.item_data["id"]

        if self.on_save:
            self.on_save(dados)
            
        self.destroy()
