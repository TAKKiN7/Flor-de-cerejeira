import os
from datetime import datetime
from tkinter import filedialog, messagebox

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class PDFService:
    """Gerador universal de relatórios PDF estilizados para a Flor de Cerejeira Creative Atelier."""

    @staticmethod
    def exportar_tabela_pdf(titulo_documento, colunas_titulos, dados_linhas, totais_info=None, base_dir=None, parent_window=None, orientacao_paisagem=True):
        """
        Abre caixa de diálogo para o usuário escolher o local de salvamento e gera o relatório PDF.
        """
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        filename_sugerido = f"Relatorio_{titulo_documento.replace(' ', '_')}.pdf"
        
        filepath = filedialog.asksaveasfilename(
            title=f"Salvar PDF - {titulo_documento}",
            defaultextension=".pdf",
            initialfile=filename_sugerido,
            filetypes=[("Arquivo PDF", "*.pdf"), ("Todos os Arquivos", "*.*")],
            parent=parent_window
        )

        if not filepath:
            return False  # Usuário cancelou a seleção

        try:
            pagesize = landscape(A4) if orientacao_paisagem else A4
            doc = SimpleDocTemplate(
                filepath,
                pagesize=pagesize,
                leftMargin=36,
                rightMargin=36,
                topMargin=36,
                bottomMargin=36
            )

            story = []
            styles = getSampleStyleSheet()

            # Estilos personalizados de texto
            style_brand = ParagraphStyle(
                'BrandTitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=18,
                leading=22,
                textColor=colors.HexColor('#5A2C34'),
                alignment=TA_CENTER
            )
            
            style_subbrand = ParagraphStyle(
                'BrandSubtitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=10,
                leading=12,
                textColor=colors.HexColor('#8E6971'),
                alignment=TA_CENTER
            )
            
            style_doc_title = ParagraphStyle(
                'DocTitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=14,
                leading=16,
                textColor=colors.HexColor('#F59CA9'),
                alignment=TA_CENTER
            )
            
            style_timestamp = ParagraphStyle(
                'Timestamp',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=8,
                leading=10,
                textColor=colors.HexColor('#685458'),
                alignment=TA_CENTER
            )

            style_cell_header = ParagraphStyle(
                'CellHeader',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=9,
                leading=11,
                textColor=colors.HexColor('#5A2C34'),
                alignment=TA_LEFT
            )

            style_cell_body = ParagraphStyle(
                'CellBody',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=9,
                leading=11,
                textColor=colors.HexColor('#331B20'),
                alignment=TA_LEFT
            )

            style_total_label = ParagraphStyle(
                'TotalLabel',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=10,
                leading=12,
                textColor=colors.HexColor('#5A2C34'),
                alignment=TA_LEFT
            )

            # --- Cabeçalho com Logo, Marca e Mascote ---
            assets_dir = os.path.join(base_dir, "assets")
            logo_path = os.path.join(assets_dir, "logo_palette.png")
            mascot_path = os.path.join(assets_dir, "hanna_mascot.png")

            img_logo = RLImage(logo_path, width=54, height=54) if os.path.exists(logo_path) else Paragraph("", styles['Normal'])
            img_mascot = RLImage(mascot_path, width=54, height=54) if os.path.exists(mascot_path) else Paragraph("", styles['Normal'])

            data_hora_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")

            text_center_p = [
                Paragraph("Flor de cerejeira", style_brand),
                Paragraph("CREATIVE ATELIER", style_subbrand),
                Spacer(1, 4),
                Paragraph(f"<b>{titulo_documento}</b>", style_doc_title),
                Paragraph(f"Gerado em: {data_hora_atual}", style_timestamp)
            ]

            header_table_data = [[img_logo, text_center_p, img_mascot]]
            
            # Larguras do cabeçalho
            page_w = doc.width
            col_img_w = 60
            col_text_w = page_w - (col_img_w * 2)

            header_table = Table(header_table_data, colWidths=[col_img_w, col_text_w, col_img_w])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ]))

            story.append(header_table)
            story.append(Spacer(1, 10))
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#F59CA9'), spaceAfter=14))

            # --- Tabela Principal ---
            # Construir cabeçalhos formatados em Paragraph
            table_data = []
            hdr_row = [Paragraph(str(col), style_cell_header) for col in colunas_titulos]
            table_data.append(hdr_row)

            for linha in dados_linhas:
                row_cells = []
                for item in linha:
                    val_str = str(item) if item is not None else "-"
                    row_cells.append(Paragraph(val_str, style_cell_body))
                table_data.append(row_cells)

            # Largura de cada coluna proporcional
            num_cols = len(colunas_titulos)
            col_w = page_w / num_cols
            col_widths = [col_w] * num_cols

            main_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            
            t_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FDF4F5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#5A2C34')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#F7E2E5')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#F2DFE2')),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]

            # Cores alternadas para as linhas
            for r in range(1, len(table_data)):
                if r % 2 == 0:
                    t_style.append(('BACKGROUND', (0, r), (-1, r), colors.HexColor('#FDF8F9')))

            main_table.setStyle(TableStyle(t_style))
            story.append(main_table)

            # --- Bloco de Totais / Resumo (opcional) ---
            if totais_info and isinstance(totais_info, dict):
                story.append(Spacer(1, 14))
                totais_rows = []
                for label, val in totais_info.items():
                    totais_rows.append([
                        Paragraph(f"<b>{label}:</b>", style_total_label),
                        Paragraph(f"<b>{val}</b>", style_total_label)
                    ])
                
                tot_table = Table(totais_rows, colWidths=[page_w * 0.7, page_w * 0.3])
                tot_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FDF4F5')),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#F59CA9')),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#F7E2E5')),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(tot_table)

            # Gerar o arquivo PDF
            doc.build(story)

            messagebox.showinfo(
                "PDF Gerado com Sucesso",
                f"O relatório PDF '{titulo_documento}' foi salvo com sucesso em:\n\n{filepath}",
                parent=parent_window
            )
            return True

        except Exception as e:
            messagebox.showerror(
                "Erro ao Gerar PDF",
                f"Ocorreu um erro ao criar o arquivo PDF:\n{str(e)}",
                parent=parent_window
            )
            return False

    @staticmethod
    def gerar_pdf_orcamento(nome_cliente, data_emissao, valor_orcamento, base_dir=None, parent_window=None):
        """
        Gera a Proposta Comercial de Orçamento personalizada em PDF utilizando o modelo base.
        Solicita ao usuário onde salvar o arquivo gerado.
        """
        import io
        from pypdf import PdfReader, PdfWriter
        from reportlab.pdfgen import canvas
        from reportlab.lib.colors import HexColor

        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        template_path = os.path.join(base_dir, "assets", "pdf_base_orcamento.pdf")

        if not os.path.exists(template_path):
            messagebox.showerror("Erro de Arquivo", f"O modelo base de PDF não foi encontrado em:\n{template_path}", parent=parent_window)
            return False

        nome_sugerido = f"Orcamento_{nome_cliente.replace(' ', '_')}.pdf" if nome_cliente else "Orcamento_Flor_de_Cerejeira.pdf"

        filepath = filedialog.asksaveasfilename(
            title="Salvar Orçamento em PDF",
            defaultextension=".pdf",
            initialfile=nome_sugerido,
            filetypes=[("Arquivo PDF", "*.pdf"), ("Todos os Arquivos", "*.*")],
            parent=parent_window
        )

        if not filepath:
            return False

        try:
            reader = PdfReader(template_path)
            writer = PdfWriter()

            # --- OVERLAY PÁGINA 1: Nome do Cliente e Data de Emissão ---
            packet1 = io.BytesIO()
            can1 = canvas.Canvas(packet1, pagesize=(595.5, 842.25))

            # Tampar o placeholder 'N O M E D O C L I E N T E'
            can1.setFillColor(HexColor('#FEFEFE'))
            can1.rect(58, 842.25 - 198, 350, 24, fill=1, stroke=0)

            can1.setFillColor(HexColor('#5A2C34'))
            can1.setFont('Helvetica-Bold', 14)
            can1.drawString(60, 842.25 - 192, nome_cliente.upper() if nome_cliente else "CLIENTE")

            # Tampar o placeholder 'DATA DA EMISSÃO'
            can1.setFillColor(HexColor('#FEFEFE'))
            can1.rect(58, 842.25 - 305, 200, 38, fill=1, stroke=0)

            # Desenhar a data de emissao exatamente após 'Emitido em:'
            can1.setFillColor(HexColor('#685458'))
            can1.setFont('Helvetica-Bold', 12)
            can1.drawString(146, 842.25 - 251.58, data_emissao if data_emissao else datetime.now().strftime("%d/%m/%Y"))

            can1.save()
            packet1.seek(0)
            overlay1 = PdfReader(packet1).pages[0]

            # --- OVERLAY PÁGINA 4: Valor do Orçamento ---
            packet4 = io.BytesIO()
            can4 = canvas.Canvas(packet4, pagesize=(595.5, 842.25))

            # Tampar o placeholder '*VALOR DO ORÇAMENTO*.'
            can4.setFillColor(HexColor('#FEFEFE'))
            can4.rect(118, 842.25 - 290, 375, 40, fill=1, stroke=0)

            can4.setFillColor(HexColor('#331B20'))
            can4.setFont('Helvetica', 11)
            txt_frase = "O valor do bordado nesse estilo no ateliê é "
            can4.drawString(121, 842.25 - 268, txt_frase)

            w_frase = can4.stringWidth(txt_frase, 'Helvetica', 11)
            can4.setFont('Helvetica-Bold', 12)
            can4.setFillColor(HexColor('#5A2C34'))
            can4.drawString(121 + w_frase, 842.25 - 268, f"{valor_orcamento}.")

            can4.save()
            packet4.seek(0)
            overlay4 = PdfReader(packet4).pages[0]

            # Mesclar overlays com as páginas do PDF modelo
            page1 = reader.pages[0]
            page1.merge_page(overlay1)

            page4 = reader.pages[3]
            page4.merge_page(overlay4)

            for p in reader.pages:
                writer.add_page(p)

            with open(filepath, "wb") as out_f:
                writer.write(out_f)

            messagebox.showinfo(
                "Orçamento Gerado com Sucesso",
                f"O PDF do Orçamento foi gerado e salvo com sucesso em:\n\n{filepath}",
                parent=parent_window
            )
            return True

        except Exception as e:
            messagebox.showerror(
                "Erro ao Gerar Orçamento",
                f"Ocorreu um erro ao processar o PDF de Orçamento:\n{str(e)}",
                parent=parent_window
            )
            return False
