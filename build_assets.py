import os
import math
from PIL import Image, ImageDraw, ImageFilter, ImageOps

def create_circular_mascot(input_path, output_path, size=(320, 320)):
    """Cria a imagem da mascote em formato circular com borda e sombra suave."""
    if not os.path.exists(input_path):
        print(f"Erro: Imagem {input_path} não encontrada.")
        return
        
    img = Image.open(input_path).convert("RGBA")
    
    # Redimensionar para tamanho alto para anti-aliasing
    scale = 4
    target_size = (size[0] * scale, size[1] * scale)
    
    # Cortar centralizado (square crop)
    min_dim = min(img.size)
    left = (img.width - min_dim) // 2
    top = (img.height - min_dim) // 2
    img = img.crop((left, top, left + min_dim, top + min_dim))
    img = img.resize(target_size, Image.Resampling.LANCZOS)
    
    # Criar máscara circular perfeitamente suave
    mask = Image.new("L", target_size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, target_size[0], target_size[1]), fill=255)
    
    # Aplicar a máscara circular
    circular_img = Image.new("RGBA", target_size, (0, 0, 0, 0))
    circular_img.paste(img, (0, 0), mask=mask)
    
    # Adicionar borda branca/suave em volta
    border_width = 8 * scale
    final_canvas_size = (target_size[0] + border_width * 2, target_size[1] + border_width * 2)
    final_canvas = Image.new("RGBA", final_canvas_size, (0, 0, 0, 0))
    
    # Borda branca circular
    border_mask = Image.new("L", final_canvas_size, 0)
    draw_bmask = ImageDraw.Draw(border_mask)
    draw_bmask.ellipse((0, 0, final_canvas_size[0], final_canvas_size[1]), fill=255)
    
    border_fill = Image.new("RGBA", final_canvas_size, (255, 255, 255, 255))
    final_canvas.paste(border_fill, (0, 0), mask=border_mask)
    final_canvas.paste(circular_img, (border_width, border_width), mask=circular_img)
    
    # Reduzir para tamanho final com antialiasing
    final_img = final_canvas.resize(size, Image.Resampling.LANCZOS)
    final_img.save(output_path, "PNG")
    print(f"Mascote circular salva em: {output_path}")

def draw_palette_logo(size=128, bg_color=(235, 175, 185), icon_color=(100, 45, 55)):
    """Cria a imagem do ícone de paleta para o topo da barra lateral."""
    img = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Fundo circular
    draw.ellipse((0, 0, size * 4, size * 4), fill=bg_color)
    
    # Paleta de pintura
    # Corpo da paleta (elipse levemente rotacionada/offset)
    p_cx, p_cy = size * 2, size * 2.05
    p_rx, p_ry = size * 1.1, size * 0.85
    draw.ellipse((p_cx - p_rx, p_cy - p_ry, p_cx + p_rx, p_cy + p_ry), fill=icon_color)
    
    # Buraco do polegar na paleta (transparente)
    h_cx, h_cy = size * 1.5, size * 2.3
    h_r = size * 0.22
    draw.ellipse((h_cx - h_r, h_cy - h_r, h_cx + h_r, h_cy + h_r), fill=bg_color)
    
    # Manchas de tinta coloridas na paleta
    dots = [
        (size * 2.3, size * 1.5, size * 0.16, (255, 255, 255)),
        (size * 2.6, size * 1.85, size * 0.14, (255, 255, 255)),
        (size * 2.4, size * 2.3, size * 0.15, (255, 255, 255)),
    ]
    for dx, dy, dr, color in dots:
        draw.ellipse((dx - dr, dy - dr, dx + dr, dy + dr), fill=color)
        
    res = img.resize((size, size), Image.Resampling.LANCZOS)
    return res

