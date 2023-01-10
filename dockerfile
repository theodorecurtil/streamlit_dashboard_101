FROM python:3.9

EXPOSE 8501

WORKDIR /app

COPY requirements.txt helper.py main.py CaseStudy_Data.csv ./

RUN pip install -r ./requirements.txt

ENTRYPOINT ["streamlit", "run", "./main.py"]
