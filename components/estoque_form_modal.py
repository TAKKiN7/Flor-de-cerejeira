import customtkinter as ctk
from tkinter import messagebox
from config.settings import PALETTE, centralizar_janela

class EstoqueFormModal(ctk.CTkToplevel):
    """Janela modal para criação e edição de itens do estoque."""
    
    CATEGORIAS_PADRAO = ["Papéis", "Tintas", "Molduras", "Pincéis", "Insumos", "Embalagens", "Outros"]
    UNIDADES_PADRAO = ["un", "ml", "g", "folha", "m", "kit"]

    def __init__(self, parent, title="Novo Item de Estoque", item_data=None, on_save=None):
        super().__init__(parent)
        
        self.on_save = on_save
        self.item_data = item_data
        
        self.title(title)
        self.geometry("480x560")
        self.resizable(False, False)
        self.configure(fg_color=PALETTE["main_bg"])
        
        # Centralizar em relação à janela principal
        centralizar_janela(self, 480, 560, parent)
        self.transient(parent)
        self.grab_set()
        
        self.grid_columnconfigure(0, weight=1)
        
        # Cabeçalho da Modal
        header_frame = ctk.CTkFrame(self, fg_color=PALETTE["sidebar_bg"], height=70, corner_radius=0)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        
        lbl_header = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(family="Georgia", size=22, weight="bold"),
            text_color=PALETTE["brand_title"]
        )
        lbl_header.pack(expand=True, pady=18)
        
        # Form Container
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=32, pady=24)
        form_frame.grid_columnconfigure(0, weight=1)
        
        # 1. Nome do Item
        ctk.CTkLabel(
            form_frame,
            text="Nome do Material / Item",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.entry_nome = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: Papel Canson 300g",
            height=40,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_nome.pack(fill="x", pady=(0, 14))
        if item_data and "nome" in item_data:
            self.entry_nome.insert(0, item_data["nome"])
            
        # 2. Categoria e Unidade (Lado a Lado)
        row_cat_uni = ctk.CTkFrame(form_frame, fg_color="transparent")
        row_cat_uni.pack(fill="x", pady=(0, 14))
        row_cat_uni.grid_columnconfigure((0, 1), weight=1)
        
        # Categoria
        col_cat = ctk.CTkFrame(row_cat_uni, fg_color="transparent")
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
        
        # Unidade
        col_uni = ctk.CTkFrame(row_cat_uni, fg_color="transparent")
        col_uni.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(
            col_uni,
            text="Unidade de Medida",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        uni_inicial = item_data.get("unidade", self.UNIDADES_PADRAO[0]) if item_data else self.UNIDADES_PADRAO[0]
        self.combo_unidade = ctk.CTkOptionMenu(
            col_uni,
            values=self.UNIDADES_PADRAO,
            height=40,
            corner_radius=10,
            fg_color=PALETTE["card_bg"],
            button_color=PALETTE["active_pill"],
            button_hover_color=PALETTE["active_pill_hover"],
            text_color=PALETTE["title_text"],
            font=ctk.CTkFont(size=13)
        )
        self.combo_unidade.pack(fill="x")
        self.combo_unidade.set(uni_inicial)
        
        # 3. Quantidade e Preço Unitário (Lado a Lado)
        row_qtd_preco = ctk.CTkFrame(form_frame, fg_color="transparent")
        row_qtd_preco.pack(fill="x", pady=(0, 20))
        row_qtd_preco.grid_columnconfigure((0, 1), weight=1)
        
        # Quantidade
        col_qtd = ctk.CTkFrame(row_qtd_preco, fg_color="transparent")
        col_qtd.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(
            col_qtd,
            text="Quantidade em Estoque",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.entry_quantidade = ctk.CTkEntry(
            col_qtd,
            placeholder_text="Ex: 10",
            height=40,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_quantidade.pack(fill="x")
        if item_data and "quantidade" in item_data:
            self.entry_quantidade.insert(0, str(item_data["quantidade"]))
            
        # Preço Unitário
        col_preco = ctk.CTkFrame(row_qtd_preco, fg_color="transparent")
        col_preco.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(
            col_preco,
            text="Preço Unitário (R$)",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.entry_preco = ctk.CTkEntry(
            col_preco,
            placeholder_text="Ex: 15.50",
            height=40,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_preco.pack(fill="x")
        if item_data and "preco_unitario" in item_data:
            self.entry_preco.insert(0, str(item_data["preco_unitario"]))
            
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
            text="Salvar Item",
            height=42,
            corner_radius=10,
            fg_color=PALETTE["active_pill"],
            hover_color=PALETTE["active_pill_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(weight="bold"),
            command=self.salvar
        )
        btn_save.grid(row=0, column=1, padx=(8, 0), sticky="ew")

    def salvar(self):
        """Valida os campos e aciona o callback de salvamento."""
        nome = self.entry_nome.get().strip()
        categoria = self.combo_categoria.get()
        unidade = self.combo_unidade.get()
        quantidade_str = self.entry_quantidade.get().strip().replace(",", ".")
        preco_str = self.entry_preco.get().strip().replace(",", ".")
        
        if not nome or not quantidade_str or not preco_str:
            messagebox.showwarning("Campos Obrigatórios", "Por favor, preencha o nome do item, quantidade e preço unitário.", parent=self)
            return
            
        try:
            quantidade = float(quantidade_str)
            if quantidade < 0:
                raise ValueError("Quantidade negativa")
        except ValueError:
            messagebox.showerror("Quantidade Inválida", "Por favor, insira um número válido e não negativo para a quantidade.", parent=self)
            return

        try:
            preco_unitario = float(preco_str)
            if preco_unitario < 0:
                raise ValueError("Preço negativo")
        except ValueError:
            messagebox.showerror("Preço Inválido", "Por favor, insira um preço unitário numérico válido (ex: 15.50).", parent=self)
            return

        dados = {
            "nome": nome,
            "categoria": categoria,
            "unidade": unidade,
            "quantidade": quantidade,
            "preco_unitario": preco_unitario
        }
        
        if self.item_data and "id" in self.item_data:
            dados["id"] = self.item_data["id"]

        if self.on_save:
            self.on_save(dados)
            
        self.destroy()
