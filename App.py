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

# Função antiga da ortopedia (exatamente a que você enviou)
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

# Função nova para Evolução exames UTI
def extrair_info_evolucao(texto):
    # Extrai as datas e valores laboratoriais de forma simples, exemplo:
    # Ajuste os padrões conforme seu formato real dos exames no texto
    padrao_valores = {
        "Cr": r"Cr\s*[:=]\s*([\d,.]+)",
        "eTFG": r"eTFG\s*[:=]\s*([\d,.]+)",
        "Ur": r"Ur\s*[:=]\s*([\d,.]+)",
        "K": r"K\s*[:=]\s*([\d,.]+)",
        "Na": r"Na\s*[:=]\s*([\d,.]+)",
        "Mg": r"Mg\s*[:=]\s*([\d,.]+)",
        "P": r"P\s*[:=]\s*([\d,.]+)",
        "TGO": r"TGO\s*[:=]\s*([\d,.]+)",
        "TGP": r"TGP\s*[:=]\s*([\d,.]+)",
        "FAL": r"FAL\s*[:=]\s*([\d,.]+)",
        "gGT": r"gGT\s*[:=]\s*([\d,.]+)",
        "BT": r"BT\s*[:=]\s*([\d,.]+)",
        "BD": r"BD\s*[:=]\s*([\d,.]+)",
        "Alb": r"Alb\s*[:=]\s*([\d,.]+)",
        "PCR": r"PCR\s*[:=]\s*([\d,.]+)",
        "Lc": r"Lc\s*[:=]\s*([\d,.]+)",
        "Bt": r"Bt\s*[:=]\s*([\d,.]+)",
        "Hb": r"Hb\s*[:=]\s*([\d,.]+)",
        "Plaq": r"Plaq\s*[:=]\s*([\d,.]+)"
    }

    # Para extrair múltiplas datas e os respectivos valores, considere que o texto tem blocos de exames.
    # Aqui vou fazer uma extração simples só pra mostrar:
    data_matches = re.findall(r'(\d{2}/\d{2}/\d{4})', texto)
    datas = sorted(set(data_matches), key=lambda d: datetime.strptime(d, "%d/%m/%Y"))

    linhas = []
    for data in datas:
        valores = []
        for chave, padrao in padrao_valores.items():
            busca = re.search(rf"{data}.*?{padrao}", texto, re.DOTALL)
            valor = busca.group(1) if busca else "-"
            valores.append(valor)
        linha = f"{data} | " + " | ".join(valores)
        linhas.append(linha)

    cabecalho = "Data | Cr | eTFG | Ur | K | Na | Mg | P | TGO | TGP | FAL | gGT | BT | BD | Alb | PCR | Lc | Bt | Hb | Plaq"
    resultado = cabecalho + "\n" + "\n".join(linhas)
    return resultado

# Escolhe função pelo modo selecionado
if modo == "Admissão Ortopedia":
    resultado = extrair_info(texto)
else:
    resultado = extrair_info_evolucao(texto)

st.text_area("Resultado formatado:", value=resultado, height=600)
