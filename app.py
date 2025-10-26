import streamlit as st
from fpdf import FPDF
from PIL import Image
import io

# --- Função para Criar o PDF ---
def criar_pdf(imagens_com_titulos, numero_projeto):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- Configurações de Borda ---
    borda_cor_r = 150 
    borda_cor_g = 150
    borda_cor_b = 150
    borda_espessura = 0.5 
    borda_margem = 10 

    # --- Página de Rosto ---
    pdf.add_page()
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 30, 'RELATÓRIO FOTOGRÁFICO', ln=True, align='C')
    
    pdf.ln(10) # Espaço
    
    pdf.set_font('Arial', '', 18)
    pdf.cell(0, 15, f'Projeto nº: {numero_projeto}', ln=True, align='C')
    
    pdf.ln(20) # Espaço
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Responsável Técnico:', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 7, 'JOSE EUSTAQUIO DE FARIA', ln=True, align='C')
    pdf.cell(0, 7, 'Título profissional: ENGENHEIRO CIVIL', ln=True, align='C')
    pdf.cell(0, 7, 'RNP: 1402023162', ln=True, align='C')
    pdf.cell(0, 7, 'Registro: MG0000023221D MG', ln=True, align='C')
    
    pdf.ln(30) # Espaço

    # --- Inserir a imagem LOGO (arquivo "Relatório Fotográfico.jpg") ---
    jjms_logo_path = "Relatório Fotográfico.jpg" 
    
    logo_width = 60 # Largura do logo no PDF (em mm)
    x_pos_logo = (pdf.w - logo_width) / 2
    
    try:
        pdf.image(jjms_logo_path, x=x_pos_logo, y=pdf.get_y(), w=logo_width)
    except FileNotFoundError:
        pdf.set_font('Arial', 'I', 10) 
        pdf.set_text_color(255, 0, 0) # Vermelho
        pdf.cell(0, 10, "(Erro: Imagem 'Relatório Fotográfico.jpg' nao encontrada)", ln=True, align='C')
        pdf.set_text_color(0, 0, 0) # Reseta a cor
    except Exception as e:
        pdf.set_font('Arial', 'I', 10) 
        pdf.set_text_color(255, 0, 0) 
        pdf.cell(0, 10, f"(Erro ao carregar logo: {e})", ln=True, align='C')
        pdf.set_text_color(0, 0, 0)

    # --- Borda para a página de rosto ---
    pdf.set_draw_color(borda_cor_r, borda_cor_g, borda_cor_b)
    pdf.set_line_width(borda_espessura)
    pdf.rect(borda_margem, borda_margem, pdf.w - 2 * borda_margem, pdf.h - 2 * borda_margem)


    # --- Páginas com Fotos e Títulos ---
    for item in imagens_com_titulos:
        try:
            titulo = item['titulo'].encode('latin-1', 'replace').decode('latin-1')
        except UnicodeEncodeError:
            titulo = item['titulo'] 

        uploaded_file = item['arquivo']
        
        pdf.add_page()
        
        # --- Borda para as páginas de foto ---
        pdf.set_draw_color(borda_cor_r, borda_cor_g, borda_cor_b)
        pdf.set_line_width(borda_espessura)
        pdf.rect(borda_margem, borda_margem, pdf.w - 2 * borda_margem, pdf.h - 2 * borda_margem)
        
        # --- Posição Y inicial (logo abaixo da borda) ---
        y_start = borda_margem + 10 # 10mm de margem superior interna
        pdf.set_y(y_start)

        # --- Adiciona a Imagem (ANTES do Título) ---
        image_bytes = io.BytesIO(uploaded_file.getvalue())
        
        try:
            pil_image = Image.open(image_bytes)
        except Exception as e:
            st.error(f"Não foi possível ler o arquivo: {uploaded_file.name}. Erro: {e}")
            continue 

        img_width, img_height = pil_image.size
        if img_width == 0 or img_height == 0:
            st.error(f"Imagem inválida: {uploaded_file.name} tem dimensão zero.")
            continue
            
        aspect_ratio = img_height / img_width
        
        # --- AJUSTE RADICAL AQUI ---
        # Definimos um 'box' máximo bem menor
        # A imagem (paisagem ou retrato) será forçada a caber
        # em um quadrado de 120mm x 120mm, mantendo a proporção.
        # (Antes, os limites eram ~170mm e ~197mm)
        pdf_img_max_width = 120 # Largura máxima fixa (em mm)
        pdf_img_max_height = 120 # Altura máxima fixa (em mm)
        
        # Lógica de redimensionamento
        if aspect_ratio > 1: # Imagem mais alta (retrato)
            pdf_img_height = pdf_img_max_height
            pdf_img_width = pdf_img_height / aspect_ratio
            if pdf_img_width > pdf_img_max_width:
                pdf_img_width = pdf_img_max_width
                pdf_img_height = pdf_img_width * aspect_ratio
        else: # Imagem mais larga (paisagem) ou quadrada
            pdf_img_width = pdf_img_max_width
            pdf_img_height = pdf_img_width * aspect_ratio
            if pdf_img_height > pdf_img_max_height:
                pdf_img_height = pdf_img_max_height
                pdf_img_width = pdf_img_height / aspect_ratio
        
        image_bytes.seek(0)
        img_type = uploaded_file.type.split('/')[-1]

        # Centraliza a imagem
        x_pos = (pdf.w - pdf_img_width) / 2
        
        # Desenha a imagem na posição Y inicial
        pdf.image(image_bytes, x=x_pos, y=y_start, w=pdf_img_width, type=img_type)

        # --- Adiciona o Título (DEPOIS da Imagem) ---
        # Define a posição Y para abaixo da imagem + 5mm de espaço
        pdf.set_y(y_start + pdf_img_height + 5) 
        
        pdf.set_font('Arial', 'B', 14)
        # Centraliza o texto
        pdf.cell(0, 10, titulo, ln=True, align='C')
    
    # --- Geração final do PDF ---
    try:
        pdf_bytes = pdf.output(dest='S')
        pdf_file_object = io.BytesIO(pdf_bytes)
        return pdf_file_object
    except Exception as e:
        st.error(f"Erro ao gerar o PDF final: {e}")
        return None

