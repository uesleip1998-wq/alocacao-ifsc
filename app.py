import streamlit as st
import pandas as pd

st.title("Alocação de Horários IFSC")

uploaded_file = st.file_uploader(
    "Envie a planilha Excel (alocacao_ifsc_V23.xlsx)",
    type="xlsx"
)

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.success("Planilha carregada com sucesso!")
    st.write(f"Número de linhas: {len(df)}")
    st.write(f"Colunas encontradas: {list(df.columns)}")

    st.subheader("Prévia dos dados")
    st.dataframe(df.head(10))

    if st.button("Processar Dados para Alocação"):
        turmas = {}

        for _, row in df.iterrows():
            turma_id = row["ID_Turma"]

            if turma_id not in turmas:
                turmas[turma_id] = {
                    "turno": row["Turno"],
                    "ucs": []
                }

            uc = {
                "nome": row["Nome_UC"],
                "ch": row["Carga_Horaria_Total"],
                "docentes": [d.strip() for d in str(row["Docentes"]).split(",")],
                "espaco": row["Espacos"],
                "regra": "" if pd.isna(row["Regra_Especial"]) else str(row["Regra_Especial"]),
                "dia_fixo": "" if pd.isna(row["Dia_Travado"]) else str(row["Dia_Travado"]),
                "semana_inicio": row["Semana_Inicio"],
                "semana_fim": row["Semana_Fim"],
                "tipo_alocacao": row["Tipo_Alocacao"],
                }

            turmas[turma_id]["ucs"].append(uc)

        st.success(f"Processadas {len(turmas)} turmas.")

        co_docencias = 0
        for turma_id, dados in turmas.items():
            for uc in dados["ucs"]:
                if len(uc["docentes"]) > 1:
                    co_docencias += 1

        st.write(f"Possíveis co-docências detectadas: {co_docencias}")

        # Verificações básicas de conflitos
        conflitos_espaco = 0
        conflitos_docente = 0
        alocacao_simulada = {}  # Simulação simples: dia -> turno -> espaço/docente

        for turma_id, dados in turmas.items():
            turno = dados["turno"]
            for uc in dados["ucs"]:
                dia = uc["dia_fixo"] if pd.notna(uc["dia_fixo"]) else "Segunda"  # Exemplo: assume dia se não fixo
                espaco = uc["espaco"]
                docentes = uc["docentes"]

                # Verificar conflito de espaço
                chave_espaco = f"{dia}_{turno}_{espaco}"
                if chave_espaco in alocacao_simulada:
                    conflitos_espaco += 1
                else:
                    alocacao_simulada[chave_espaco] = True

                # Verificar conflito de docente
                for docente in docentes:
                    chave_docente = f"{dia}_{turno}_{docente}"
                    if chave_docente in alocacao_simulada:
                        conflitos_docente += 1
                    else:
                        alocacao_simulada[chave_docente] = True

        st.subheader("Verificações de Conflitos (Simulação Básica)")
        st.write(f"**Conflitos de espaço:** {conflitos_espaco} (mesmo local/horário)")
        st.write(f"**Conflitos de docente:** {conflitos_docente} (mesmo professor/horário)")
        
        if conflitos_espaco == 0 and conflitos_docente == 0:
            st.success("Nenhum conflito básico detectado! Pronto para alocação avançada.")
        else:
            st.warning("Conflitos detectados. O motor real aplicaria regras de cascata para resolver.")
                    # NOVO: Implementação da Estratégia A (Guia/Eventos)
        estrategia_a_turmas = []
        for turma_id, dados in turmas.items():
            # Identificar turmas de Estratégia A (ex: contém "EVENTOS" ou regra "EAD Sexta-feira")
            if "EVENTOS" in turma_id or any("EAD Sexta-feira" in uc["regra"] for uc in dados["ucs"]):
                estrategia_a_turmas.append(turma_id)
                # Simulação básica: alocar UCs em blocos (B1: semanas 1-8, B2: 9-16, B3: 17-20)
                for uc in dados["ucs"]:
                    if uc["ch"] == 80:
                        # 64h presencial (16 encontros) + 16h EAD
                        uc["bloco_alocado"] = "B1-B2"  # Exemplo: distribuir em 2 blocos
                        uc["dias_alocados"] = ["Segunda", "Quarta"]  # Exemplo criativo: explorar combinações
                    elif uc["ch"] == 40:
                        # Parear com 80h ou "dupla intensiva"
                        uc["bloco_alocado"] = "B3"  # Exemplo: bloco final
                        uc["dias_alocados"] = ["Terça", "Quinta"]  # Pareamento criativo

        st.subheader("Estratégia A (Guia/Eventos) - Simulação")
        if estrategia_a_turmas:
            st.write(f"Turmas identificadas para Estratégia A: {', '.join(estrategia_a_turmas)}")
            st.success("Alocação básica aplicada: UCs distribuídas em blocos com pareamento criativo.")
        else:
            st.info("Nenhuma turma identificada para Estratégia A (verifique regras na planilha).")

        # Futuro: Expandir para Estratégias B/C/D, restrições docentes, cascata de conflitos
                # NOVO: Implementação da Estratégia B (SUP Gestão - Noturno)
        estrategia_b_turmas = []
        for turma_id, dados in turmas.items():
            # Identificar turmas de Estratégia B (ex: contém "SUP GESTAO" ou turno "Noturno")
            if "SUP GESTAO" in turma_id or dados["turno"] == "Noturno":
                estrategia_b_turmas.append(turma_id)
                # Simulação: alocar UCs em 2 blocos (B1: semanas 1-11, B2: 12-22), sempre noturno
                for uc in dados["ucs"]:
                    if uc["ch"] == 60:
                        # Âncora semestral (20 encontros de 3h)
                        uc["bloco_alocado"] = "B1-B2"  # Exemplo: distribuir nos 2 blocos
                        uc["dias_alocados"] = ["Segunda", "Quarta", "Sexta"]  # Exemplo criativo: explorar combinações noturnas
                    elif uc["ch"] == 30:
                        # Peça de bloco (10 encontros)
                        uc["bloco_alocado"] = "B1"  # Exemplo: bloco inicial
                        uc["dias_alocados"] = ["Terça", "Quinta"]  # Pareamento criativo

        st.subheader("Estratégia B (SUP Gestão - Noturno) - Simulação")
        if estrategia_b_turmas:
            st.write(f"Turmas identificadas para Estratégia B: {', '.join(estrategia_b_turmas)}")
            st.success("Alocação aplicada: UCs distribuídas em blocos noturnos com pareamento criativo.")
        else:
            st.info("Nenhuma turma identificada para Estratégia B (verifique turnos e nomes na planilha).")
        st.info("Próxima etapa: Implementar regras específicas (blocos A/B/C/D, restrições docentes).")
else:
    st.info("Faça upload da planilha para começar.")