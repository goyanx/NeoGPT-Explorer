import openai
import streamlit as st
from streamlit_chat import message

from driver import read_query, get_article_text
from train_cypher import examples

st.title("NeoGPT : GPT3 + Neo4j")

# st.secrets["api_secret"]
openai.api_key = "<<Insert API KEY>>"


def generate_response(prompt, cypher=True):
    if cypher:
        completions = openai.Completion.create(
            engine="text-davinci-003",
            prompt=examples + "\n#" + prompt,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.5,
        )
        cypher_query = completions.choices[0].text
        message = read_query(cypher_query)
        return message, cypher_query
    else:
        completions = openai.Completion.create(
            engine="text-davinci-003",
            prompt="Summarize the following article: \n" + prompt,
            max_tokens=156,
            n=1,
            stop=None,
            temperature=0.5,
        )
        message = completions.choices[0].text
        return message, None


# Storing the chat
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []


def get_text():
    input_text = st.text_input(
        "Ask away", "", key="input")
    return input_text


col1, col2 = st.columns([2, 1])


with col2:
    another_placeholder = st.empty()
with col1:
    placeholder = st.empty()
user_input = get_text()


if user_input:
    if "summar" in user_input:
        article_title = user_input.split(":")[1].strip()
        article_text = get_article_text(article_title)
        if not article_text:

        output, cypher_query = generate_response(user_input, cypher=False)
        st.session_state.past.append(user_input)
        st.session_state.generated.append((output, cypher_query))

    else:
        output, cypher_query = generate_response(user_input)
        # store the output
        st.session_state.past.append(user_input)
        st.session_state.generated.append((output, cypher_query))


with placeholder.container():

    if st.session_state['generated']:
        #len_generated = len(st.session_state['generated'])
        #start = 0 if len_generated < 3 else len_generated - 3
        # for i in range(start, len_generated):

        message(st.session_state['past'][-1],
                is_user=True, key=str(-1) + '_user')
        for j, text in enumerate(st.session_state['generated'][-1][0]):
            message(text, key=str(-1) + str(j))

with another_placeholder.container():
    if st.session_state['generated']:
        st.text_area("Generated Cypher statement",
                     st.session_state['generated'][-1][1], height=240)
