import streamlit as st
from query_ramayana.query import Query

st.set_page_config(page_title="Ask Ramayana", layout="centered")

st.title("Ask Ramayana")
st.write("Query from Ramayana! \n Currently supports Valmiki and Tulsidas versions.")

user_input = st.text_area("Enter your query here")


if st.button("Ask"):
    if user_input.strip() == "":
        st.warning("Please enter some input text.")
    else:
        with st.spinner("Generating response..."):
            rag_response, valmiki_sources, tulsidas_sources = Query(user_input).run()
        st.success("Check out the response below:")
        # st.write(output)
        st.text_area("Response", value=rag_response, height=300, disabled=True)

        if valmiki_sources:
            with st.expander("\n Sources from Valmiki Ramayana: \n"):
                st.text(valmiki_sources)

        if tulsidas_sources:
            with st.expander("\n Sources from Tulsidas Ramayana: \n"):
                st.text(tulsidas_sources)
