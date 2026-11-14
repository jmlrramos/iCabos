# Tecneira · Dimensionamento de Cabos e Linhas

Aplicação Streamlit para dimensionar cabos e linhas de centrais solares e parques eólicos (BT, MT, AT e MAT).
Criada por Jorge Ramos para uso privado da Tecneira – Tecnologias Energéticas, S.A.

## Funcionalidades
- Critério térmico (RTIEBT 523), proteção (RTIEBT 433), queda de tensão, perdas, curto-circuito e efeito capacitivo.
- Perdas anuais com horas equivalentes da central e horas de perdas τ; valor e VAL das perdas.
- Painel lateral com os cálculos justificativos e memória de cálculo descarregável.
- Cálculo rápido de linhas aéreas (10 a 400 kV), linha simples ou dupla, critério N-1.
- Consulta de tabelas de correntes admissíveis: LXHIOV, XHIOV, MT tripolares, VV/VAV, XV/XAV, LVV/LSVV, LXV/LSXV, ACSR, AAAC e H1Z2Z2-K.
- Resultados ordenados da menor para a maior utilização.

## Executar no PC
```
pip install -r requirements.txt
streamlit run app.py
```

## Publicar no Streamlit Community Cloud
1. Coloque estes ficheiros na raiz de um repositório GitHub (incluindo as pastas `assets` e `.streamlit`).
2. Em https://share.streamlit.io clique em **Create app** → **Deploy a public app from GitHub**.
3. Escolha o repositório, o ramo `main` e o ficheiro `app.py`. Clique em **Deploy**.
4. Para uso privado: no painel da app, **Settings → Sharing → Only specific people can view this app**.

## Fontes
Tabelas técnicas Eurocabos (Mai.06), IEC 60364-5-52, IEC 60502-2, IEC 60287, EN 50618, RTIEBT, RSLEAT, RSRDEEBT.
Valores indicativos; validar com o fabricante para projeto de execução.
