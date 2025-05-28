import streamlit as st
import re
import unicodedata

def remover_acentos(txt):
    """Remove acentos para facilitar buscas insensíveis."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', txt)
        if unicodedata.category(c) != 'Mn'
    )

def extrair_valores_robusto(prontuario):
    texto_original = prontuario
    texto = remover_acentos(prontuario).lower()

    # Extrai a data de coleta
    padrao_data = r'(data\s*(da\s*)?coleta|coleta\s*em)[:\-]?\s*(\d{2}/\d{2}/\d{4})'
    data_coleta_match = re.search(padrao_data, texto)
    data_coleta = data_coleta_match.group(3) if data_coleta_match else 'Data nao encontrada'

    exames_formas = {
        "Cr": [r'creatinina', r'creat'],
        "eTFG": [r'etfg', r'estimativa da taxa de filtracao glomerular', r'taxa de filtracao glomerular', r'tfg'],
        "Ur": [r'ureia'],
        "K": [r'potassio', r'k\W'],
        "Na": [r'sodio', r'na\W'],
        "Mg": [r'magnesio', r'mg\W'],
        "P": [r'fosforo', r'p\W'],
        "TGO": [r'tgo', r'aspartato aminotransferase', r'asat'],
        "TGP": [r'tgp', r'alanina aminotransferase', r'alat'],
        "FAL": [r'fosfatase alcalina', r'fal', r'fa alcalina'],
        "gGT": [r'ggt', r'gamma glutamiltransferase', r'gamma gt'],
        "BT": [r'bilirrubina total', r'bt\b', r'bilirrubina total'],
        "BD": [r'bilirrubina direta', r'bd\b', r'bilirrubina direta'],
        "Alb": [r'albumina', r'alb'],
        "PCR": [r'proteina c reativa', r'pcr'],
        "Lc": [r'leucocitos', r'leucocitos totais', r'leucocitose'],
        "Bt": [r'bat', r'bastonetes', r'contagem de bastonetes'],
        "Hb": [r'hemoglobina', r'hb\b'],
        "Plaq": [r'plaquetas', r'plaq']
    }

    def encontrar_valor(exame_patterns):
        for pattern in exame_patterns:
            regex = rf'{pattern}[^0-9,\.\-]*[:\-]?\s*([\-]?\d+[.,]?\d*)'
            match = re.search(regex, texto)
            if match:
                valor = match.group(1).replace(',', '.')
                return valor
        return None

    resultados = {}
    for exame, patterns in exames_formas.items():
        val = encontrar_valor(patterns)
        resultados[exame] = val

    # Tratamento especial para eTFG (com unidades)
    if resultados["eTFG"] is None:
        match_etfg = re.search(r'(estimativa da taxa de filtracao glomerular|etfg|tfg)[^0-9]*[:\-]?\s*(\d+[.,]?\d*)\s*m[lL]/min', texto)
        if match_etfg:
            resultados["eTFG"] = match_etfg.group(2).replace(',', '.')

    # Construção do resultado completo (com XX)
    partes_completas = [f"Data de coleta: {data_coleta}"]

    for chave in ["Cr", "eTFG", "Ur", "K", "Na", "Mg", "P", "TGO", "TGP", "FAL", "gGT", "BT", "BD", "Alb", "PCR", "Lc", "Bt", "Hb", "Plaq"]:
        valor = resultados.get(chave)
        if valor is None:
            valor = "XX"
        if chave == "eTFG":
            partes_completas.append(f"{chave} {valor} mL/min/1,73 m²")
        else:
            partes_completas.append(f"{chave} {valor}")

    resultado_completo = " | ".join(partes_completas)

    # Construção do resultado filtrado (somente valores encontrados, exclui XX)
    partes_filtradas = [f"Data de coleta: {data_coleta}"]

    for chave in ["Cr", "eTFG", "Ur", "K", "Na", "Mg", "P", "TGO", "TGP", "FAL", "gGT", "BT", "BD", "Alb", "PCR", "Lc", "Bt", "Hb", "Plaq"]:
        valor = resultados.get(chave)
        if valor is not None:
            if chave == "eTFG":
                partes_filtradas.append(f"{chave} {valor} mL/min/1,73 m²")
            else:
                partes_filtradas.append(f"{chave} {valor}")

    resultado_filtrado = " | ".join(partes_filtradas)

    return resultado_completo, resultado_filtrado


def main():
    st.title("Extração de Exames Laboratoriais - Prontuário")
    st.write("Cole o texto do prontuário no campo abaixo e clique em 'Extrair'.")

    prontuario_texto = st.text_area("Texto do Prontuário", height=300)

    if st.button("Extrair"):
        if not prontuario_texto.strip():
            st.warning("Por favor, cole o texto do prontuário para extrair os dados.")
        else:
            completo, filtrado = extrair_valores_robusto(prontuario_texto)
            st.subheader("Resultado Completo (com XX):")
            st.code(completo)
            st.subheader("Resultado Filtrado (sem XX):")
            st.code(filtrado)


if __name__ == "__main__":
    main()
