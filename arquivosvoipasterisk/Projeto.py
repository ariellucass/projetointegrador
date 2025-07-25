import os
import csv
import psycopg2
from psycopg2 import Error

# --- CONFIGURAÇÕES DO BANCO DE DADOS PostgreSQL ---
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "projeto"
DB_USER = "lucas"
DB_PASSWORD = "18059829"
DB_TABLE_NAME = "public.cdr"


CAMINHO_ARQUIVO_CSV = "/var/log/asterisk/cdr-custom/Master.csv"
# ---------------------------

def inserir_registros_no_banco(registros):

    conn = None
    try:
        # Estabelece a conexão com o banco de dados
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # Prepara a query de inserção.

        insert_query = f"""
        INSERT INTO CDR (nomeramal, ramalprincipal, ramaldestino, contexto,
        canalprincipal, canaldestino, aplicacao, sipdestino, ligacaorealizada, ligacaoatendida,
        ligacaofinal, duracao, sequencia, situacao, bandeira, contapares, identificacaounica,
        campousuario) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
        """

        print(f"\nIniciando inserção de {len(registros)} registros na tabela CDR ...")
        for i, registro in enumerate(registros):
            try:

                cursor.execute(insert_query, registro)

            except Exception as e:
                print(f"Erro ao inserir registro na linha {i+1}: {e}")
                conn.rollback()

        conn.commit()
        print("\nTodos os registros processados. Inserção finalizada.")
    except (Exception, Error) as error:
        print(f"Erro ao conectar ou operar com o PostgreSQL: {error}")
        if conn:
            conn.rollback() # Garante que qualquer transação incompleta seja desfeita
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Conexão com o PostgreSQL fechada.")


def processar_e_excluir_csv():

    dados_do_csv = []

    if not os.path.exists(CAMINHO_ARQUIVO_CSV):
        print(f"Erro: O arquivo '{CAMINHO_ARQUIVO_CSV}' não foi encontrado.")
        return

    print(f"\nIniciando a leitura do arquivo: {CAMINHO_ARQUIVO_CSV}\n")

    try:
        # Abre o arquivo para leitura
        with open(CAMINHO_ARQUIVO_CSV, mode='r', newline='', encoding='utf-8') as arquivo_csv:
            leitor_csv = csv.reader(arquivo_csv)
            linha_numero = 0

            for linha in leitor_csv:
                linha_numero += 1
#                print(f"--- Linha {linha_numero} ---")

                registro_da_linha = [] # Variável para armazenar os campos da linha atual
                for i, campo in enumerate(linha):
                    campo_processado = campo.strip()
#                    print(f"Campo {i+1}: {campo_processado}")
                    registro_da_linha.append(campo_processado) # Adiciona o campo processado à lista do registro atual

                # Garante que a linha tem exatamente 18 campos antes de adicionar.
                if len(registro_da_linha) < 18:
                    registro_da_linha.extend([''] * (18 - len(registro_da_linha)))
                elif len(registro_da_linha) > 18:
                    registro_da_linha = registro_da_linha[:18]

                dados_do_csv.append(registro_da_linha) # Adiciona o registro completo à lista principal

        print("Leitura do arquivo CSV finalizada com sucesso.")

        # --- Chamada da função de inserção ---
        if dados_do_csv: # Só chama se houver dados para inserir
            inserir_registros_no_banco(dados_do_csv)
        else:
            print("Nenhum dado encontrado no CSV para inserir no banco de dados.")

        # Excluir o arquivo após a leitura e inserção
        print(f"\nTentando excluir o arquivo: {CAMINHO_ARQUIVO_CSV}...")
        os.remove(CAMINHO_ARQUIVO_CSV)
        print("Arquivo excluído com sucesso!")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{CAMINHO_ARQUIVO_CSV}' não foi encontrado.")
    except PermissionError:
        print(f"Erro: Permissão negada para ler ou excluir o arquivo '{CAMINHO_ARQUIVO_CSV}'. Verifique as permissões.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a leitura/processamento do CSV: {e}")

# Executa a função principal quando o script é iniciado
if __name__ == "__main__":
    processar_e_excluir_csv()
