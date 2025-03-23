#!/usr/bin/env python3

# Base imports
import json
import os

# Third imports
import streamlit as st
import pandas as pd

# Project imports


# Define answer choices with numerical values
answer_choices = {
    "Nunca ou Raramente": 1,
    "Às vezes": 2,
    "Frequentemente": 3,
    "Muito": 4,
    "Muitíssimo": 5
}

# Load gabarito (question mappings for each gift)
with open("gabarito_dons.json", "r", encoding="utf-8") as gifts:
    gabarito_dict = json.load(gifts)

# Load questions
with open('questions.tsv', 'r') as q:
    questions_list = [question.strip() for question in q]

# Convert question numbers to zero-based indices
gabarito_dict = {dom: [int(q) - 1 for q in questions] for dom, questions in gabarito_dict.items()}

# Function to load saved responses
def load_responses():
    if os.path.exists("respostas.csv"):
        return pd.read_csv("respostas.csv")
    return pd.DataFrame()

# Function to process and generate graph data
def generate_graph_data(df):
    lista_de_dons_por_pessoa = pd.DataFrame()

    for i, row in df.iterrows():
        list_of_dons = pd.DataFrame(columns=["Dom", "Pontuação", "Dom_pontuacao"])
        membro = f"Pessoa {i+1}"  # Creating a unique identifier for each person

        for dom, indices in gabarito_dict.items():
            score_sum = row.iloc[indices].sum()
            list_of_dons.loc[len(list_of_dons)] = [dom, score_sum, f"{dom} {score_sum}"]

        # Sort values by score
        list_of_dons.sort_values(by="Pontuação", ascending=False, inplace=True)

        # Store data
        lista_de_dons_por_pessoa[membro] = list_of_dons["Dom_pontuacao"].values

    return lista_de_dons_por_pessoa

# Create session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "form"

# Form Page
if st.session_state.page == "form":
    st.title("Questionário 'Qual é o seu dom?'- Adaptado por Berndt Wolter D.Min (133 Questões)")

    with st.form("questionnaire_form"):
        responses = {}
        for i in range(1, 134):
            responses[f"Q{i}"] = st.radio(f"Questão {i}: {questions_list[i-1]}", answer_choices.keys(), index=0)

        submitted = st.form_submit_button("Enviar Respostas")

    if submitted:
        # Convert responses to DataFrame
        df = pd.DataFrame([{q: answer_choices[a] for q, a in responses.items()}])

        # Save responses
        if os.path.exists("respostas.csv"):
            df.to_csv("respostas.csv", mode="a", header=False, index=False)
        else:
            df.to_csv("respostas.csv", index=False)

        # Change page to results
        st.session_state.page = "results"
        st.rerun()  # ✅ Fixed rerun function

# Results Page
if st.session_state.page == "results":
    st.title("Resultados")

    # Load all responses
    df = load_responses()

    if not df.empty:
        # Generate graph data
        dons_df = generate_graph_data(df[-1:])

        # Display results
        st.write("Pontuações por Dom:")
        st.dataframe(dons_df)

        # Bar chart visualization
        total_scores = {dom: df.iloc[:, indices].sum().sum() for dom, indices in gabarito_dict.items()}
        total_scores_df = pd.DataFrame(list(total_scores.items()), columns=["Dom", "Pontuação"]).set_index("Dom")

        st.bar_chart(total_scores_df)
        st.write("Respostas anteriores:")
        st.dataframe(df)
    st.button("Voltar ao Início", on_click=lambda: st.session_state.update(page="form"))


