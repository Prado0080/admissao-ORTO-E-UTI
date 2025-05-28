import streamlit as st
import re

st.title("Formatador de Evolução de Exames - UTI")

texto_input = st.text_area("Cole aqui o texto do prontuário com os exames:", height=400)

def extrair_data_coleta(texto):
    match = re.search(r'Data\s+de\s+Coleta:\s*(\d{2}/\d{2}/\d{4})', texto, re.IGNORECASE)
    if match:
        return match.group(1)
    return "Data nao encontrada"

def encontrar_valor(exame_patterns, texto_original, texto_limpo):
    # Primeiro tenta encontrar pelo método tradicional (linha única)
    for pattern in exame_patterns:
        regex = rf'{pattern}[^0-9,\.\-]*[:\-]?\s*([\-]?\d+[.,]?\d*)'
        match = re.search(regex, texto_limpo)
        if match:
            return match.group(1).replace(',', '.')

    # Se não encontrar, tenta encontrar em bloco com "Resultado:"
    for pattern in exame_patterns:
        padrao_bloco = rf'({pattern}.*?)resultado[^0-9,\.\-]*[:\-]?\s*([\-]?\d+[.,]?\d*)'
        match = re.search(padrao_bloco, texto_original, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(2).replace(',', '.')

    return None

def formatar_resultado(data_coleta, resultados, remover_xx=False):
    partes = [f"Data de coleta: {data_coleta}"]
    for exame, valor in resultados.items():
        if remover_xx and (valor is None or valor == "XX"):
            continue
        if exame == "eTFG" and valor not in [None, "XX"]:
            partes.append(f"eTFG {valor} mL/min/1,73 m²")
        else:
            partes.append(f"{exame} {valor if valor else 'XX'}")
    return " | ".join(partes)

if texto_input:
    # Original mantém quebras de linha para facilitar blocos de resultado
    texto_original = texto_input
    texto_limpo = re.sub(r'\s+', ' ', texto_input)  # versão sem quebras para busca direta

    data_coleta = extrair_data_coleta(texto_original)

    exames_formas = {
        "Cr": ["creatinina"],
        "eTFG": ["etfg", "tfgr", "tfg"],
        "Ur": ["ureia", "uréia"],
        "K": ["potássio", "potassio"],
        "Na": ["sódio", "sodio"],
        "Mg": ["magnésio", "magnesio"],
        "P": ["fósforo", "fosforo"],
        "TGO": ["tgo", "ast"],
        "TGP": ["tgp", "alt"],
        "FAL": ["fosfatase alcalina", "fal"],
        "gGT": ["ggt", "gama gt", "gama-glutamil transferase"],
        "BT": ["bilirrubina total", "bt"],
        "BD": ["bilirrubina direta", "bd"],
        "Alb": ["albumina"],
        "PCR": ["proteína c reativa", "pcr"],
        "Lc": ["leucócitos", "leucocitos"],
        "Bt": ["bastões", "bastoes"],
        "Hb": ["hemoglobina", "hb"],
        "Plaq": ["plaquetas", "plaq"]
    }

    resultados = {}
    for exame, patterns in exames_formas.items():
        val = encontrar_valor(patterns, texto_original, texto_limpo)
        resultados[exame] = val

    resultado_completo = formatar_resultado(data_coleta, resultados, remover_xx=False)
    resultado_filtrado = formatar_resultado(data_coleta, resultados, remover_xx=True)

    st.subheader("🧾 Resultado completo (com XX onde não encontrado):")
    st.code(resultado_completo, language='text')

    st.subheader("🧼 Resultado limpo (somente exames encontrados):")
    st.code(resultado_filtrado, language='text')
