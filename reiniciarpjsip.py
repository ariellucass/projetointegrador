import subprocess

def executar_comando_asterisk(comando_asterisk):
    comando_completo = ['sudo', 'asterisk', '-rx', comando_asterisk]
    try:
        resultado = subprocess.run(
            comando_completo,
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Comando executado com sucesso!")
        return resultado.stdout

    except FileNotFoundError:
        return "⚠️ Erro: Comando 'sudo' ou 'asterisk' não encontrado. Verifique se o Asterisk está instalado e no PATH do sistema."
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar o comando (Código de Saída: {e.returncode}):")
        return e.stderr
    except Exception as e:
        return f"🚨 Ocorreu um erro inesperado: {e}"

# --- Script Principal ---
if __name__ == "__main__":
    comando_para_executar = "module reload res_pjsip.so"
    saida_do_comando = executar_comando_asterisk(comando_para_executar)
