
import streamlit as st
import re
from datetime import datetime

st.title("Gerador de Admissão / Evolução Farmácia Clínica")

modo = st.radio("Escolha o modo de formatação:", ["Admissão Ortopedia", "Evolução exames UTI"])
texto = st.text_area("Cole aqui os dados do prontuário:", height=600)

# Função para normalizar data no modo ortopedia
def normalizar_data(data):
    if re.match(r'\d{2}/\d{2}/\d{2}$', data):
        return re.sub(r'/(\d{2})$', lambda m: '/20' + m.group(1), data)
    return data

# Função antiga da ortopedia
def extrair_info(texto):
    hoje = datetime.today().strftime('%d/%m/%Y')
    ses = re.search(r'SES:\s+(\d+)', texto)
    paciente = re.search(r'Paciente:\s+([^\t\n]+)', texto)
    idade = re.search(r'Idade:\s+(\d+)', texto)

    diagnostico = ""
    padroes_diagnostico = [
        r'DIAGNÓSTICOS?:\s*((?:- .+\n?)+)',
        r'DIAGNÓSTICO:\s*((?:- .+\n?)+)',
        r'DIAGNÓSTICO:\s+([^\n]+)'
    ]
    for padrao in padroes_diagnostico:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            diagnostico = match.group(1).strip().replace('\n', ' ')
            break

    mecanismo = re.search(r'MECANISMO DO TRAUMA:\s*(.+)', texto, re.IGNORECASE)
    hda = re.search(r'HDA:\s*(.+)', texto, re.IGNORECASE)
    mecanismo_trauma = mecanismo.group(1).strip() if mecanismo else (hda.group(1).strip() if hda else "mecanismo não especificado")

    data_fratura = re.search(r'DATA DA (?:FRATURA|LES[AÃ]O):\s+(\d{2}/\d{2}/\d{2,4})', texto, re.IGNORECASE)
    data_fratura_formatada = normalizar_data(data_fratura.group(1)) if data_fratura else "-"

    cirurgia_matches = re.findall(r'DATA DA CIRURGIA:\s+(\d{2}/\d{2}/\d{2,4})(?:\s+\((.*?)\))?', texto)
    datas_cirurgia = []
    for data, medico in cirurgia_matches:
        data_formatada = normalizar_data(data)
        if medico:
            medico = re.sub(r'(?i)^Dr\.?\s*', '', medico.strip())
            datas_cirurgia.append(f"{data_formatada} (Dr. {medico.capitalize()})")
        else:
            datas_cirurgia.append(data_formatada)
    cirurgia_str = "; ".join(datas_cirurgia) if datas_cirurgia else "-"

    analgesicos = []
    analgesia_padrao = re.compile(
        r'(DIPI?RONA|TRAMADOL)[^\n]*?\n\s*(\d+)\s+Mili(?:grama|gramas)[^\n]*\n\s*(.+?)\s+(Endovenosa)',
        re.IGNORECASE
    )
    for match in analgesia_padrao.findall(texto):
        nome, dose, freq_raw, via = match
        nome = nome.capitalize()
        freq_raw = freq_raw.lower()
        if "crit" in freq_raw:
            freq = "ACM"
        elif "sos" in freq_raw:
            freq = "SOS"
        else:
            freq = re.sub(r'[^0-9x/]', '', freq_raw).replace('x', 'x') or freq_raw.strip().split()[0]
        analgesicos.append(f"{nome} {dose}mg, {freq}, {via}")
    analgesia_str = "; ".join(analgesicos) if analgesicos else "-"

    tev_tvp = "-"
    enoxa_match = re.search(
        r'ENOXAPARINA[^\n]*?\n\s*(\d+)\s+(?:UM|Miligrama.*)?\s*\n\s*(.+?)\s+(Subcutanea)',
        texto, re.IGNORECASE
    )
    if enoxa_match:
        dose, freq_raw, via = enoxa_match.groups()
        freq_raw = freq_raw.lower()
        if "crit" in freq_raw:
            freq = "ACM"
        elif "sos" in freq_raw:
            freq = "SOS"
        else:
            freq = re.sub(r'[^0-9x/]', '', freq_raw).replace('x', 'x') or freq_raw.strip().split()[0]
        tev_tvp = f"Enoxaparina {dose}mg, {freq}, {via}"

    return f"""FARMÁCIA CLÍNICA 
ADMISSÃO ORTOPEDIA 1
----------------------------------------------------------------------------
Paciente: {paciente.group(1) if paciente else '-'}; SES: {ses.group(1) if ses else '-'}; 
Idade: {idade.group(1) if idade else '-'} anos; Peso: -
Data de admissão: {hoje}
Data da entrevista: {hoje}
----------------------------------------------------------------------------
Motivo da internação:
{diagnostico}
Mecanismo do trauma:
{mecanismo_trauma}
Data da fratura: {data_fratura_formatada}
Data da cirurgia: {cirurgia_str}
----------------------------------------------------------------------------
Antecedentes: 
----------------------------------------------------------------------------
Alergias: 
----------------------------------------------------------------------------
Conciliação medicamentosa:
- Histórico obtido através de: 
- Medicamentos de uso domiciliar: 
----------------------------------------------------------------------------
Antimicrobianos:
Em uso:
- 
Uso prévio:
- 
-----------------------------------------------------------------------------
Culturas e Sorologias:
-----------------------------------------------------------------------------
Profilaxias e protocolos
- TEV/TVP: {tev_tvp}
- 
- LAMG: 
-
- Analgesia:
- {analgesia_str}
----------------------------------------------------------------------------- 
Conduta
- Realizo análise técnica da prescrição quanto à indicação, efetividade, posologia, dose, possíveis interações medicamentosas e disponibilidade na farmácia.
- Realizo visita beira a leito, encontro o paciente dormindo 
- Monitoro exames laboratoriais de **/**/****, controles e evolução clínica.
---
- Acompanho antibioticoterapia e parâmetros infecciosos: Paciente afebril, em uso de (***) D*; Leuco **.
- Paciente avaliado como risco (****), reavaliação programada para o dia: **/**/****
- Segue em acompanhamento pelo Núcleo de Farmácia Clínica.

- Estagiário ***, supervisionado por *********
- Farmacêutico ***
*******************************************************"""

# Função nova: formatação de exames UTI
def formatar_evolucao_exames(texto):
    campos = [
        "Data", "Cr", "eTFG", "Ur", "K", "Na", "Mg", "P",
        "TGO", "TGP", "FAL", "gGT", "BT", "BD", "Alb",
        "PCR", "Lc", "Bt", "Hb", "Plaq"
    ]
    resultados = {}
    for campo in campos:
        padrao = fr"{campo}\s*[:=]?\s*([\d.,]+)"
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            resultados[campo] = match.group(1).strip()

    return "Evolução exames UTI:\n" + "; ".join(
        [f"{k} {resultados.get(k, '---')}" + (" mL/min/1,73 m²" if k == "eTFG" else "") for k in campos]
    )

# Execução conforme o modo escolhido
if st.button("Gerar resultado"):
    if not texto.strip():
        st.warning("Por favor, cole o texto do prontuário.")
    else:
        if modo == "Admissão Ortopedia":
            resultado = extrair_info(texto)
        elif modo == "Evolução exames UTI":
            resultado = formatar_evolucao_exames(texto)

        st.text_area("Resultado Formatado:", resultado, height=800)
        st.download_button("📥 Baixar como .txt", resultado, file_name="formatação_farmacia.txt")
