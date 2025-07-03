import streamlit as st
from query_ramayana.query import Query

st.set_page_config(page_title="ask_ramayana", layout="centered")

st.title("Ask Ramayana")
st.write("Query from Ramayana! \n Currently supports Valmiki and Tulsidas versions.")

user_input = st.text_area("Enter your query here")

if st.button("Ask"):
    if user_input.strip() == "":
        st.warning("Please enter some input text.")
    else:
        with st.spinner("Generating response..."):
            output = Query(user_input).run()
        st.success("Check out the response below:")
        st.write(output)
