#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug para verificar conexão com banco de dados e recuperação de dados
"""

import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Usuario, Fazenda, Sensor, Atuador, NivelAcesso, TipoSensor, TipoAtuador, Alerta, RegistroLeitura, RegistroComandoAtuador

def test_database_connection():
    """Testa a conexão com o banco de dados."""
    app = create_app()

    with app.app_context():
        try:
            # Testar conexão básica
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT 1"))
            print("✅ Conexão com banco de dados OK")

            # Testar cada modelo
            models_to_test = {
                'usuarios': Usuario,
                'fazendas': Fazenda,
                'sensores': Sensor,
                'atuadores': Atuador,
                'niveis_acesso': NivelAcesso,
                'tipos_sensor': TipoSensor,
                'tipos_atuador': TipoAtuador,
                'alertas': Alerta,
                'registro_leituras': RegistroLeitura,
                'registro_comandos': RegistroComandoAtuador
            }

            print("\n=== TESTE DE MODELOS ===")

            for table_name, Model in models_to_test.items():
                print(f"\n--- Testando: {table_name} ---")

                try:
                    # Contar registros
                    count = Model.query.count()
                    print(f"Registros encontrados: {count}")

                    if count > 0:
                        # Pegar um registro de exemplo
                        first_item = Model.query.first()
                        print(f"Primeiro item: {first_item}")
                        print(f"Tipo do item: {type(first_item)}")

                        # Listar atributos do modelo
                        headers = [c.key for c in Model.__table__.columns]
                        print(f"Headers (nomes dos atributos): {headers}")

                        # Testar acesso aos atributos
                        print("Valores dos atributos:")
                        for header in headers:
                            try:
                                value = getattr(first_item, header)
                                print(f"  {header}: {value} ({type(value)})")
                            except Exception as e:
                                print(f"  {header}: ERRO - {e}")

                        # Testar conversão para dicionário
                        try:
                            item_dict = {}
                            for header in headers:
                                item_dict[header] = getattr(first_item, header, None)
                            print(f"Dicionário criado: {item_dict}")
                        except Exception as e:
                            print(f"Erro ao criar dicionário: {e}")

                    print(f"✅ {table_name}: OK")

                except Exception as e:
                    print(f"❌ {table_name}: ERRO - {e}")
                    import traceback
                    traceback.print_exc()

            # Teste específico para usuários (já que sabemos que existem dados)
            print("\n=== TESTE ESPECÍFICO: USUÁRIOS ===")
            try:
                usuarios = Usuario.query.all()
                print(f"Total de usuários: {len(usuarios)}")

                for i, user in enumerate(usuarios):
                    print(f"\nUsuário {i+1}:")
                    print(f"  ID: {user.id_usuario}")
                    print(f"  Nome: {user.nome_usuario}")
                    print(f"  Email: {user.email}")
                    print(f"  Status: {user.status_conta}")

            except Exception as e:
                print(f"Erro no teste específico de usuários: {e}")
                import traceback
                traceback.print_exc()

        except Exception as e:
            print(f"❌ Erro na conexão com banco de dados: {e}")
            import traceback
            traceback.print_exc()

def test_raw_sql():
    """Testa consultas SQL diretas."""
    app = create_app()

    with app.app_context():
        try:
            print("\n=== TESTE SQL DIRETO ===")

            # Consulta direta na tabela usuarios
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT * FROM usuarios LIMIT 3"))
                rows = result.fetchall()

            print(f"Registros encontrados via SQL direto: {len(rows)}")

            for i, row in enumerate(rows):
                print(f"\nRegistro {i+1}:")
                print(f"  Raw row: {row}")
                print(f"  Row type: {type(row)}")

                # Tentar acessar por índice
                try:
                    print(f"  Por índice - ID: {row[0]}, Nome: {row[1]}")
                except Exception as e:
                    print(f"  Erro ao acessar por índice: {e}")

                # Tentar acessar por nome da coluna
                try:
                    print(f"  Por nome - ID: {row['ID_Usuario']}, Nome: {row['Nome_Usuario']}")
                except Exception as e:
                    print(f"  Erro ao acessar por nome: {e}")

        except Exception as e:
            print(f"Erro no teste SQL direto: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("=== SCRIPT DE DEBUG DO BANCO DE DADOS ===")
    test_database_connection()
    test_raw_sql()
    print("\n=== FIM DO DEBUG ===")
