import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from wordcloud import WordCloud
import google.generativeai as genai

#  Page settings
st.set_page_config(
    page_title='Project 5', 
    page_icon='🤖', 
    layout='wide'
)

# Project Description
st.header('Project 5')
st.markdown('''
    **Artificial Intelligence (LLM) to analyze Copom minutes** 
''')

# Function to collect the text of a Copom meeting minute
def get_minute_text(number):
    url = f'https://raw.githubusercontent.com/ajdavidl/corpus-atas-copom/main/atas/ata{number}.txt'
    txt = requests.get(url).text
    #  If the minutes do not exist, it returns an empty string.
    if len(txt) < 100:
        return ''
    return txt
 
# side bar settings
st.sidebar.header('Options Menu')

#  Field for the user to enter their API key
api_key = st.sidebar.text_input('🔑 Chave da API do Gemini', type='password', value='')

# Field for the user to enter the Copom minutes number
copom_number = st.sidebar.number_input('#️⃣ Número da ata do Copom', value=267)

if st.sidebar.button('🤖 Analisar com IA'):

    # Entry validation
    if api_key and copom_number:
        with st.spinner('Carregando dados da ata'):
            #  Get the text of the minutes
            txt_minute = get_minute_text(copom_number)

            # if the minutes are invalid
            if not txt_minute:
                st.warning(f'Ata **{copom_number}** não encontrada.')
                # Interrupts the Streamlit execution flow.
                st.stop()

        # Progress Bar
        with st.spinner('Analyzing'):
            #  API Gemini sets
            genai.configure(api_key=api_key)

        
            # Instantiates the model and performs the request.
            model = genai.GenerativeModel('gemini-3.5-flash')
            prompt = f'''
                You will act as an experienced financial analyst to analyze the minutes of the Monetary Policy Committee (Copom) meeting below. 
                Based on the text, generate a JSON object with the following structure:         

                - summary: a brief yet comprehensive summary of the minutes, in 3 paragraphs. 
                - key_topics: a list of 5 sentences covering the main themes. 
                - keywords: a list of at least 20 keywords found in the minutes that reflect the economic team's key highlights.
                
                JSON output example:
                {{
            
                    "summary": "Objective summary of the minutes in just 3 paragraphs.",
                    "key_topics": ["example1", "example2", "exampleN"],
                    "keywords": ["example1", "example2", "exampleN"]
                }}

                Ensure your output is in Brazilian Portuguese. (obviously, english speakers must change the language)

                Minutes text:

                {txt_minute}
            '''
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type='application/json'
                )
            )
            response = json.loads(response.text)

            # Two columns layout
            col1, col2 = st.columns(2)
            with col1:
                st.subheader('Resumo da ata')
                st.write(f'''
                    <p style="font-size:12px">
                        {response["resumo"]}
                    </p>
                    ''', unsafe_allow_html=True)
                
                st.subheader('Destaques principais')
                for topico in response['topicos_chave']:
                    st.markdown(f'- {topico}')

            #  Column 2: Word Cloud
            with col2:
                st.subheader('Principais termos')

                # Generates and displays the word cloud
                stopwords = ['de', 'do', 'da', 'no', 'na']
                wordcloud = WordCloud(height=400, background_color='white', stopwords=stopwords).generate(
                    ', '.join(response['palavras_chave'])
                )
                fig, ax = plt.subplots()
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
        
    else:
        st.warning('Please enter the API key and the Copom meeting number.')

st.sidebar.markdown('''
    <p style="margin-top: 30px; text-align: center">
        Python project to financial markets <br>
        
''', unsafe_allow_html=True)