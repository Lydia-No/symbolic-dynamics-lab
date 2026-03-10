import streamlit as st
from api.experiment_api import SymbolicExperiment


st.title("Symbolic Hypercube Explorer 🧊")

dimension = st.slider("Hypercube dimension", 2, 16, 8)

if "experiment" not in st.session_state:
    st.session_state.experiment = SymbolicExperiment(dimension)

exp = st.session_state.experiment


st.header("Add Symbol")

word = st.text_input("Symbol name")

bit = st.number_input("Bit index", 0, dimension - 1, 0)

if st.button("Add Symbol"):
    if word:
        exp.add_symbol(word, bit)
        st.success(f"{word} → flip bit {bit}")


st.header("Current Symbols")

st.write(exp.symbols())


st.header("Run Sequence")

text = st.text_input("Enter sequence (space separated)")

if st.button("Run"):
    if text:
        traj = exp.run_text(text)

        st.write("Trajectory:")

        for state in traj:
            st.write(state)
