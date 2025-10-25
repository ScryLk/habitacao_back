"""
Validadores customizados para o app Habitação
"""
from django.core.exceptions import ValidationError
import re


def validate_cpf(value):
    """
    Valida um CPF brasileiro.
    Aceita formatos: 000.000.000-00 ou 00000000000
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', value)

    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        raise ValidationError('CPF deve conter 11 dígitos.')

    # Verifica se todos os dígitos são iguais (CPF inválido)
    if cpf == cpf[0] * 11:
        raise ValidationError('CPF inválido.')

    # Calcula o primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cpf[9]) != digito1:
        raise ValidationError('CPF inválido.')

    # Calcula o segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    if int(cpf[10]) != digito2:
        raise ValidationError('CPF inválido.')

    return value


def validate_nis(value):
    """
    Valida um NIS/PIS/PASEP brasileiro.
    Deve conter exatamente 11 dígitos numéricos.
    """
    # Remove caracteres não numéricos
    nis = re.sub(r'[^0-9]', '', value)

    # Verifica se tem 11 dígitos
    if len(nis) != 11:
        raise ValidationError('NIS deve conter 11 dígitos.')

    # Sequência de multiplicadores
    multiplicadores = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    # Calcula o dígito verificador
    soma = sum(int(nis[i]) * multiplicadores[i] for i in range(10))
    resto = soma % 11
    digito_verificador = 0 if resto < 2 else 11 - resto

    if int(nis[10]) != digito_verificador:
        raise ValidationError('NIS inválido.')

    return value


def validate_cep(value):
    """
    Valida um CEP brasileiro.
    Aceita formatos: 00000-000 ou 00000000
    """
    # Remove caracteres não numéricos
    cep = re.sub(r'[^0-9]', '', value)

    # Verifica se tem 8 dígitos
    if len(cep) != 8:
        raise ValidationError('CEP deve conter 8 dígitos.')

    return value


def validate_phone(value):
    """
    Valida telefone brasileiro.
    Aceita: (00) 0000-0000 ou (00) 00000-0000
    """
    # Remove caracteres não numéricos
    phone = re.sub(r'[^0-9]', '', value)

    # Verifica se tem 10 ou 11 dígitos (fixo ou celular)
    if len(phone) not in [10, 11]:
        raise ValidationError('Telefone deve conter 10 ou 11 dígitos.')

    return value


def validate_positive_income(value):
    """
    Valida que a renda é positiva quando informada.
    """
    if value is not None and value <= 0:
        raise ValidationError('Renda deve ser maior que zero.')

    return value
