#!/usr/bin/env python3
"""
Script de verificação de segurança do sistema Habitação MCMV
Verifica configurações críticas antes do deploy em produção
"""

import os
import sys
from pathlib import Path

# Cores para output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Imprime cabeçalho colorido"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"{GREEN}✓{RESET} {text}")

def print_warning(text):
    """Imprime aviso"""
    print(f"{YELLOW}⚠{RESET} {text}")

def print_error(text):
    """Imprime erro"""
    print(f"{RED}✗{RESET} {text}")

def check_file_exists(filepath, description):
    """Verifica se arquivo existe"""
    if os.path.exists(filepath):
        print_success(f"{description} existe")
        return True
    else:
        print_error(f"{description} NÃO encontrado")
        return False

def check_env_file():
    """Verifica arquivo .env"""
    print_header("Verificando arquivo .env")

    if not os.path.exists('.env'):
        print_error("Arquivo .env não encontrado!")
        print_warning("Copie .env.example para .env e configure as variáveis")
        return False

    print_success("Arquivo .env encontrado")

    # Verificar variáveis críticas
    critical_vars = [
        'SECRET_KEY',
        'DB_PASSWORD',
        'MYSQL_ROOT_PASSWORD',
        'ADMIN_PASSWORD',
    ]

    env_content = open('.env').read()
    issues = []

    for var in critical_vars:
        if var not in env_content:
            print_error(f"Variável {var} não encontrada no .env")
            issues.append(var)
        elif f"{var}=" in env_content:
            # Verificar se tem valor
            for line in env_content.split('\n'):
                if line.startswith(f"{var}="):
                    value = line.split('=', 1)[1].strip()
                    if not value or value.startswith('#'):
                        print_error(f"Variável {var} está vazia")
                        issues.append(var)
                    elif 'change' in value.lower() or 'example' in value.lower() or 'insecure' in value.lower():
                        print_error(f"Variável {var} contém valor padrão/inseguro")
                        issues.append(var)
                    elif len(value) < 16:
                        print_warning(f"Variável {var} pode ser muito curta (recomendado: 16+ caracteres)")
                    else:
                        print_success(f"Variável {var} configurada")

    return len(issues) == 0

def check_debug_mode():
    """Verifica se DEBUG está desligado em produção"""
    print_header("Verificando modo DEBUG")

    if not os.path.exists('.env'):
        print_warning("Arquivo .env não encontrado")
        return False

    env_content = open('.env').read()

    for line in env_content.split('\n'):
        if line.startswith('DEBUG='):
            value = line.split('=', 1)[1].strip()
            if value.lower() in ['false', '0', 'no']:
                print_success("DEBUG está DESLIGADO (recomendado para produção)")
                return True
            else:
                print_warning("DEBUG está LIGADO (não recomendado para produção)")
                return False

    print_warning("Variável DEBUG não encontrada no .env")
    return False

def check_allowed_hosts():
    """Verifica ALLOWED_HOSTS"""
    print_header("Verificando ALLOWED_HOSTS")

    if not os.path.exists('.env'):
        return False

    env_content = open('.env').read()

    for line in env_content.split('\n'):
        if line.startswith('ALLOWED_HOSTS='):
            value = line.split('=', 1)[1].strip()
            if value and value != '*':
                print_success(f"ALLOWED_HOSTS configurado: {value}")
                if 'localhost' in value.lower() or '127.0.0.1' in value:
                    print_warning("ALLOWED_HOSTS contém localhost (remova em produção)")
                return True
            elif value == '*':
                print_error("ALLOWED_HOSTS='*' é INSEGURO em produção")
                return False

    print_error("ALLOWED_HOSTS não configurado")
    return False

