import customtkinter as ctk
from config.settings import PALETTE

class GenericModuleView(ctk.CTkFrame):
    """Visão genérica para os outros módulos da aplicação com visual coerente."""
    def __init__(self, master, title, description, icon_image=None, **kwargs):
        super().__init__(master, fg_color=PALETTE["main_bg"], corner_radius=0, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Cabeçalho do Módulo
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(30, 10))
        
        lbl_title = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(family="Georgia", size=28, weight="bold"),
            text_color=PALETTE["title_text"],
            anchor="w"
        )
        lbl_title.pack(side="left")
        
        lbl_desc = ctk.CTkLabel(
            self,
            text=description,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=PALETTE["subtitle_text"],
            anchor="w"
        )
        lbl_desc.grid(row=1, column=0, sticky="ew", padx=40, pady=(0, 20))
        
        # Container de cards / dados
        cards_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        cards_container.grid(row=2, column=0, sticky="nsew", padx=40, pady=(0, 30))
        cards_container.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Exemplo de cards demonstrativos
        stats = [
            ("Total Registrado", "128", "+12% este mês"),
            ("Em Processamento", "14", "Atualizado hoje"),
            ("Status do Módulo", "Ativo", "Sincronizado")
        ]
        
        for i, (st_title, st_val, st_sub) in enumerate(stats):
            card = ctk.CTkFrame(
                cards_container,
                fg_color=PALETTE["card_bg"],
                border_color=PALETTE["card_border"],
                border_width=1,
                corner_radius=16
            )
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            
            ctk.CTkLabel(
                card,
                text=st_title,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=PALETTE["brand_subtitle"]
            ).pack(anchor="w", padx=16, pady=(16, 4))
            
            ctk.CTkLabel(
                card,
                text=st_val,
                font=ctk.CTkFont(family="Georgia", size=26, weight="bold"),
                text_color=PALETTE["title_text"]
            ).pack(anchor="w", padx=16, pady=2)
            
            ctk.CTkLabel(
                card,
                text=st_sub,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=PALETTE["subtitle_text"]
            ).pack(anchor="w", padx=16, pady=(0, 16))
