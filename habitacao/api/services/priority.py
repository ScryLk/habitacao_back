"""
Serviço de critérios de priorização
"""
from django.db import transaction
from habitacao.models import PriorityCriteria, BeneficiaryPriority, Beneficiary


class PriorityService:
    """Serviço de gerenciamento de prioridades"""

    @staticmethod
    def list_all():
        """Lista todos os critérios de priorização ativos"""
        return PriorityCriteria.objects.filter(active=True).order_by('group_tag', 'label')

    @staticmethod
    def get_for_beneficiary(beneficiary_id):
        """Lista critérios aplicados a um beneficiário"""
        return BeneficiaryPriority.objects.filter(
            beneficiary_id=beneficiary_id
        ).select_related('criteria')

    @staticmethod
    @transaction.atomic
    def replace_for_beneficiary(beneficiary_id, criteria_ids):
        """
        Substitui conjunto de critérios de um beneficiário
        Remove todos existentes e adiciona os novos
        """
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)

        # Remove todos existentes
        BeneficiaryPriority.objects.filter(beneficiary=beneficiary).delete()

        # Adiciona novos
        priorities = []
        for criteria_id in criteria_ids:
            criteria = PriorityCriteria.objects.get(id=criteria_id)
            priorities.append(
                BeneficiaryPriority(
                    beneficiary=beneficiary,
                    criteria=criteria
                )
            )

        BeneficiaryPriority.objects.bulk_create(priorities)

        return BeneficiaryPriority.objects.filter(beneficiary=beneficiary).select_related('criteria')

    @staticmethod
    @transaction.atomic
    def add_criteria(beneficiary_id, criteria_id):
        """Adiciona um critério ao beneficiário"""
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)
        criteria = PriorityCriteria.objects.get(id=criteria_id)

        priority, created = BeneficiaryPriority.objects.get_or_create(
            beneficiary=beneficiary,
            criteria=criteria
        )

        return priority

    @staticmethod
    def remove_criteria(beneficiary_id, criteria_id):
        """Remove um critério do beneficiário"""
        deleted_count = BeneficiaryPriority.objects.filter(
            beneficiary_id=beneficiary_id,
            criteria_id=criteria_id
        ).delete()[0]

        return deleted_count > 0
