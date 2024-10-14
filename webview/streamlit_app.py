#streamlit_app.py

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import json
import os
from datetime import datetime

# Set the API URL
API_URL = os.getenv("API_URL", "http://web:8000/api/v1")
# Page config
st.set_page_config(page_title="Анализатор резюме", page_icon="📊", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .sidebar .sidebar-content {
        background: #ffffff
    }
    .Widget>label {
        color: #31333F;
        font-weight: bold;
    }
    .stButton>button {
        color: #ffffff;
        background-color: #4CAF50;
        border-radius: 5px;
    }
    .stDataFrame {
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    h1, h2, h3 {
        color: #2C3E50;
    }
    .stPlotlyChart {
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Load Lottie animation
@st.cache_data
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_resume = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_5n8yfkac.json")

# Sidebar
with st.sidebar:
    st_lottie(lottie_resume, speed=1, height=200, key="resume_animation")
    st.title("Анализатор резюме")
    st.info("Загрузите резюме и получите мгновенный анализ!")

# Main content
tab1, tab2, tab3 = st.tabs(["📈 Дашборд", "📄 Анализ резюме", "🔍 Просмотр всех резюме"])

# Dashboard Tab
with tab1:
    st.header("📊 Дашборд анализа резюме")
    
    # Fetch all resumes
    with st.spinner("Загрузка данных..."):
        response = requests.get(f"{API_URL}/resumes/")
    
    if response.status_code == 200:
        resumes = response.json()
        df = pd.DataFrame(resumes)
        
        # Data cleaning and formatting
        df['predicted_salary'] = df['predicted_salary'].fillna(0).astype(float)
        df['formatted_salary'] = df['predicted_salary'].apply(lambda x: f"{x:,.2f} ₽")
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Всего резюме", len(df))
        col2.metric("Средний опыт", f"{df['experience'].mean():.1f} лет")
        col3.metric("Средняя прогнозируемая зарплата", f"{df['predicted_salary'].mean():,.2f} ₽")
        col4.metric("Удаленная работа", f"{df['is_remote'].sum()} ({df['is_remote'].mean()*100:.1f}%)")
        
        # Salary Distribution
        st.subheader("Распределение зарплат")
        fig = px.histogram(df, x='predicted_salary', nbins=20, 
                           labels={'predicted_salary': 'Прогнозируемая зарплата'},
                           title="Распределение зарплат")
        fig.update_xaxes(ticksuffix=" ₽", tickformat=",.0f")
        fig.update_layout(bargap=0.1)
        st.plotly_chart(fig, use_container_width=True)
        
        # Experience vs Salary
        st.subheader("Опыт vs Прогнозируемая зарплата")
        fig = px.scatter(df, x='experience', y='predicted_salary', 
                         hover_data=['title'], 
                         labels={'experience': 'Опыт работы (лет)', 'predicted_salary': 'Прогнозируемая зарплата'},
                         title="Опыт vs Прогнозируемая зарплата")
        fig.update_yaxes(ticksuffix=" ₽", tickformat=",.0f")
        st.plotly_chart(fig, use_container_width=True)
        
        # Job Types
        st.subheader("Типы работы")
        job_type_counts = df['job_type'].value_counts()
        fig = px.pie(values=job_type_counts.values, names=job_type_counts.index, title="Распределение типов работы")
        st.plotly_chart(fig, use_container_width=True)
        
        # Seniority Levels
        st.subheader("Уровни должности")
        seniority_counts = df['seniority_level'].value_counts()
        fig = px.bar(x=seniority_counts.index, y=seniority_counts.values, title="Распределение уровней должности")
        fig.update_xaxes(title="Уровень должности")
        fig.update_yaxes(title="Количество")
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.error("Ошибка при загрузке резюме. Пожалуйста, попробуйте еще раз.")

# Analyze Resume Tab
with tab2:
    st.header("📄 Анализ резюме")
    uploaded_file = st.file_uploader("Выберите файл резюме в формате PDF", type="pdf")

    if uploaded_file is not None:
        st.write("Загруженный файл:", uploaded_file.name)

        if st.button("Анализировать резюме"):
            with st.spinner("Анализ резюме..."):
                files = {"file": ("resume.pdf", uploaded_file.getvalue(), "application/pdf")}
                response = requests.post(f"{API_URL}/resumes/upload", files=files)

            if response.status_code == 200:
                result = response.json()
                st.success("Резюме успешно проанализировано!")

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Детали резюме")
                    st.write(f"**Должность:** {result['title']}")
                    st.write(f"**Опыт:** {result['experience']} лет")
                    st.write(f"**Местоположение:** {result['location']}")
                    st.write(f"**Тип работы:** {result['job_type']}")
                    st.write(f"**Уровень должности:** {result['seniority_level']}")
                    st.write(f"**Удаленная работа:** {'Да' if result['is_remote'] else 'Нет'}")
                
                with col2:
                    st.subheader("Рекомендуемые курсы")
                    # Define a list of desired skills
                    desired_skills = ["Python", "Machine Learning", "Data Analysis", "SQL", "Deep Learning"]
                    
                    # Extract skills from the resume
                    resume_skills = set(result['key_skills'].split(', '))
                    
                    # Find missing skills
                    missing_skills = set(desired_skills) - resume_skills
                    
                    # Coursera course recommendations (you can expand this dictionary)
                    coursera_courses = {
                        "Python": "https://www.coursera.org/learn/python",
                        "Machine Learning": "https://www.coursera.org/learn/machine-learning",
                        "Data Analysis": "https://www.coursera.org/learn/data-analysis-with-python",
                        "SQL": "https://www.coursera.org/learn/sql-for-data-science",
                        "Deep Learning": "https://www.coursera.org/specializations/deep-learning"
                    }
                    
                    if missing_skills:
                        st.write("Рекомендуемые курсы для улучшения навыков:")
                        for skill in missing_skills:
                            if skill in coursera_courses:
                                st.write(f"- [{skill}]({coursera_courses[skill]})")
                    else:
                        st.write("У вас есть все необходимые навыки!")
                
                st.subheader("Прогноз зарплаты")
                if result['predicted_salary']:
                    salary = result['predicted_salary']
                    fig = go.Figure(go.Indicator(
                        mode = "number+gauge+delta",
                        value = salary,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Прогнозируемая зарплата"},
                        delta = {'reference': 100000},
                        gauge = {
                            'axis': {'range': [None, 200000]},
                            'bar': {'color': "#4CAF50"},
                            'steps': [
                                {'range': [0, 50000], 'color': "lightgray"},
                                {'range': [50000, 100000], 'color': "gray"}],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 150000}}))
                    st.plotly_chart(fig)
                    st.write(f"Прогнозируемая зарплата: {salary:,.2f} ₽")
                else:
                    st.write("Прогноз зарплаты недоступен для этого резюме.")
            else:
                st.error("Ошибка при анализе резюме. Пожалуйста, попробуйте еще раз.")

# View All Resumes Tab
with tab3:
    st.header("🔍 Все резюме")

    if st.button("Обновить список резюме"):
        with st.spinner("Загрузка резюме..."):
            response = requests.get(f"{API_URL}/resumes/")
        
        if response.status_code == 200:
            resumes = response.json()
            df = pd.DataFrame(resumes)
            
            # Data cleaning and formatting
            df['predicted_salary'] = df['predicted_salary'].fillna(0).astype(float)
            df['formatted_salary'] = df['predicted_salary'].apply(lambda x: f"{x:,.2f} ₽")
            
            # Translate column names
            df.columns = ['ID', 'Должность', 'Опыт', 'Ключевые навыки', 'Местоположение', 'Тип работы', 
                          'Уровень должности', 'Удаленная работа', 'Прогнозируемая зарплата', 'Отформатированная зарплата']
            
            # Display the dataframe
            st.dataframe(df[['Должность', 'Опыт', 'Местоположение', 'Тип работы', 'Уровень должности', 'Отформатированная зарплата']], use_container_width=True)
            
            # Download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Скачать CSV",
                csv,
                "данные_резюме.csv",
                "text/csv",
                key='download-csv'
            )
        else:
            st.error("Ошибка при загрузке резюме. Пожалуйста, попробуйте еще раз.")

# Footer
st.markdown("---")
footer_col1, footer_col2 = st.columns(2)
with footer_col1:
    st.markdown("Разработано Рикардо Самбрано")
with footer_col2:
    st.markdown(f"Последнее обновление: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")