"""
Serviço de benefícios sociais
"""
from django.db import transaction
from habitacao.models import SocialBenefitType, BeneficiarySocialBenefit, Beneficiary


class SocialBenefitService:
    """Serviço de gerenciamento de benefícios sociais"""

    @staticmethod
    def list_types():
        """Lista todos os tipos de benefícios sociais ativos"""
        return SocialBenefitType.objects.filter(active=True).order_by('label')

    @staticmethod
    def get_for_beneficiary(beneficiary_id):
        """Lista benefícios sociais de um beneficiário"""
        return BeneficiarySocialBenefit.objects.filter(
            beneficiary_id=beneficiary_id
        ).select_related('benefit')

    @staticmethod
    @transaction.atomic
    def replace_for_beneficiary(beneficiary_id, benefit_ids, other_text=''):
        """
        Substitui conjunto de benefícios de um beneficiário
        Remove todos existentes e adiciona os novos
        """
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)

        # Remove todos existentes
        BeneficiarySocialBenefit.objects.filter(beneficiary=beneficiary).delete()

        # Adiciona novos
        benefits = []
        for benefit_id in benefit_ids:
            benefit = SocialBenefitType.objects.get(id=benefit_id)

            # Se for "OUTROS", adiciona o texto especificado
            other_text_value = other_text if benefit.code == 'OUTROS' else ''

            benefits.append(
                BeneficiarySocialBenefit(
                    beneficiary=beneficiary,
                    benefit=benefit,
                    other_text=other_text_value
                )
            )

        BeneficiarySocialBenefit.objects.bulk_create(benefits)

        return BeneficiarySocialBenefit.objects.filter(beneficiary=beneficiary).select_related('benefit')

    @staticmethod
    @transaction.atomic
    def add_benefit(beneficiary_id, benefit_id, other_text=''):
        """Adiciona um benefício ao beneficiário"""
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)
        benefit = SocialBenefitType.objects.get(id=benefit_id)

        social_benefit, created = BeneficiarySocialBenefit.objects.get_or_create(
            beneficiary=beneficiary,
            benefit=benefit,
            defaults={'other_text': other_text}
        )

        if not created and other_text:
            social_benefit.other_text = other_text
            social_benefit.save()

        return social_benefit

    @staticmethod
    def remove_benefit(beneficiary_id, benefit_id):
        """Remove um benefício do beneficiário"""
        deleted_count = BeneficiarySocialBenefit.objects.filter(
            beneficiary_id=beneficiary_id,
            benefit_id=benefit_id
        ).delete()[0]

        return deleted_count > 0
