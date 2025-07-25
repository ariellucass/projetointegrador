# gerar_cliente.py
import sys
import os

# Verifica se os argumentos corretos foram fornecidos
if len(sys.argv) != 4:
    print("Uso: python gerar_cliente.py <ramal> <nome> <senha>")
    print("Exemplo: python gerar_cliente.py 1001 \"Joao Silva\" senha123")
    sys.exit(1)

# Atribui os argumentos a variáveis
ramal = sys.argv[1]
nome = sys.argv[2]
senha = sys.argv[3]

# Arquivo base fornecido
base_template = """\
[$ramal]
type=endpoint
context=ramais-interno
disallow=all
allow=alaw
allow=ulaw
allow=g729
allow=opus
dtmf_mode=rfc4733
direct_media=no
force_rport=yes
rewrite_contact=yes
auth=auth_$ramal
aors=$ramal
callerid="$nome" <$ramal>

[auth_$ramal]
type=auth
auth_type=userpass
username=$ramal
password=$senha
[$ramal]
type=aor
max_contacts=1
remove_existing=yes
"""

# Realiza as substituições no template
# Usamos replace() para cada variável
output_content = base_template.replace('$ramal', ramal)
output_content = output_content.replace('$nome', nome)
output_content = output_content.replace('$senha', senha)

# Nome do arquivo de saída
output_file = '/etc/asterisk/ramaismoradores.conf'

try:
    # Abre o arquivo em modo de anexação ('a').
    # Se o arquivo não existir, ele será criado.
    # Se existir, o novo conteúdo será adicionado ao final.
    with open(output_file, 'a') as f:
        f.write(output_content + "\n") # Adiciona uma quebra de linha extra para separar blocos
    print(f"Dados do ramal {ramal} adicionados com sucesso ao arquivo '{output_file}'.")
except IOError as e:
    print(f"Erro ao escrever no arquivo '{output_file}': {e}")
    sys.exit(1)
