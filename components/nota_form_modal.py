import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from config.settings import PALETTE

class NotaFormModal(ctk.CTkToplevel):
    """Janela modal para criação de uma nova nota/lembrete na agenda."""
    
    def __init__(self, parent, data_padrao=None, on_save=None):
        super().__init__(parent)
        
        self.on_save = on_save
        data_str = data_padrao if data_padrao else datetime.now().strftime("%d/%m/%Y")
        
        self.title("Adicionar Lembrete / Nota")
        self.geometry("450x440")
        self.resizable(False, False)
        self.configure(fg_color=PALETTE["main_bg"])
        
        self.transient(parent)
        self.grab_set()
        
        self.grid_columnconfigure(0, weight=1)
        
        # Cabeçalho da Modal
        header_frame = ctk.CTkFrame(self, fg_color=PALETTE["sidebar_bg"], height=65, corner_radius=0)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        
        lbl_header = ctk.CTkLabel(
            header_frame,
            text=f"Nova Nota - {data_str}",
            font=ctk.CTkFont(family="Georgia", size=20, weight="bold"),
            text_color=PALETTE["brand_title"]
        )
        lbl_header.pack(expand=True, pady=16)
        
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30, pady=20)
        form_frame.grid_columnconfigure(0, weight=1)
        
        # 1. Data
        ctk.CTkLabel(
            form_frame,
            text="Data (DD/MM/AAAA)",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.entry_data = ctk.CTkEntry(
            form_frame,
            height=38,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_data.pack(fill="x", pady=(0, 14))
        self.entry_data.insert(0, data_str)
        
        # 2. Horário
        ctk.CTkLabel(
            form_frame,
            text="Horário",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.entry_horario = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: 14:00",
            height=38,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_horario.pack(fill="x", pady=(0, 14))
        self.entry_horario.insert(0, "09:00")
        
        # 3. Título / Descrição da Nota
        ctk.CTkLabel(
            form_frame,
            text="Nota / Lembrete",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.entry_titulo = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: 🎨 Comprar tintas aquarela para novos quadros",
            height=40,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_titulo.pack(fill="x", pady=(0, 20))
        
        # Botões
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom")
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        btn_cancel = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            height=40,
            corner_radius=10,
            fg_color="transparent",
            border_color=PALETTE["sidebar_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(weight="bold"),
            command=self.destroy
        )
        btn_cancel.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        
        btn_save = ctk.CTkButton(
            btn_frame,
            text="Salvar Nota",
            height=40,
            corner_radius=10,
            fg_color=PALETTE["active_pill"],
            hover_color=PALETTE["active_pill_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(weight="bold"),
            command=self.salvar
        )
        btn_save.grid(row=0, column=1, padx=(6, 0), sticky="ew")

    def salvar(self):
        data_val = self.entry_data.get().strip()
        horario = self.entry_horario.get().strip()
        titulo = self.entry_titulo.get().strip()
        
        if not data_val or not titulo:
            messagebox.showwarning("Campos Obrigatórios", "Por favor, preencha a data e o título da nota.", parent=self)
            return

        if self.on_save:
            self.on_save(data_val, titulo, horario)
            
        self.destroy()
