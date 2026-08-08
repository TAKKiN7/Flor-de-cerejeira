import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from config.settings import PALETTE, centralizar_janela

class ClienteFormModal(ctk.CTkToplevel):
    """Janela modal para criação e edição de clientes."""
    
    def __init__(self, parent, title="Novo Cliente", cliente_data=None, on_save=None, nome_inicial=None):
        super().__init__(parent)
        
        self.on_save = on_save
        self.cliente_data = cliente_data
        
        self.title(title)
        self.geometry("480x540")
        self.resizable(False, False)
        self.configure(fg_color=PALETTE["main_bg"])
        
        # Centralizar em relação à janela principal
        centralizar_janela(self, 480, 540, parent)
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
        
        # 1. Nome do Cliente
        ctk.CTkLabel(
            form_frame,
            text="Nome do Cliente",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.entry_nome = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: Camila Oliveira",
            height=40,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_nome.pack(fill="x", pady=(0, 14))
        if cliente_data and "nome_cliente" in cliente_data:
            self.entry_nome.insert(0, cliente_data["nome_cliente"])
        elif nome_inicial:
            self.entry_nome.insert(0, nome_inicial)
            
        # 2. Endereço
        ctk.CTkLabel(
            form_frame,
            text="Endereço",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.entry_endereco = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: Rua das Flores, 123 - São Paulo/SP",
            height=40,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_endereco.pack(fill="x", pady=(0, 14))
        if cliente_data and "endereco" in cliente_data:
            self.entry_endereco.insert(0, cliente_data["endereco"])
            
        # 3. Data do Último Pedido
        ctk.CTkLabel(
            form_frame,
            text="Data do Último Pedido",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        data_ult_inicial = cliente_data.get("data_ultimo_pedido", data_hoje) if cliente_data else data_hoje
        
        self.entry_data_ultimo = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: 04/08/2026",
            height=40,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_data_ultimo.pack(fill="x", pady=(0, 14))
        self.entry_data_ultimo.insert(0, data_ult_inicial)
        
        # 4. Contato (Telefone / WhatsApp / E-mail)
        ctk.CTkLabel(
            form_frame,
            text="Contato (Telefone / WhatsApp / E-mail)",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.entry_contato = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: (11) 98765-4321 ou cliente@email.com",
            height=40,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_contato.pack(fill="x", pady=(0, 20))
        if cliente_data and "contato" in cliente_data:
            self.entry_contato.insert(0, cliente_data["contato"])
            
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
            text="Salvar Cliente",
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
        endereco = self.entry_endereco.get().strip()
        data_ultimo = self.entry_data_ultimo.get().strip()
        contato = self.entry_contato.get().strip()
        
        if not nome or not contato:
            messagebox.showwarning("Campos Obrigatórios", "Por favor, preencha pelo menos o Nome do Cliente e o Contato.", parent=self)
            return

        dados = {
            "nome_cliente": nome,
            "endereco": endereco if endereco else "-",
            "data_ultimo_pedido": data_ultimo if data_ultimo else "-",
            "contato": contato
        }
        
        if self.cliente_data and "id" in self.cliente_data:
            dados["id"] = self.cliente_data["id"]

        if self.on_save:
            self.on_save(dados)
            
        self.destroy()