# --- Interface do Streamlit (Front-End) ---

st.set_page_config(layout="centered")

try:
    st.image("Tatá.jpg", use_container_width=True)
except FileNotFoundError:
    st.error("Imagem 'Tatá.jpg' não encontrada. Verifique se está no repositório GitHub.")
except Exception as e:
    st.error(f"Não foi possível carregar a imagem 'Tatá.jpg': {e}")


st.title("Gerador de Relatório Fotográfico 📷📄")

# Campo para o Número do Projeto
numero_projeto = st.text_input("Número do Projeto", value="XXXXX", help="Informe o número do projeto para a página de rosto.")

# Upload das fotos
uploaded_files = st.file_uploader(
    "1. Escolha suas fotos",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} fotos carregadas!")
    
    imagens_com_titulos = []
    
    st.markdown("---")
    st.subheader("2. Adicione os títulos para cada imagem:")
    
    with st.form(key="titulos_form"):
        
        for i, file in enumerate(uploaded_files):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(file, width=150) # Miniatura
            with col2:
                titulo = st.text_input(f"Título para: {file.name}", key=f"titulo_{i}")
            
            imagens_com_titulos.append({
                "arquivo": file,
                "titulo": titulo
            })
        
        st.markdown("---")
        submit_button = st.form_submit_button(label="3. Gerar PDF do Relatório")

    if submit_button:
        if not numero_projeto or numero_projeto == "XXXXX":
            st.error("Por favor, preencha um número de projeto válido.")
        elif all(item['titulo'] for item in imagens_com_titulos):
            with st.spinner("Gerando seu Relatório Fotográfico em PDF..."):
                pdf_file_object = criar_pdf(imagens_com_titulos, numero_projeto) 
            
            if pdf_file_object:
                st.success("Relatório PDF Gerado com sucesso!")
                
                st.download_button(
                    label="4. Baixar Relatório PDF",
                    data=pdf_file_object,
                    file_name=f"relatorio_fotografico_projeto_{numero_projeto}.pdf",
                    mime="application/pdf"
                )
        else:
            st.error("Por favor, preencha todos os títulos das fotos.")