def draw_vector_icon(name, color=(90, 69, 73), size=64):
    """Gera ícones vetoriais em alta resolução para os botões do menu."""
    S = 256
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    lw = 18
    
    if name == "boas_vindas":
        # Ícone de mão acenando / flor com palma
        cx, cy = S // 2, S // 2 + 10
        # Palma
        draw.ellipse((cx - 45, cy - 35, cx + 45, cy + 45), fill=color)
        # Dedos
        for angle, length in [(-40, 50), (-15, 60), (15, 60), (40, 50)]:
            rad = math.radians(angle)
            fx = cx + int(length * math.sin(rad))
            fy = cy - 35 - int(length * math.cos(rad))
            draw.line([(cx + int(20 * math.sin(rad)), cy - 25 - int(20 * math.cos(rad))), (fx, fy)], fill=color, width=lw, joint="round")
            draw.ellipse((fx - lw//2, fy - lw//2, fx + lw//2, fy + lw//2), fill=color)
        # Brilho / faísca
        draw.polygon([(cx + 65, cy - 65), (cx + 75, cy - 45), (cx + 95, cy - 35), (cx + 75, cy - 25), (cx + 65, cy - 5), (cx + 55, cy - 25), (cx + 35, cy - 35), (cx + 55, cy - 45)], fill=color)

    elif name == "pedidos":
        # Bolsa de compras (Shopping bag)
        x1, y1, x2, y2 = 50, 80, 206, 220
        r = 16
        draw.rounded_rectangle((x1, y1, x2, y2), radius=r, outline=color, width=lw)
        # Alça da bolsa
        draw.arc((85, 35, 171, 110), start=180, end=360, fill=color, width=lw)

    elif name == "clientes":
        # Ícone de usuários (Pessoas)
        # Usuário 1 (frente)
        c1x, c1y = 110, 90
        r1 = 32
        draw.ellipse((c1x - r1, c1y - r1, c1x + r1, c1y + r1), outline=color, width=lw)
        draw.arc((45, 135, 175, 235), start=190, end=350, fill=color, width=lw)
        # Usuário 2 (trás)
        c2x, c2y = 175, 75
        r2 = 25
        draw.ellipse((c2x - r2, c2y - r2, c2x + r2, c2y + r2), fill=color)
        draw.arc((125, 120, 225, 200), start=200, end=340, fill=color, width=lw)

    elif name == "estoque":
        # Caixa de papelão / Estoque
        x1, y1, x2, y2 = 45, 80, 211, 210
        draw.rounded_rectangle((x1, y1, x2, y2), radius=12, outline=color, width=lw)
        # Tampa / Linha central
        draw.line([(45, 120), (211, 120)], fill=color, width=lw)
        # Trava frontal
        draw.rounded_rectangle((100, 105, 156, 145), radius=6, outline=color, width=lw)

    elif name == "financeiro":
        # Cédula de dinheiro
        x1, y1, x2, y2 = 40, 75, 216, 181
        draw.rounded_rectangle((x1, y1, x2, y2), radius=14, outline=color, width=lw)
        # Círculo no centro
        cx, cy = S // 2, S // 2
        draw.ellipse((cx - 28, cy - 28, cx + 28, cy + 28), outline=color, width=lw)
        # Símbolo cifrão ou linhas laterais
        draw.line([(60, 100), (60, 156)], fill=color, width=lw)
        draw.line([(196, 100), (196, 156)], fill=color, width=lw)

    elif name == "configuracoes":
        # Engrenagem
        cx, cy = S // 2, S // 2
        r_out = 75
        r_in = 45
        teeth = 6
        points = []
        for i in range(teeth * 2):
            angle = i * (360 / (teeth * 2))
            rad = math.radians(angle)
            r = r_out if i % 2 == 0 else r_in + 10
            points.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
        draw.polygon(points, outline=color, width=lw)
        draw.ellipse((cx - r_in, cy - r_in, cx + r_in, cy + r_in), outline=color, width=lw)
        draw.ellipse((cx - 20, cy - 20, cx + 20, cy + 20), fill=color)

    elif name == "suporte":
        # Balão / Círculo com interrogação
        cx, cy = S // 2, S // 2
        r = 80
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=lw)
        # Interrogação ?
        draw.arc((cx - 22, cy - 50, cx + 22, cy - 6), start=180, end=380, fill=color, width=lw)
        draw.line([(cx + 2, cy - 6), (cx + 2, cy + 12)], fill=color, width=lw)
        draw.ellipse((cx - 8, cy + 26, cx + 10, cy + 44), fill=color)

    elif name == "agenda":
        # Calendário / Agenda
        x1, y1, x2, y2 = 45, 60, 211, 215
        draw.rounded_rectangle((x1, y1, x2, y2), radius=14, outline=color, width=lw)
        # Topo do calendário
        draw.line([(45, 105), (211, 105)], fill=color, width=lw)
        # Anéis do topo
        draw.line([(85, 40), (85, 75)], fill=color, width=lw)
        draw.line([(171, 40), (171, 75)], fill=color, width=lw)
        # Pontos da grade de dias
        for dx in [95, 160]:
            for dy in [140, 180]:
                draw.ellipse((dx - 12, dy - 12, dx + 12, dy + 12), fill=color)

    res = img.resize((size, size), Image.Resampling.LANCZOS)
    return res

def generate_all_assets(base_dir):
    os.makedirs(os.path.join(base_dir, "assets"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "assets", "icons"), exist_ok=True)
    
    # 1. Mascote circular
    orig_mascot = r'C:\Users\TK\.gemini\antigravity-ide\brain\73a71cc9-508c-444c-9bf1-a7d738ab6b77\hanna_mascot_1785885056294.png'
    out_mascot = os.path.join(base_dir, "assets", "hanna_mascot.png")
    create_circular_mascot(orig_mascot, out_mascot, size=(300, 300))
    
    # 2. Logo da paleta
    logo_img = draw_palette_logo(size=96)
    logo_img.save(os.path.join(base_dir, "assets", "logo_palette.png"))
    
    # 3. Ícones do menu (Normal e Ativo)
    icon_names = ["boas_vindas", "pedidos", "clientes", "agenda", "estoque", "financeiro", "configuracoes", "suporte"]
    color_normal = (90, 69, 73)   # #5A4549 (Brownish mauve)
    color_active = (255, 255, 255) # White
    
    for name in icon_names:
        img_norm = draw_vector_icon(name, color=color_normal, size=48)
        img_norm.save(os.path.join(base_dir, "assets", "icons", f"{name}_normal.png"))
        
        img_act = draw_vector_icon(name, color=color_active, size=48)
        img_act.save(os.path.join(base_dir, "assets", "icons", f"{name}_active.png"))
        
    print(f"Todos os assets gerados com sucesso para {base_dir}!")

if __name__ == "__main__":
    generate_all_assets(r"d:\Python Projetos\Atelier")
    generate_all_assets(r"d:\Python Projetos\Antigravity JANELA")
