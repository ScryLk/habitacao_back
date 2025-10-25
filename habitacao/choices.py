"""
Choices (Enums) para o app Habitação
"""
from django.db import models


class ApplicationStatus(models.TextChoices):
    """Status da inscrição do beneficiário"""
    DRAFT = 'DRAFT', 'Rascunho'
    SUBMITTED = 'SUBMITTED', 'Submetida'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Em Análise'
    CORRECTION_REQUESTED = 'CORRECTION_REQUESTED', 'Correção Solicitada'
    APPROVED = 'APPROVED', 'Aprovada'
    REJECTED = 'REJECTED', 'Rejeitada'


class UserRole(models.TextChoices):
    """Papel/função do usuário no sistema"""
    ADMIN = 'ADMIN', 'Administrador'
    COORDINATOR = 'COORDINATOR', 'Coordenador'
    ANALYST = 'ANALYST', 'Analista'
    CLERK = 'CLERK', 'Atendente'


class MaritalStatus(models.TextChoices):
    """Estado civil"""
    SOLTEIRO = 'SOLTEIRO', 'Solteiro(a)'
    CASADO = 'CASADO', 'Casado(a)'
    UNIAO_ESTAVEL = 'UNIAO_ESTAVEL', 'União Estável'
    VIUVO = 'VIUVO', 'Viúvo(a)'
    DIVORCIADO = 'DIVORCIADO', 'Divorciado(a)'
    SEPARADO = 'SEPARADO', 'Separado(a)'
    OUTRO = 'OUTRO', 'Outro'


class Gender(models.TextChoices):
    """Gênero"""
    MASCULINO = 'MASCULINO', 'Masculino'
    FEMININO = 'FEMININO', 'Feminino'
    OUTRO = 'OUTRO', 'Outro'
    NAO_INFORMADO = 'NAO_INFORMADO', 'Não informado'


class UF(models.TextChoices):
    """Estados brasileiros"""
    AC = 'AC', 'Acre'
    AL = 'AL', 'Alagoas'
    AP = 'AP', 'Amapá'
    AM = 'AM', 'Amazonas'
    BA = 'BA', 'Bahia'
    CE = 'CE', 'Ceará'
    DF = 'DF', 'Distrito Federal'
    ES = 'ES', 'Espírito Santo'
    GO = 'GO', 'Goiás'
    MA = 'MA', 'Maranhão'
    MT = 'MT', 'Mato Grosso'
    MS = 'MS', 'Mato Grosso do Sul'
    MG = 'MG', 'Minas Gerais'
    PA = 'PA', 'Pará'
    PB = 'PB', 'Paraíba'
    PR = 'PR', 'Paraná'
    PE = 'PE', 'Pernambuco'
    PI = 'PI', 'Piauí'
    RJ = 'RJ', 'Rio de Janeiro'
    RN = 'RN', 'Rio Grande do Norte'
    RS = 'RS', 'Rio Grande do Sul'
    RO = 'RO', 'Rondônia'
    RR = 'RR', 'Roraima'
    SC = 'SC', 'Santa Catarina'
    SP = 'SP', 'São Paulo'
    SE = 'SE', 'Sergipe'
    TO = 'TO', 'Tocantins'


class ApplicationAction(models.TextChoices):
    """Ações possíveis no fluxo da inscrição"""
    SUBMIT = 'SUBMIT', 'Submeter'
    START_REVIEW = 'START_REVIEW', 'Iniciar Análise'
    REQUEST_CORRECTION = 'REQUEST_CORRECTION', 'Solicitar Correção'
    APPROVE = 'APPROVE', 'Aprovar'
    REJECT = 'REJECT', 'Rejeitar'
    UPLOAD_DOC = 'UPLOAD_DOC', 'Upload de Documento'
    VALIDATE_DOC = 'VALIDATE_DOC', 'Validar Documento'
    NOTE = 'NOTE', 'Adicionar Nota'
    EDIT = 'EDIT', 'Editar'
