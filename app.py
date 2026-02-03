import streamlit as st
import pandas as pd

st.title("Alocação de Horários IFSC")

# Upload da planilha
uploaded_file = st.file_uploader("Envie a planilha Excel (alocacao_ifsc_V23.xlsx)", type="xlsx")

if uploaded_file is not None:
    # Ler a planilha com pandas
    df = pd.read_excel(uploaded_file)
    
    st.success("Planilha carregada com sucesso!")
    st.write(f"**Número de linhas:** {len(df)}")
    st.write(f"**Colunas encontradas:** {list(df.columns)}")
    
    # Prévia dos dados (primeiras 10 linhas)
    st.subheader("Prévia dos Dados")
    st.dataframe(df.head(10))
    
    # Botão para processar (próxima etapa)
    if st.button("Processar Dados para Alocação"):
        st.info("Aqui vamos integrar o motor de alocação. Por enquanto, apenas uma mensagem de teste.")
        # Futuro: chamar função de alocação
else:
    st.info("Faça upload da planilha para começar.")