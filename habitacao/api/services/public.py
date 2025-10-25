"""
Serviço de consulta pública
"""
from habitacao.models import Beneficiary


class PublicService:
    """Serviço de consultas públicas (sem autenticação)"""

    @staticmethod
    def get_status_by_protocol_or_cpf(protocol=None, cpf=None):
        """
        Consulta pública por protocolo ou CPF
        Retorna apenas informações básicas de status
        """
        if not protocol and not cpf:
            raise ValueError("Informe o protocolo ou CPF para consulta")

        queryset = Beneficiary.objects.all()

        if protocol:
            queryset = queryset.filter(protocol_number__iexact=protocol)
        elif cpf:
            # Remove formatação do CPF
            cpf_clean = cpf.replace('.', '').replace('-', '').replace(' ', '')
            queryset = queryset.filter(cpf__icontains=cpf_clean)

        beneficiary = queryset.first()

        if not beneficiary:
            return None

        # Retorna apenas informações públicas
        return {
            'protocol_number': beneficiary.protocol_number,
            'full_name': beneficiary.full_name,
            'status': beneficiary.status,
            'status_display': beneficiary.get_status_display(),
            'submitted_at': beneficiary.submitted_at,
            'municipality': {
                'name': beneficiary.municipality.name if beneficiary.municipality else None,
                'uf': beneficiary.municipality.uf if beneficiary.municipality else None,
            } if beneficiary.municipality else None,
            # Informações limitadas para segurança
            'cpf_masked': f"***.***.{beneficiary.cpf[-6:-3]}-{beneficiary.cpf[-2:]}" if beneficiary.cpf else None,
        }
