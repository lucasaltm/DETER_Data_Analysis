# =======================       IMPORTS       ========================== #

import streamlit as st
import pandas as pd
import zipfile
import gdown
import os
import streamlit.components.v1 as components

# =======================    PAGE  CONFIG    ========================== #
icon = "🌳"

st.set_page_config(
    page_title="DETER",
    page_icon=icon,
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =======================    Download Maps    ========================== #
def toast_msg():
    st.toast("Seleção de Idioma disponível no menu lateral.", icon='💬')
    st.toast("Language selection available in the sidebar menu.", icon='💬')

def isMapsDownloaded():
    folder = 'Visualizations/DETER/Maps'
    os.makedirs(folder, exist_ok=True)
    total = 22

    downloaded = False
    
    if os.path.exists(folder):
        num = len([nome for nome in os.listdir(folder)])
        if num >= total:
            downloaded = True

    return downloaded

def download_maps():
    d = isMapsDownloaded()

    while not d:
        toast_msg()
        output = 'Visualizations/DETER/Maps/maps.zip'
        data_link = 'https://drive.google.com/uc?id=11qIncS7zDWkc7-7PmbDLRVnKJna2rAPA&export=download'

        gdown.download(data_link, output, quiet=False)
        
        with zipfile.ZipFile('Visualizations/DETER/Maps/maps.zip', 'r') as zip_ref:
            zip_ref.extractall('Visualizations/DETER/Maps')
        d = isMapsDownloaded()
with st.spinner(text="Loading..."):
    download_maps()


# =======================       TEXTS       ========================== #

df_texts = pd.read_csv('texts/texts_deter.csv', sep='§', engine='python')
english = {list(df_texts['Key'])[i]: list(df_texts['English'])[i] for i in range(len(list(df_texts['Key'])))}
portuguese = {list(df_texts['Key'])[i]: list(df_texts['Portuguese'])[i] for i in range(len(list(df_texts['Key'])))}

classes_deter_en = {'CICATRIZ_DE_QUEIMADA': 'Forest Fire Scar',
          'DESMATAMENTO_CR': 'Deforestation with Exposed Soil',
          'DESMATAMENTO_VEG': 'Deforestation with Vegetation',
          'MINERACAO': 'Mining',
          'DEGRADACAO': 'Degradation',
          'CS_DESORDENADO': 'Selective Logging Type 1 (Disordered)',
          'CS_GEOMETRICO': 'Selective Logging Type 2 (Geometric)',
}

classes_deter_pt = {'CICATRIZ_DE_QUEIMADA': 'Cicatriz de incêndio florestal',
          'DESMATAMENTO_CR': 'Desmatamento com solo exposto',
          'DESMATAMENTO_VEG': 'Desmatamento com Vegetação',
          'MINERACAO': 'Mineração',
          'DEGRADACAO': 'Degradação',
          'CS_DESORDENADO': 'Corte Seletivo Tipo 1 (Desordenado)',
          'CS_GEOMETRICO': 'Corte Seletivo Tipo 2 (Geométrico)',
}

estados = {
    "MT": "Mato Grosso",
    "PA": "Pará",
    "AM": "Amazonas",
    "RO": "Rondônia",
    "MA": "Maranhão",
    "RR": "Roraima",
    "AC": "Acre",
    "TO": "Tocantins",
    "AP": "Amapá"
}

def get_texts(lang):
    if lang == "English":
        return classes_deter_en, english
    else:
        return classes_deter_pt, portuguese

# ======================= lANGUAGE SETTINGS  ========================== #
languages = {"English": "en", "Portuguese": "pt"}

dict_params = st.query_params.to_dict()

if "lang" not in dict_params.keys():
    st.query_params["lang"] = "en"
    st.rerun()

def set_language() -> None:
    if "selected_language" in st.session_state:
        st.query_params["lang"] = languages.get(st.session_state["selected_language"])

with st.sidebar:
    sel_lang = st.radio(
    "Language", options=languages,
    horizontal=True, 
    on_change=set_language,
    key="selected_language",)

dict_classes, texts = get_texts(sel_lang)

# =======================      HEADER       ========================== #
st.image('Images/fire3.png')

def center_md(text):
    return "<h3 style='text-align: center;'>" + text + "</h3>"
    
st.markdown(center_md(texts['page_title']), unsafe_allow_html=True)

# =======================        BODY       ========================== #

def divider():
    st.markdown('</br>',unsafe_allow_html=True)
    st.divider()
    st.markdown('</br>',unsafe_allow_html=True)

about, mapv, alert_classes, states_statistics, cities_statistics, ucs_statistics, dmg_ty = st.tabs([texts['about'],
                                                                                                    texts['map'],
                                                                                                    texts['alert_classes'],
                                                                                                    texts['states_statistics'],
                                                                                                    texts['cities_statistics'],
                                                                                                    texts['ucs_statistics'],
                                                                                                    texts['dmg_ty']])
# About DETER
with about:

    st.write(texts['deter_expander_desc_1'])
    st.write(texts['deter_expander_desc_2'])
    divider()

# =======================        MAPS       ========================== #
def center_map(html_map):
    html_final = """
    <div style='display:flex; justify-content:center; align-items:center; height:100%;'>
    <div style='width: 80%;'>""" + html_map + """</div>
    </div>
    """
    return html_final

def read_map(map_name):
    html_file_path = f'Visualizations/DETER/Maps/{map_name}.html'
    
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    return html_content

with mapv:
    
    radio_title = texts['vis_type']
    options = texts['vis_options'].split(';')

    seL_map = st.radio(radio_title, options=options,
                           horizontal=True, index=0)

    if seL_map == options[1]:
        map_name = 'States_' + st.query_params["lang"].upper()
        with st.spinner(text="Loading..."):
            components.html(read_map(map_name), height=900)
            
    elif seL_map == options[2]:
        df_estados = pd.DataFrame(list(estados.items()), columns=['UF', 'Nome'])
        df_estados['Nome_UF'] = df_estados['Nome'] + ' (' + df_estados['UF'] + ')'
        
        lst_states = list(df_estados['Nome_UF'])
        
        ms_title = texts['vis_state']
        option = st.selectbox(
            ms_title,
            tuple(lst_states))

        #if option != 'All Cities':
        uf_sel = df_estados[df_estados['Nome_UF'] == (option)].UF
        uf_sel = uf_sel.values[0]

        map_name = 'Cities_' + st.query_params["lang"].upper() + '_' + uf_sel.upper()
        
        with st.spinner('Loading visualization, please wait...'):
            components.html(read_map(map_name), height=900)
        
        
    elif seL_map == options[3]:
        map_name = 'C_Units_' + st.query_params["lang"].upper()
        with st.spinner(text="Loading..."):
            components.html(read_map(map_name), height=900)
    divider()

# =======================        GRAPHS       ========================== #
def plot_graph(name, format='png', language=st.query_params["lang"]):
    dir = "Visualizations/DETER/Graphs"
    img_name = f"{name}_{language.upper()}.{format}"
    img_path = os.path.join(dir, img_name)
    
    if os.path.exists(img_path):
        st.image(img_path)
    else:
        st.error(f"Image {img_name} not found.")

def read_txt_graph(name):
    dir = "Visualizations/DETER/Graphs"
    file_name = name + '.txt'
    file_path = os.path.join(dir, file_name)
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as txt:
            return txt.read()
    else:
        print(f"File {file_name} not found.")
    
    

# General Vision
with alert_classes:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(center_md(texts['title_deter_graph2']), unsafe_allow_html=True)
        plot_graph('Graph2')
        
    with col2:
        st.markdown(center_md(texts['title_deter_graph1']), unsafe_allow_html=True)
        plot_graph('Graph1')


    st.markdown(texts['graphs_12_desc'])
    divider()

with states_statistics:
    st.markdown(center_md(texts['title_deter_graph3']), unsafe_allow_html=True)
    plot_graph('Graph3')
    st.markdown(texts['graph3_desc'])
    
    divider()

    st.markdown(center_md(texts['graph8_title']), unsafe_allow_html=True)
    plot_graph('Graph8')
    st.markdown(texts['graph8_desc'])
    divider()

with cities_statistics:

    st.markdown(center_md(texts['title_deter_graph4']), unsafe_allow_html=True)
    plot_graph('Graph4')
    st.markdown(texts['graph4_desc'])
    divider()
    
with ucs_statistics:

    st.markdown(center_md(texts['graph9_title']), unsafe_allow_html=True)
    plot_graph('Graph9')
    st.markdown(texts['graph9_desc'])

    divider()

# Damage through years
with dmg_ty:
    st.markdown(center_md(texts['title_deter_graph5']), unsafe_allow_html=True)
    plot_graph('Graph5')
    st.markdown(texts['graph5_desc'])
    
    divider()
    
    period = read_txt_graph('Graph6_' + st.query_params["lang"].upper() + '_period')
    print(period)
    period = period.split(';')
    st.markdown(center_md(texts['title_deter_graph6'].format(period[0],period[1])), unsafe_allow_html=True)
    plot_graph('Graph6')
    st.markdown(texts['graph6_desc'])

    divider()

    st.markdown(center_md(texts['title_deter_graph7']), unsafe_allow_html=True)
    plot_graph('Graph7')
    st.markdown(texts['graph7_desc'],unsafe_allow_html=True)
    divider()


# =======================        FOOTER       ========================== #
st.image("Images/logo_aeb_mcti_horizontal_positiva_02.png")
#st.image("http://www.inpe.br/marcasOficiais/imagens/logo_aeb_mcti_horizontal_positiva_02.png")
st.markdown("<h6 style='text-align: center;'>" + texts['inpe_ref'] + "</h6>", unsafe_allow_html=True)