def check_ssl_settings():
    """Verifica configurações SSL"""
    print_header("Verificando configurações SSL/HTTPS")

    if not os.path.exists('.env'):
        return False

    env_content = open('.env').read()
    ssl_vars = {
        'SECURE_SSL_REDIRECT': 'True',
        'SESSION_COOKIE_SECURE': 'True',
        'CSRF_COOKIE_SECURE': 'True',
    }

    all_ok = True
    for var, expected in ssl_vars.items():
        found = False
        for line in env_content.split('\n'):
            if line.startswith(f'{var}='):
                value = line.split('=', 1)[1].strip()
                found = True
                if value == expected:
                    print_success(f"{var}={value}")
                else:
                    print_warning(f"{var}={value} (recomendado: {expected} para produção)")
                    all_ok = False
                break

        if not found:
            print_warning(f"{var} não configurado")
            all_ok = False

    return all_ok

def check_gitignore():
    """Verifica .gitignore"""
    print_header("Verificando .gitignore")

    if not os.path.exists('.gitignore'):
        print_error(".gitignore não encontrado")
        return False

    gitignore = open('.gitignore').read()

    required_entries = ['.env', '*.log', 'media/', 'staticfiles/']
    all_ok = True

    for entry in required_entries:
        if entry in gitignore:
            print_success(f"'{entry}' está no .gitignore")
        else:
            print_error(f"'{entry}' NÃO está no .gitignore")
            all_ok = False

    return all_ok

def check_file_permissions():
    """Verifica permissões de arquivos sensíveis"""
    print_header("Verificando permissões de arquivos")

    if os.path.exists('.env'):
        stat = os.stat('.env')
        perms = oct(stat.st_mode)[-3:]

        if perms in ['600', '400']:
            print_success(f"Permissões do .env: {perms} (seguro)")
        else:
            print_warning(f"Permissões do .env: {perms} (recomendado: 600)")
            print_warning("Execute: chmod 600 .env")

    if os.path.exists('entrypoint.sh'):
        stat = os.stat('entrypoint.sh')
        perms = oct(stat.st_mode)[-3:]

        if perms in ['755', '700']:
            print_success(f"Permissões do entrypoint.sh: {perms}")
        else:
            print_warning(f"Permissões do entrypoint.sh: {perms} (recomendado: 755)")
            print_warning("Execute: chmod +x entrypoint.sh")

    return True

def check_required_files():
    """Verifica arquivos necessários"""
    print_header("Verificando arquivos necessários")

    required_files = {
        'docker-compose.yml': 'Docker Compose',
        'Dockerfile': 'Dockerfile',
        'requirements.txt': 'Requirements',
        'manage.py': 'Django manage.py',
        'entrypoint.sh': 'Entrypoint script',
        'SECURITY.md': 'Documentação de segurança',
    }

    all_ok = True
    for filepath, description in required_files.items():
        if not check_file_exists(filepath, description):
            all_ok = False

    return all_ok

def main():
    """Função principal"""
    print_header("VERIFICAÇÃO DE SEGURANÇA - HABITAÇÃO MCMV")

    # Mudar para diretório do projeto
    os.chdir(Path(__file__).parent)

    results = {
        'Arquivo .env': check_env_file(),
        'Modo DEBUG': check_debug_mode(),
        'ALLOWED_HOSTS': check_allowed_hosts(),
        'Configurações SSL': check_ssl_settings(),
        '.gitignore': check_gitignore(),
        'Permissões': check_file_permissions(),
        'Arquivos necessários': check_required_files(),
    }

    # Resumo
    print_header("RESUMO DA VERIFICAÇÃO")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for check, result in results.items():
        if result:
            print_success(f"{check}: OK")
        else:
            print_error(f"{check}: FALHOU")

    print(f"\n{BLUE}Resultado: {passed}/{total} verificações passaram{RESET}\n")

    if passed == total:
        print_success("✓ Todas as verificações passaram!")
        print_success("Sistema pronto para produção.")
        return 0
    elif passed >= total * 0.7:
        print_warning("⚠ Algumas verificações falharam.")
        print_warning("Revise os itens acima antes do deploy em produção.")
        return 1
    else:
        print_error("✗ Muitas verificações falharam!")
        print_error("NÃO faça deploy em produção sem corrigir os problemas.")
        return 2

if __name__ == '__main__':
    sys.exit(main())
