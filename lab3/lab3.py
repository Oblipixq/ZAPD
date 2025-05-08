import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import re

area_dict = {
    1: "Вінницька", 2: "Волинська", 3: "Дніпропетровська", 4: "Донецька",
    5: "Житомирська", 6: "Закарпатська", 7: "Запорізька", 8: "Івано-Франківська",
    9: "Київська", 10: "Кіровоградська", 11: "Луганська", 12: "Львівська",
    13: "Миколаївська", 14: "Одеська", 15: "Полтавська", 16: "Рівненська",
    17: "Сумська", 18: "Тернопільська", 19: "Харківська", 20: "Херсонська",
    21: "Хмельницька", 22: "Черкаська", 23: "Чернівецька", 24: "Чернігівська",
    25: "Республіка Крим"
}

area_name_to_id = {v: k for k, v in area_dict.items()}

st.markdown("""
    <style>
        .main { background-color: #f0f2f6; }
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .stSlider > div, .stSelectbox > div { color: #1f4e79; }
        .stButton>button {
            background-color: #1f4e79;
            color: white;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)


def read_vhi_from_csv(directory):
    data_frames = []
    for filename in os.listdir(directory):
        if filename.startswith('vhi_id_') and filename.endswith('.csv'):
            filepath = os.path.join(directory, filename)
            try:
                area_id = int(filename.split('_')[2])
            except (IndexError, ValueError):
                print(f"Невірний формат імені файлу: {filename}. Видаляємо файл.")
                os.remove(filepath)
                continue
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    cleaned_lines = [re.sub(r'<.*?>', '', line) for line in f]
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(cleaned_lines)

                df = pd.read_csv(filepath, index_col=False, header=1)
                df.columns = df.columns.str.strip()
                df['area_ID'] = area_id
                data_frames.append(df)
            except Exception as e:
                print(f"Помилка при зчитуванні файлу {filename}: {e}")
    return pd.concat(data_frames, ignore_index=True) if data_frames else pd.DataFrame()

# --- Завантаження даних ---
directory = os.path.join(os.path.dirname(__file__), 'csvfiles')
df = read_vhi_from_csv(directory)

default_state = {
    "selected_index": "VCI",
    "selected_area": "Вінницька",
    "week_range": (1, 52),
    "year_range": (1982, 2024),
    "ascending": False,
    "descending": False,
}

if st.session_state.get("reset_filters", False):
    for key, value in default_state.items():
        st.session_state[key] = value
    st.session_state.reset_filters = False
    st.rerun()


for key, value in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = value



# --- Інтерактив ---
vhi_options = ["VCI", "TCI", "VHI"]
available_area_names = [area_dict[aid] for aid in sorted(df['area_ID'].unique())]

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Фільтри")
    selected_index = st.selectbox("Оберіть показник", options=vhi_options, key="selected_index")
    
    selected_area_name = st.selectbox("Оберіть область", options=available_area_names, key="selected_area")
    selected_area = area_name_to_id[selected_area_name]

    week_range = st.slider("Інтервал тижнів", 1, 52, key="week_range")
    year_range = st.slider("Інтервал років", 1982, 2024, key="year_range")

    ascending = st.checkbox("Сортувати за зростанням", key="ascending")
    descending = st.checkbox("Сортувати за спаданням", key="descending")

    if ascending and descending:
        st.warning("Не можна одночасно обрати сортування за зростанням і спаданням.")
        ascending = descending = False

    if st.button("Скинути фільтри"):
        st.session_state["reset_filters"] = True
        st.rerun()

    

# --- Фільтрація ---
filtered_df = df[
    (df['area_ID'] == selected_area) &
    (df['week'].between(*week_range)) &
    (df['year'].between(*year_range))
]

# --- Сортування ---
if ascending:
    filtered_df = filtered_df.sort_values(by=selected_index, ascending=True)
elif descending:
    filtered_df = filtered_df.sort_values(by=selected_index, ascending=False)

# --- Вкладки ---
with col2:
    tab1, tab2, tab3 = st.tabs(["Таблиця", "Графік", "Порівняння"])

    with tab1:
        st.dataframe(filtered_df)

    with tab2:
        st.subheader(f"Динаміка {selected_index} по області {selected_area_name}")
        fig, ax = plt.subplots()
        x_labels = filtered_df['year'].astype(str) + "-W" + filtered_df['week'].astype(int).astype(str)
        ax.plot(x_labels, filtered_df[selected_index], marker='o', linestyle='-')
        ax.set_xlabel("Тиждень")
        ax.set_ylabel(selected_index)
        ax.tick_params(axis='x', labelrotation=45)
        
        if len(x_labels) > 20:
            ax.set_xticks([])
            st.info("Підписи на осі X приховано, оскільки їх більше 20")
        else:
            ax.set_xticklabels(x_labels, rotation=45)

        ax.grid(True)
        st.pyplot(fig)

    with tab3:
        st.subheader(f"Середні значення {selected_index} по всіх областях")
        comp_df = df[
            (df['week'].between(*week_range)) &
            (df['year'].between(*year_range))
        ]
        mean_values = comp_df.groupby("area_ID")[selected_index].mean()
        mean_values = mean_values.rename(index=area_dict).sort_values()
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        mean_values.plot(kind='bar', ax=ax2, color='#1f77b4')
        ax2.set_ylabel(f"Середнє {selected_index}")
        ax2.set_xlabel("Область")
        ax2.grid(axis='y')
        st.pyplot(fig2)


