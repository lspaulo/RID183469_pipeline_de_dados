import traceback
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import pandas as pd
from datetime import datetime
import os
import logging
from airflow.models import TaskInstance

# Parâmetros básicos do DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),  # ajusta a data de início conforme necessário
    'retries': 1,
}

# Criação do DAG com definição de schedule e sem "catchup"
with DAG(
    'pipeline_dados',
    default_args=default_args,
    description='Pipeline de dados: do carregamento à transformação final',
    schedule_interval='@daily',  # ou ajuste o intervalo conforme sua necessidade
    catchup=False,
    tags=['pipeline', 'dados']
) as dag:

    def upload_raw_data_to_bronze(**kwargs):
        """
        Carrega o arquivo CSV de dados brutos e o salva na camada Bronze.
        """
        task_instance = kwargs['ti']

        # Caminhos de entrada e saída para os dados brutos.
        input_path = '/opt/airflow/data/raw/raw_data.csv'       # arquivo de origem com os dados brutos
        output_path = '/opt/airflow/data/bronze/dados_bronze.csv'  # onde os dados brutos serão copiados na camada Bronze

        try:
            # Log inicial
            task_instance.log.info("🔵 Iniciando upload para camada Bronze...")
            task_instance.log.info(f"📤 Origem: {input_path}")
            task_instance.log.info(f"📥 Destino: {output_path}")

            # Ler o CSV original
            df = pd.read_csv(input_path)

            # Garantir que o diretório para bronze existe (caso contrário, cria)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

             # Log da amostra do DataFrame (3 primeiras linhas)
            task_instance.log.info("📋 Amostra dos dados brutos (3 primeiras linhas):\n" + 
                                df.head(3).to_string(index=False))
        
            # Log de estatísticas básicas
            task_instance.log.info("📊 Estatísticas descritivas:\n" +
                                df.describe().to_string())

            # Salvar os dados na camada Bronze
            df.to_csv(output_path, index=False)

            # Log de sucesso
            task_instance.log.info(f"✅ Dados brutos salvos com sucesso na Bronze")
            task_instance.log.info(f"📊 Total de registros: {len(df)}")
            task_instance.log.info(f"💾 Tamanho do arquivo: {os.path.getsize(output_path)/1024:.2f} KB")
        
        except Exception as e:
            print(f"Erro ao carregar os dados brutos: {e}")
            raise

    def process_bronze_to_silver(**kwargs):
        """
        Lê os dados da camada Bronze, realiza a limpeza dos dados e os salva na camada Prata.
        
        As operações de limpeza incluem:
        - Remover registros com campos nulos nas colunas 'name', 'email' e 'date_of_birth'
        - Corrigir emails sem '@'
        - Converter e validar datas de nascimento
        - Calcular idade dos usuários
        """
        ti = kwargs['ti']  # TaskInstance para logging
        input_path = '/opt/airflow/data/bronze/dados_bronze.csv'
        output_path = '/opt/airflow/data/silver/dados_silver.csv'

        try:
            # 1. Carregar dados
            ti.log.info("📥 Carregando dados da camada Bronze...")
            df = pd.read_csv(input_path)
            ti.log.info(f"✅ Dados carregados | Registros: {len(df)}")
            ti.log.info("🔍 Amostra dos dados brutos:\n" + df.head(3).to_markdown())
            
            # 2. Limpeza inicial
            ti.log.info("🧹 Removendo registros com valores nulos...")
            df_clean = df.dropna(subset=['name', 'email', 'date_of_birth'])
            ti.log.info(f"📊 Registros após limpeza: {len(df_clean)} (removidos: {len(df)-len(df_clean)})")
            
            # 3. Correção de emails
            ti.log.info("✉️ Corrigindo formatos de email...")
            email_mask = df_clean['email'].apply(lambda x: isinstance(x, str) and 'example' in x and '@' not in x)
            ti.log.info(f"🔧 Emails a corrigir: {email_mask.sum()}")
            
            df_clean['email'] = df_clean['email'].apply(
                lambda x: x.replace("example", "@example") if isinstance(x, str) and 'example' in x and '@' not in x else x
            )
            ti.log.info("📩 Amostra de emails corrigidos:\n" + 
                    df_clean[email_mask].head(3)[['email']].to_markdown())
            
            # 4. Tratamento de datas
            ti.log.info("📅 Convertendo datas de nascimento...")
            df_clean['date_of_birth'] = pd.to_datetime(df_clean['date_of_birth'], errors='coerce')
            date_mask = df_clean['date_of_birth'].isna()
            ti.log.info(f"⚠️ Datas inválidas detectadas: {date_mask.sum()}")
            
            df_clean = df_clean.dropna(subset=['date_of_birth'])
            ti.log.info(f"🗓️ Registros após filtro de datas: {len(df_clean)}")
            
            # 5. Cálculo de idade
            ti.log.info("🧮 Calculando idades...")
            today = pd.Timestamp(datetime.today().strftime('%Y-%m-%d'))
            df_clean['age'] = df_clean['date_of_birth'].apply(
                lambda dob: (today.year - dob.year) - ((today.month, today.day) < (dob.month, dob.day))
            )
            ti.log.info("📊 Distribuição de idades:\n" + 
                    df_clean['age'].describe().to_markdown())
            
            # 6. Salvar dados
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df_clean.to_csv(output_path, index=False)
            ti.log.info(f"💾 Dados salvos na Silver | Registros: {len(df_clean)}")
            ti.log.info(f"📁 Local: {output_path}")
            ti.log.info("🔎 Amostra final:\n" + df_clean.head(3).to_markdown())
            
        except Exception as e:
            ti.log.error(f"❌ Falha no processamento: {str(e)}")
            ti.log.error("🔄 Stack Trace:\n" + traceback.format_exc())
            raise

    def process_silver_to_gold(ti, **kwargs):
        """
        Lê os dados da camada Prata, executa transformações adicionais e salva os dados transformados na camada Ouro.
        
        Transformações realizadas:
        - Criação de faixas etárias a partir da coluna "age".
        - Agregação dos dados por faixa etária e status de assinatura ("active" ou "inactive"),
            contando o número de usuários em cada grupo.
        """
        input_path = '/opt/airflow/data/silver/dados_silver.csv'
        output_path = '/opt/airflow/data/gold/dados_gold.csv'
        
        try:
            df = pd.read_csv(input_path)
            ti.log.info("Dados da camada Prata carregados com sucesso.")
        except Exception as e:
            ti.log.error(f"Erro ao ler dados da camada Prata: {e}")
            raise
        
        # Verifica se a coluna 'age' está presente
        if 'age' not in df.columns:
            msg = "Coluna 'age' ausente. Verifique se o processamento anterior foi realizado corretamente."
            ti.log.error(msg)
            raise KeyError(msg)
        
        # Criação das faixas etárias
        bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        labels = ["0-10", "11-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71-80", "81-90", "91-100"]
        df['age_range'] = pd.cut(
            df['age'],
            bins=bins,
            labels=labels,
            include_lowest=True,
            right=False           
        ).cat.add_categories(["Idade inválida"]).fillna("Idade inválida")
        
        # Agregar dados: contar quantos usuários existem por faixa etária e status
        agregacao = (
            df.groupby(['age_range', 'subscription_status'])
            .size()
            .reset_index(name="user_count")
            .sort_values(['age_range', 'user_count'], ascending=[True, False])
        )
        # Log da tabela completa (formato markdown para melhor visualização)
        ti.log.info("\n🔍 Tabela completa:\n" + agregacao.to_markdown(index=False))
        ti.log.info("Dados agregados por faixa etária e status.")
        
        # Garante que o diretório para a camada Ouro existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        agregacao.to_csv(output_path, index=False)
        
        ti.log.info(f"💾 Dados salvos na Gold | Registros: {len(agregacao)}")
        ti.log.info(f"📁 Local: {output_path}")
        ti.log.info("🔎 Amostra final:\n" + agregacao.head(3).to_markdown())
        
        return "Transformações para a camada Ouro concluídas"

    def process_silver_to_gold(ti, **kwargs):
        """
        Lê os dados da camada Prata, executa transformações adicionais e salva os dados transformados na camada Ouro.
        
        Transformações realizadas:
        - Criação de faixas etárias a partir da coluna "age".
        - Agregação dos dados por faixa etária e status de assinatura ("active" ou "inactive"),
            contando o número de usuários em cada grupo.
        """
        input_path = '/opt/airflow/data/silver/dados_silver.csv'
        output_path = '/opt/airflow/data/gold/dados_gold.csv'
        
        try:
            df = pd.read_csv(input_path)
            ti.log.info("Dados da camada Prata carregados com sucesso.")
        except Exception as e:
            ti.log.error(f"Erro ao ler dados da camada Prata: {e}")
            raise
        
        # Verifica se a coluna 'age' está presente
        if 'age' not in df.columns:
            msg = "Coluna 'age' ausente. Verifique se o processamento anterior foi realizado corretamente."
            ti.log.error(msg)
            raise KeyError(msg)
        
        # Criação das faixas etárias
        bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        labels = ["0-10", "11-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71-80", "81-90", "91-100"]
        df['age_range'] = pd.cut(df['age'], bins=bins, labels=labels, include_lowest=True)
        ti.log.info("Faixas etárias criadas com sucesso.")
        
        # Agregar dados: contar quantos usuários existem por faixa etária e status
        agregacao = df.groupby(['age_range', 'subscription_status']).size().reset_index(name="user_count")
        ti.log.info("Dados agregados por faixa etária e status.")
        
        # Garante que o diretório para a camada Ouro existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        agregacao.to_csv(output_path, index=False)
        
        ti.log.info(f"💾 Dados salvos na Gold | Registros: {len(agregacao)}")
        ti.log.info(f"📁 Local: {output_path}")
        ti.log.info("🔎 Amostra final:\n" + agregacao.head(3).to_markdown())
        
        return "Transformações para a camada Ouro concluídas"


    # Criação dos operadores para cada etapa
    task_carregar = PythonOperator(
        task_id='upload_raw_data_to_bronze',
        python_callable=upload_raw_data_to_bronze
    )

    task_transformar = PythonOperator(
        task_id='process_bronze_to_silver',
        python_callable=process_bronze_to_silver
    )

    task_processar = PythonOperator(
        task_id='process_silver_to_gold',
        python_callable=process_silver_to_gold
    )
    # Definição das dependências (ordem sequencial das tarefas)
    task_carregar >> task_transformar >> task_processar
