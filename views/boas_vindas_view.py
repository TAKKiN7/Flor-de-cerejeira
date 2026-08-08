import customtkinter as ctk
from config.settings import PALETTE

class BoasVindasView(ctk.CTkFrame):
    """Tela principal de Boas-Vindas com a mascote Hanna."""
    def __init__(self, master, mascot_image, **kwargs):
        super().__init__(master, fg_color=PALETTE["main_bg"], corner_radius=0, **kwargs)
        
        # Centralizador vertical e horizontal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, padx=40, pady=40)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Título principal
        lbl_title = ctk.CTkLabel(
            content_frame,
            text="Hello! Eu sou a Hanna",
            font=ctk.CTkFont(family="Georgia", size=38, weight="bold"),
            text_color=PALETTE["title_text"]
        )
        lbl_title.pack(pady=(0, 8))
        
        # Subtítulo
        lbl_subtitle = ctk.CTkLabel(
            content_frame,
            text="Bem-vinda ao seu espaço criativo, onde a organização encontra a arte.",
            font=ctk.CTkFont(family="Segoe UI", size=15),
            text_color=PALETTE["subtitle_text"]
        )
        lbl_subtitle.pack(pady=(0, 35))
        
        # Mascote Hanna centralizada
        if mascot_image:
            lbl_mascot = ctk.CTkLabel(
                content_frame,
                text="",
                image=mascot_image
            )
            lbl_mascot.pack(pady=10)
