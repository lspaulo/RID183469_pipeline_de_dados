# 📊 Pipeline de Dados - Bronze, Silver e Gold

![Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)


## 🚀 Sobre o Projeto

Pipeline de dados em 3 camadas desenvolvido como desafio final do curso de Engenheiro de Dados da Escola DNC.

## 🔧 Funcionalidades

### 1️⃣ Camada Bronze
- ✅ Upload de dados brutos
- 📊 Log de estatísticas
- 💾 Armazenamento inicial

### 2️⃣ Camada Silver
- 🧼 Limpeza de dados
- ✉️ Validação de emails
- 📅 Correção de datas
- 🧮 Cálculo de idades

### 3️⃣ Camada Gold
- 📊 Agregação de dados
- 🗂️ Criação de faixas etárias
- 📈 Métricas analíticas

## ⚙️ Configuração

### Pré-requisitos
- Docker
- Docker Compose
- Python 3.8+

```bash
# Clone o repositório
git clone [URL_DO_REPO]

# Inicie os containers
docker-compose up -d

## 🏗 Estrutura do Projeto

AIRFLOW-PROJECT/
├── .venv/               # Ambiente virtual Python
├── airflow_home/        # Configurações do Airflow
├── assets/              # Arquivos estáticos
├── dags/
│   └── dag_pipeline_dados.py  # Pipeline principal
├── data/
│   ├── raw/            # Dados brutos
│   │   └── raw_data.csv
│   ├── bronze/         # Dados limpos
│   │   └── dados_bronze.csv
│   ├── silver/         # Dados transformados
│   │   └── dados_silver.csv
│   └── gold/           # Dados agregados
│       └── dados_gold.csv
├── logs/               # Logs de execução
├── plugins/            # Plugins customizados
├── tmp/                # Arquivos temporários
├── docker-compose.yml  # Configuração Docker
├── Dockerfile          # Imagem Docker
├── .env                # Variáveis de ambiente
└── README.md           # Documentação
