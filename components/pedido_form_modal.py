import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from config.settings import PALETTE

class PedidoFormModal(ctk.CTkToplevel):
    """Janela modal para criação e edição de pedidos."""
    
    def __init__(self, parent, title="Novo Pedido", pedido_data=None, on_save=None):
        super().__init__(parent)
        
        self.on_save = on_save
        self.pedido_data = pedido_data
        
        self.title(title)
        self.geometry("480x580")
        self.resizable(False, False)
        self.configure(fg_color=PALETTE["main_bg"])
        
        # Centralizar em relação à janela principal
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
        
        # 1. Data do Pedido
        ctk.CTkLabel(
            form_frame,
            text="Data do Pedido",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        data_ped_inicial = pedido_data.get("data_pedido", data_hoje) if pedido_data else data_hoje
        
        self.entry_data_pedido = ctk.CTkEntry(
            form_frame,
            height=40,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_data_pedido.pack(fill="x", pady=(0, 14))
        self.entry_data_pedido.insert(0, data_ped_inicial)
        
        # 2. Nome do Cliente
        ctk.CTkLabel(
            form_frame,
            text="Nome do Cliente",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.entry_cliente = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: Maria Clara",
            height=40,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_cliente.pack(fill="x", pady=(0, 14))
        if pedido_data and "nome_cliente" in pedido_data:
            self.entry_cliente.insert(0, pedido_data["nome_cliente"])
            
        # 3. Produto
        ctk.CTkLabel(
            form_frame,
            text="Produto",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.entry_produto = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: Quadro Ilustrado 30x40",
            height=40,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_produto.pack(fill="x", pady=(0, 14))
        if pedido_data and "produto" in pedido_data:
            self.entry_produto.insert(0, pedido_data["produto"])
            
        # 4. Valor do Produto
        ctk.CTkLabel(
            form_frame,
            text="Valor do Produto (R$)",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.entry_valor = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: 150.00",
            height=40,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_valor.pack(fill="x", pady=(0, 14))
        if pedido_data and "valor_produto" in pedido_data:
            self.entry_valor.insert(0, str(pedido_data["valor_produto"]))
            
        # 5. Data de Entrega
        ctk.CTkLabel(
            form_frame,
            text="Data de Entrega",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        data_ent_inicial = pedido_data.get("data_entrega", "") if pedido_data else ""
        self.entry_data_entrega = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: 15/08/2026",
            height=40,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_data_entrega.pack(fill="x", pady=(0, 20))
        if data_ent_inicial:
            self.entry_data_entrega.insert(0, data_ent_inicial)
            
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
            text="Salvar Pedido",
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
        data_ped = self.entry_data_pedido.get().strip()
        cliente = self.entry_cliente.get().strip()
        produto = self.entry_produto.get().strip()
        valor = self.entry_valor.get().strip().replace(",", ".")
        data_ent = self.entry_data_entrega.get().strip()
        
        if not cliente or not produto or not valor:
            messagebox.showwarning("Campos Obrigatórios", "Por favor, preencha o nome do cliente, produto e valor.", parent=self)
            return
            
        try:
            val_float = float(valor)
            valor_fmt = f"{val_float:.2f}"
        except ValueError:
            messagebox.showerror("Valor Inválido", "Por favor, insira um valor numérico válido (ex: 150.00).", parent=self)
            return

        dados = {
            "data_pedido": data_ped if data_ped else datetime.now().strftime("%d/%m/%Y"),
            "nome_cliente": cliente,
            "produto": produto,
            "valor_produto": valor_fmt,
            "data_entrega": data_ent if data_ent else "-"
        }
        
        if self.pedido_data and "id" in self.pedido_data:
            dados["id"] = self.pedido_data["id"]

        if self.on_save:
            self.on_save(dados)
            
        self.destroy()
