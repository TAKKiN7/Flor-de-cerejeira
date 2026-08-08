import customtkinter as ctk

# Configurações globais de aparência do CustomTkinter
def setup_theme():
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")

# Cores da Paleta "Flor de Cerejeira" com suporte a Modo Claro e Modo Escuro (Light, Dark)
PALETTE = {
    "sidebar_bg": ("#FDF4F5", "#1C1718"),
    "sidebar_border": ("#F2DFE2", "#2D2426"),
    "main_bg": ("#FFFDFE", "#141112"),
    "active_pill": "#F59CA9",
    "active_pill_hover": "#ED8B99",
    "inactive_text": ("#5A4549", "#D3C2C5"),
    "inactive_hover": ("#F9E5E8", "#2A2123"),
    "active_text": "#FFFFFF",
    "title_text": ("#331B20", "#FAECEF"),
    "subtitle_text": ("#685458", "#B5A2A6"),
    "brand_title": ("#5A2C34", "#F4C4CD"),
    "brand_subtitle": ("#8E6971", "#CBA4AC"),
    "card_bg": ("#FDF8F9", "#1E1819"),
    "card_border": ("#F7E2E5", "#332729"),
    "accent": "#F59CA9"
}

def get_color(color_val, mode=None):
    """Retorna uma string de cor única (#HEX) compatível com o TTK do Tkinter."""
    if mode is None:
        mode = ctk.get_appearance_mode()
    if isinstance(color_val, (list, tuple)):
        return color_val[1] if mode == "Dark" else color_val[0]
    return color_val
