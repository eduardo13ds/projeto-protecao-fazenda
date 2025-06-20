#!/usr/bin/env python3
"""
Script para corrigir o hash da senha do usuário admin no banco de dados.
Este script gera um hash compatível com Werkzeug e atualiza o banco.
"""

import mysql.connector
from werkzeug.security import generate_password_hash

def fix_admin_password():
    """Corrige o hash da senha do usuário admin no banco de dados."""

    print("🔧 Corrigindo senha do usuário admin...")

    try:
        # Configurações do banco
        config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '',
            'database': 'stormguard'
        }

        # Gera o hash correto para a senha 'admin123'
        senha_original = 'admin123'
        hash_correto = generate_password_hash(senha_original)

        print(f"   📝 Gerando hash para senha '{senha_original}'...")
        print(f"   🔐 Hash gerado: {hash_correto[:50]}...")

        # Conecta ao banco
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Verifica se o usuário admin existe
        cursor.execute("SELECT ID_Usuario, Nome_Usuario, Senha_Hash FROM usuarios WHERE Nome_Usuario = 'admin'")
        resultado = cursor.fetchone()

        if not resultado:
            print("   ❌ Usuário admin não encontrado!")
            return False

        print(f"   👤 Usuário encontrado: ID {resultado[0]} - {resultado[1]}")
        print(f"   🔐 Hash atual: {resultado[2][:50]}...")

        # Atualiza a senha
        update_sql = "UPDATE usuarios SET Senha_Hash = %s WHERE Nome_Usuario = 'admin'"
        cursor.execute(update_sql, (hash_correto,))
        connection.commit()

        # Verifica se a atualização foi bem-sucedida
        if cursor.rowcount > 0:
            print("   ✅ Senha do admin atualizada com sucesso!")

            # Verifica a atualização
            cursor.execute("SELECT Senha_Hash FROM usuarios WHERE Nome_Usuario = 'admin'")
            nova_senha = cursor.fetchone()[0]
            print(f"   🔐 Novo hash: {nova_senha[:50]}...")

            # Testa a senha
            from werkzeug.security import check_password_hash
            if check_password_hash(nova_senha, senha_original):
                print("   ✅ Verificação da senha: OK")
            else:
                print("   ❌ Verificação da senha: FALHOU")
                return False

        else:
            print("   ❌ Nenhuma linha foi atualizada!")
            return False

        cursor.close()
        connection.close()

        print("\n🎉 Correção concluída com sucesso!")
        print("📋 Credenciais para login:")
        print("   • Usuário: admin")
        print("   • Senha: admin123")

        return True

    except mysql.connector.Error as e:
        print(f"   ❌ Erro de banco de dados: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🔧 StormGuard - Correção de Senha do Admin")
    print("=" * 50)

    success = fix_admin_password()

    if success:
        print("\n🚀 Próximos passos:")
        print("   1. Execute: flask run")
        print("   2. Acesse: http://localhost:5000")
        print("   3. Faça login com admin/admin123")
    else:
        print("\n❌ Falhou ao corrigir a senha. Verifique os logs acima.")
