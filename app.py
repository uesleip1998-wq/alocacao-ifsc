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
                "regra": row["Regra_Especial"],
                "dia_fixo": row["Dia_Travado"],
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
        st.info("Próxima etapa: implementar regras e motor de alocação.")
else:
    st.info("Faça upload da planilha para começar.")