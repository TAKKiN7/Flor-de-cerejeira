import sys
import os
import customtkinter as ctk

def get_base_dir():
    """Retorna o diretório base para gravação de dados (onde o .exe está localizado se congelado, ou a raiz do projeto)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_assets_dir(base_dir=None):
    """Retorna o diretório de assets estáticos (prioriza sys._MEIPASS quando congelado)."""
    if getattr(sys, 'frozen', False):
        meipass_assets = os.path.join(getattr(sys, '_MEIPASS', ''), "assets")
        if os.path.exists(meipass_assets):
            return meipass_assets
    if base_dir is None:
        base_dir = get_base_dir()
    return os.path.join(base_dir, "assets")

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

def centralizar_janela(window, width, height, parent=None):
    """Centraliza a janela modal (CTkToplevel) no centro exato da janela pai ou da tela."""
    window.update_idletasks()
    
    if parent is None and hasattr(window, "master"):
        parent = window.master
        
    if parent:
        try:
            root = parent.winfo_toplevel()
            root.update_idletasks()
            p_w = root.winfo_width()
            p_h = root.winfo_height()
            p_x = root.winfo_x()
            p_y = root.winfo_y()
            
            if p_w > 100 and p_h > 100:
                pos_x = p_x + (p_w - width) // 2
                pos_y = p_y + (p_h - height) // 2
                pos_x = max(0, pos_x)
                pos_y = max(0, pos_y)
                window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
                return
        except Exception:
            pass

    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    pos_x = max(0, (screen_w - width) // 2)
    pos_y = max(0, (screen_h - height) // 2)
    window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
