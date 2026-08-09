import customtkinter as ctk
from tkinter import messagebox
from config.settings import PALETTE, centralizar_janela
from services.cursos_service import CursosService

class CursoFormModal(ctk.CTkToplevel):
    """Modal para criação e edição de um curso."""
    
    def __init__(self, parent, title="Novo Curso", curso_data=None, on_save=None):
        super().__init__(parent)
        
        self.on_save = on_save
        self.curso_data = curso_data
        
        self.title(title)
        self.geometry("500x520")
        self.resizable(False, False)
        self.configure(fg_color=PALETTE["main_bg"])
        
        centralizar_janela(self, 500, 520, parent)
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
        
        # 1. Título do Curso
        ctk.CTkLabel(
            form_frame,
            text="Nome do Curso *",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.entry_titulo = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: Costura Criativa Avançada",
            height=40,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_titulo.pack(fill="x", pady=(0, 14))
        if curso_data and "titulo" in curso_data:
            self.entry_titulo.insert(0, curso_data["titulo"])
            
        # 2. Categoria
        ctk.CTkLabel(
            form_frame,
            text="Categoria",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.combo_categoria = ctk.CTkComboBox(
            form_frame,
            values=CursosService.CATEGORIAS_PADRAO,
            height=40,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=13),
            dropdown_font=ctk.CTkFont(size=13)
        )
        self.combo_categoria.pack(fill="x", pady=(0, 14))
        if curso_data and "categoria" in curso_data:
            self.combo_categoria.set(curso_data["categoria"])
        else:
            self.combo_categoria.set("Costura")
            
        # 3. Descrição
        ctk.CTkLabel(
            form_frame,
            text="Descrição / Objetivos do Curso",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.textbox_desc = ctk.CTkTextbox(
            form_frame,
            height=100,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            border_width=1,
            font=ctk.CTkFont(size=13)
        )
        self.textbox_desc.pack(fill="x", pady=(0, 20))
        if curso_data and "descricao" in curso_data:
            self.textbox_desc.insert("1.0", curso_data["descricao"])
            
        # Botões de Ação
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom")
        
        self.btn_cancelar = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            height=42,
            corner_radius=10,
            fg_color="transparent",
            border_color=PALETTE["sidebar_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.destroy
        )
        self.btn_cancelar.pack(side="left", expand=True, fill="x", padx=(0, 8))
        
        self.btn_salvar = ctk.CTkButton(
            btn_frame,
            text="Salvar Curso",
            height=42,
            corner_radius=10,
            fg_color=PALETTE["active_pill"],
            hover_color=PALETTE["active_pill_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.salvar
        )
        self.btn_salvar.pack(side="right", expand=True, fill="x", padx=(8, 0))

    def salvar(self):
        titulo = self.entry_titulo.get().strip()
        categoria = self.combo_categoria.get().strip()
        descricao = self.textbox_desc.get("1.0", "end-1c").strip()
        
        if not titulo:
            messagebox.showwarning("Campo Obrigatório", "Por favor, digite o nome do curso.", parent=self)
            self.entry_titulo.focus()
            return
            
        dados = {
            "titulo": titulo,
            "categoria": categoria,
            "descricao": descricao
        }
        
        if self.on_save:
            self.on_save(dados)
            
        self.destroy()
