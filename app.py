import streamlit as st
from fpdf import FPDF
from PIL import Image
import io  # <-- Importamos a biblioteca io

# --- Função para Criar o PDF ---
def criar_pdf(imagens_com_titulos):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for item in imagens_com_titulos:
        
        try:
            titulo = item['titulo'].encode('latin-1', 'replace').decode('latin-1')
        except UnicodeEncodeError:
            titulo = item['titulo'] 

        uploaded_file = item['arquivo']
        
        pdf.add_page()
        
        # --- Adiciona o Título ---
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, titulo, ln=True, align='C') 
        pdf.ln(10)

        # --- Adiciona a Imagem ---
        image_bytes = io.BytesIO(uploaded_file.getvalue())
        
        pil_image = Image.open(image_bytes)
        img_width, img_height = pil_image.size
        aspect_ratio = img_height / img_width
        
        pdf_img_width = 190
        pdf_img_height = pdf_img_width * aspect_ratio
        
        image_bytes.seek(0)
        
        img_type = uploaded_file.type.split('/')[-1]

        pdf.image(image_bytes, x=None, y=None, w=pdf_img_width, type=img_type)

    # --- ALTERAÇÃO AQUI (Parte 1) ---
    # 1. Geramos os bytes como antes
    pdf_bytes = pdf.output(dest='S')
    
    # 2. "Embrulhamos" os bytes em um objeto de arquivo em memória
    pdf_file_object = io.BytesIO(pdf_bytes)
    
    # 3. Retornamos o objeto de arquivo
    return pdf_file_object

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
        
        for i, file in enumerate(uploaded_files):
            st.image(file, width=200) 
            titulo = st.text_input(f"Título para: {file.name}", key=f"titulo_{i}")
            
            imagens_com_titulos.append({
                "arquivo": file,
                "titulo": titulo
            })
        
        submit_button = st.form_submit_button(label="Gerar PDF")

    # 4. Lógica de Geração e Download
    if submit_button:
        if all(item['titulo'] for item in imagens_com_titulos):
            with st.spinner("Gerando seu PDF..."):
                
                # --- ALTERAÇÃO AQUI (Parte 2) ---
                # A variável agora contém o objeto de arquivo
                pdf_file_object = criar_pdf(imagens_com_titulos) 
            
            st.success("PDF Gerado com sucesso!")
            
            # 5. Botão de Download
            st.download_button(
                label="Baixar PDF",
                data=pdf_file_object,  # <-- Passamos o objeto de arquivo aqui
                file_name="meu_album.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Por favor, preencha todos os títulos.")
