# 📊 Pipeline de Dados - Bronze, Silver e Gold

![Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)

## 🏗 Estrutura do Projeto

- 📁 **AIRFLOW-PROJECT/**
  - 📁 `.venv/` - _Ambiente virtual Python_
  - 📁 `airflow_home/` - _Configurações do Airflow_
  - 📁 `assets/` - _Arquivos estáticos (imagens, etc.)_
  - 📁 `dags/` - _DAGs do Airflow_
    - 📄 `dag_pipeline_dados.py` - _Pipeline principal Bronze→Silver→Gold_
  - 📁 `data/` - _Camadas de dados_
    - 📁 `raw/` - _Dados brutos originais_
      - 📄 `raw_data.csv`
    - 📁 `bronze/` - _Dados brutos limpos_
      - 📄 `dados_bronze.csv`
    - 📁 `silver/` - _Dados transformados_
      - 📄 `dados_silver.csv_
    - 📁 `gold/` - _Dados agregados_
      - 📄 `dados_gold.csv_
  - 📁 `logs/` - _Logs de execução_
  - 📁 `plugins/` - _Plugins customizados_
  - 📁 `tmp/` - _Arquivos temporários_
  - 📄 `docker-compose.yml` - _Orquestração de containers_
  - 📄 `Dockerfile` - _Configuração do container_
  - 📄 `.env` - _Variáveis de ambiente_
  - 📄 `README.md` - _Documentação do projeto_
