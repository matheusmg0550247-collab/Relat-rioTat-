import streamlit as st
from fpdf import FPDF
from PIL import Image # Para verificar o tamanho das imagens
import io

# --- Função para Criar o PDF ---
# Esta é a lógica "back-end"
def criar_pdf(imagens_com_titulos):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for item in imagens_com_titulos:
        
        # Tenta codificar o título para 'latin-1' (padrão do FPDF)
        # Isso ajuda com acentos comuns, mas não com todos os caracteres
        try:
            titulo = item['titulo'].encode('latin-1', 'replace').decode('latin-1')
        except UnicodeEncodeError:
            titulo = item['titulo'] # Usa o original se falhar

        uploaded_file = item['arquivo']
        
        pdf.add_page()
        
        # --- Adiciona o Título ---
        # Definir a fonte para o título (Ex: Arial, Negrito, 16)
        pdf.set_font('Arial', 'B', 16)
        # Escreve o título. O 'ln=True' quebra a linha depois
        pdf.cell(0, 10, titulo, ln=True, align='C') 
        
        # Adiciona um espaço
        pdf.ln(10)

        # --- Adiciona a Imagem ---
        # Precisamos ler os bytes do arquivo enviado
        # Usamos 'io.BytesIO' para que a biblioteca de PDF possa ler o arquivo em memória
        image_bytes = io.BytesIO(uploaded_file.getvalue())
        
        # Carrega a imagem com PIL para obter as dimensões e calcular o aspect ratio
        pil_image = Image.open(image_bytes)
        img_width, img_height = pil_image.size
        aspect_ratio = img_height / img_width
        
        # Define a largura da imagem no PDF (ex: 190mm, a página A4 tem 210mm)
        pdf_img_width = 190
        pdf_img_height = pdf_img_width * aspect_ratio
        
        # Reseta o "ponteiro" dos bytes para o início
        image_bytes.seek(0)
        
        # Pega o tipo da imagem (jpg, png) do nome do arquivo
        img_type = uploaded_file.type.split('/')[-1]

        # Adiciona a imagem ao PDF
        pdf.image(image_bytes, x=None, y=None, w=pdf_img_width, type=img_type)

    # Gera o PDF em memória como bytes
    # --- ESTA É A LINHA CORRIGIDA ---
    pdf_output = pdf.output(dest='S')
    
    return pdf_output

# --- Interface do Streamlit (Front-End) ---

st.title("Gerador de PDF a partir de Imagens")

# 1. Upload das fotos
uploaded_files = st.file_uploader(
    "Escolha suas fotos",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} fotos carregadas!")
    
    imagens_com_titulos = []
    
    # 2. Formulário para os títulos
    with st.form(key="titulos_form"):
        st.subheader("Adicione os títulos para cada imagem:")
        
        # Loop para criar um campo de texto para cada imagem
        for i, file in enumerate(uploaded_files):
            st.image(file, width=200) # Mostra uma miniatura
            titulo = st.text_input(f"Título para: {file.name}", key=f"titulo_{i}")
            
            imagens_com_titulos.append({
                "arquivo": file,
                "titulo": titulo
            })
        
        # 3. Botão para gerar
        submit_button = st.form_submit_button(label="Gerar PDF")

    # 4. Lógica de Geração e Download
    if submit_button:
        # Verifica se todos os títulos foram preenchidos
        if all(item['titulo'] for item in imagens_com_titulos):
            with st.spinner("Gerando seu PDF..."):
                pdf_bytes = criar_pdf(imagens_com_titulos)
            
            st.success("PDF Gerado com sucesso!")
            
            # 5. Botão de Download
            st.download_button(
                label="Baixar PDF",
                data=pdf_bytes,
                file_name="meu_album.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Por favor, preencha todos os títulos.")
