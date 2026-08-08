import customtkinter as ctk
from config.settings import PALETTE

class SidebarButton(ctk.CTkButton):
    """Botão da barra lateral estilizado conforme o protótipo."""
    def __init__(self, master, text, icon_normal, icon_active, command=None, **kwargs):
        self.icon_normal = icon_normal
        self.icon_active = icon_active
        self.is_active = False
        
        super().__init__(
            master,
            text=text,
            image=self.icon_normal,
            compound="left",
            anchor="w",
            height=46,
            corner_radius=14,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="transparent",
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            command=command,
            border_spacing=12,
            **kwargs
        )

    def set_active(self, active: bool):
        self.is_active = active
        if active:
            self.configure(
                fg_color=PALETTE["active_pill"],
                text_color=PALETTE["active_text"],
                hover_color=PALETTE["active_pill_hover"],
                image=self.icon_active
            )
        else:
            self.configure(
                fg_color="transparent",
                text_color=PALETTE["inactive_text"],
                hover_color=PALETTE["inactive_hover"],
                image=self.icon_normal
            )
