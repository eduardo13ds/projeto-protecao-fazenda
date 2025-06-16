# create_user.py
# --------------------------------------------------------------------
# Este script interativo ajuda a criar um novo usuário com uma senha segura (hash).
# Ele não faz parte da aplicação Flask, é uma ferramenta de apoio.
#
# Como usar:
# 1. Rode no terminal: python create_user.py
# 2. Responda às perguntas para inserir os detalhes do usuário.
#    A senha não aparecerá na tela enquanto você digita.
# 3. Copie o comando SQL gerado na saída.
# 4. Cole e execute o comando no seu cliente de banco de dados.
# --------------------------------------------------------------------

from werkzeug.security import generate_password_hash
import getpass # Módulo para inserção segura de senhas

print("--- Ferramenta Interativa de Criação de Usuário ---")
print("Por favor, insira os detalhes para o novo usuário.")

# --- 1. Coleta interativa dos dados ---

# Garante que o ID do usuário seja um número inteiro
while True:
    try:
        id_usuario = int(input("ID do Usuário (ex: 5): ").strip())
        break
    except ValueError:
        print("Erro: O ID deve ser um número inteiro. Tente novamente.")

nome_usuario = input("Nome de usuário (ex: j.silva): ").strip()
nome_completo = input("Nome completo (ex: João da Silva): ").strip()
email = input("Email (ex: joao.silva@email.com): ").strip()

# Usa getpass para que a senha não seja exibida no terminal
senha_plana = getpass.getpass("Senha (não será visível): ").strip()


# --- 2. Geração do Hash da Senha ---
# A função generate_password_hash faz todo o trabalho pesado.
senha_hash = generate_password_hash(senha_plana)

print("\n" + "="*50)
print("\n--- DADOS PROCESSADOS ---")
print(f"Usuário: {nome_usuario}")
print(f"Senha Hash Gerada (este é o valor que vai para o banco):")
print(f"'{senha_hash}'") # Adiciona aspas para facilitar o copia e cola
print("\n" + "="*50 + "\n")


# --- 3. Geração do Comando SQL ---
# O script monta o comando INSERT para você com os dados inseridos.
sql_command = f"""
INSERT INTO `usuarios`
(`ID_Usuario`, `Nome_Usuario`, `Senha_Hash`, `Nome_Completo`, `Email`, `Status_Conta`, `Data_Criacao`)
VALUES
    ({id_usuario}, '{nome_usuario}', '{senha_hash}', '{nome_completo}', '{email}', 'Ativa', NOW());
    """

print("Comando SQL para inserir no banco de dados (copie e cole):")
print(sql_command)
