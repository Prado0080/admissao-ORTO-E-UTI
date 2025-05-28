import streamlit as st
import re

# Função para extrair dados laboratoriais do texto
def extrair_dados(texto):
    padroes = {
        'Cr': r"(?i)(?<=CREATININA[\s\S]{0,200}?Resultado\W{0,5}:?\s*)(\d+[\.,]\d+)",
        'eTFG': r"(?i)(?<=CKD-EPI[\s\S]{0,200}?)\b(\d{1,3})\s*mL/min/1,73\s*m²",
        'Ur': r"(?i)(?<=UREIA[\s\S]{0,200}?Resultado\W{0,5}:?\s*)(\d+[\.,]\d+)",
        'K': r"(?i)(?<=POT[ÁA]SSIO[\s\S]{0,200}?Resultado\W{0,5}:?\s*)(\d+[\.,]\d+)",
        'Na': r"(?i)(?<=S[ÓO]DIO[\s\S]{0,200}?Resultado\W{0,5}:?\s*)(\d+[\.,]\d+)",
        'Mg': r"(?i)(?<=MAGN[ÊE]SIO[\s\S]{0,200}?Resultado\W{0,5}:?\s*)(\d+[\.,]\d+)",
        'P': r"(?i)(?<=F[ÓO]SFORO[\s\S]{0,200}?Resultado\W{0,5}:?\s*)(\d+[\.,]\d+)",
        'TGO': r"(?i)(?<=TGO[\s\S]{0,200}?Resultado\W{0,5}:?\s*)(\d+[\.,]\d+)",
        'TGP': r"(?i)(?<=TGP[\s\S]{0,200}?Resultado\W{0,5}:?\s*)(\d+[\.,]\d+)",
        'FAL': r"(?i)(?<=FOSFATASE\s+ALCALINA[\s\S]{0,200}?Resultado\W{0,5}:?\s*)(\d+[\.,]\d+)",
        'gGT': r"(?i)(?<=GAMA\s*GT[\s\S]{0,200}?Resultado\W{0,5}:?\s*)(\d+[\.,]\d+)",
        'BT': r"(?i)(?<=BILIRRUBINA\s+TOTAL[\s\S]{0,200}?Resultado\W{0,5}:?\s*)(\d+[\.,]\d+)",
        'BD': r"(?i)(?<=BILIRRUBINA\s+DIRETA[\s\S]{0,200}?Resultado\W{0,5}:?\s*)(\d+[\.,]\d+)",
        'Alb': r"(?i)(?<=ALBUMINA[\s\S]{0,200}?Resultado\W{0,5}:?\s*)(\d+[\.,]\d+)|(?<=Albumina\s*[:\-\s]{0,5})(\d+[\.,]\d+)",
        'PCR': r"(?i)(?<=PROTE[IÍ]NA\s+C\s+REATIVA[\s\S]{0,200}?Resultado\W{0,5}:?\s*)(\d+[\.,]\d+)",
        'Lc': r"(?i)(Leuc[óo]citos\s+Totais\s*:\s*)(\d+[\.,]?\d*)|\|\s*Lc\s*([\d.,]+)",
        'Bt': r"(?i)(?<=Bastonetes[\s\S]{0,100}?\s*:\s*)(\d+[\.,]?\d*)%|\|\s*Bt\s*(\d+[.,]?\d*)%",
        'Hb': r"(?i)(Hemoglobina\s*[:\-]?\s*)(\d+[\.,]?\d*)|\|\s*Hb\s*([\d.,]+)",
        'Plaq': r"(?i)(Plaquetas\s*[:\-]?\s*)(\d+[\.,]?\d*)|\|\s*Plaq\s*([\d.,]+)",
    }

    resultados = {}
    for chave, padrao in padroes.i'tems():
        match = re.search(padrao, texto)
        if match:
            for g in match.groups():
                if g:
                    resultados[chave] = g.replace(',', '.').strip()
                    break
        else:
            resultados[chave] = "XX"

    data_coleta_match = re.search(r"(?i)Data de Coleta[:\-\s]+(\d{2}/\d{2}/\d{4})", texto)
    data_coleta = data_coleta_match.group(1) if data_coleta_match else "Data nao encontrada"

    resultado_formatado = f"Data de coleta: {data_coleta} | " + " | ".join([f"{k} {v}" for k, v in resultados.items()])
    resultado_sem_xx = f"Data de coleta: {data_coleta} | " + " | ".join([f"{k} {v}" for k, v in resultados.items() if v != "XX"])

    return resultado_formatado, resultado_sem_xx


# Interface Streamlit
st.title("Evolução de Exames UTI")
texto_input = st.text_area("Cole aqui o texto do prontuário com os exames:", height=500)

if st.button("Extrair e formatar"):
    if texto_input:
        resultado1, resultado2 = extrair_dados(texto_input)

        st.subheader("Formato completo (com XX nos ausentes):")
        st.code(resultado1)

        st.subheader("Formato limpo (somente resultados encontrados):")
        st.code(resultado2)
    else:
        st.warning("Por favor, cole o texto do prontuário.")
