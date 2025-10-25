"""
Serviço de atribuições
"""
from django.db import transaction
from django.contrib.auth.models import User
from habitacao.models import ApplicationAssignment, Beneficiary, ApplicationActionHistory
from habitacao.choices import ApplicationAction as ActionType


class AssignmentService:
    """Serviço de gerenciamento de atribuições"""

    @staticmethod
    @transaction.atomic
    def assign(beneficiary_id, assigned_to_id, user):
        """
        Atribui beneficiário a um analista
        """
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)
        assigned_to = User.objects.get(id=assigned_to_id)

        # Encerra atribuições anteriores
        ApplicationAssignment.objects.filter(
            beneficiary=beneficiary,
            active=True
        ).update(active=False)

        # Cria nova atribuição
        assignment = ApplicationAssignment.objects.create(
            beneficiary=beneficiary,
            assigned_to=assigned_to,
            active=True
        )

        # Registra ação
        ApplicationActionHistory.objects.create(
            beneficiary=beneficiary,
            action=ActionType.NOTE,
            from_status=beneficiary.status,
            to_status=beneficiary.status,
            message=f"Atribuído para {assigned_to.get_full_name()}",
            created_by=user
        )

        return assignment

    @staticmethod
    def get_active(beneficiary_id):
        """Obtém atribuição ativa do beneficiário"""
        try:
            return ApplicationAssignment.objects.select_related(
                'assigned_to', 'beneficiary'
            ).get(
                beneficiary_id=beneficiary_id,
                active=True
            )
        except ApplicationAssignment.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def close_active(beneficiary_id, user):
        """Encerra atribuição ativa"""
        updated = ApplicationAssignment.objects.filter(
            beneficiary_id=beneficiary_id,
            active=True
        ).update(active=False)

        if updated > 0:
            beneficiary = Beneficiary.objects.get(id=beneficiary_id)

            ApplicationActionHistory.objects.create(
                beneficiary=beneficiary,
                action=ActionType.NOTE,
                from_status=beneficiary.status,
                to_status=beneficiary.status,
                message="Atribuição encerrada",
                created_by=user
            )

        return updated > 0

    @staticmethod
    def list_by_user(user_id, active_only=True):
        """Lista atribuições de um usuário"""
        queryset = ApplicationAssignment.objects.select_related(
            'beneficiary', 'beneficiary__municipality'
        ).filter(assigned_to_id=user_id)

        if active_only:
            queryset = queryset.filter(active=True)

        return queryset.order_by('-assigned_at')
