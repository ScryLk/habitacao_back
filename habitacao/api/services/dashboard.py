"""
Serviço de dashboard e estatísticas
"""
from django.db.models import Count, Q
from habitacao.models import Beneficiary, DocumentType
from habitacao.choices import ApplicationStatus, UserRole


class DashboardService:
    """Serviço de dashboard e estatísticas"""

    @staticmethod
    def get_overview(user):
        """
        Retorna visão geral/resumo do sistema
        Respeita escopo de município do usuário
        """
        # Base queryset respeitando escopo
        queryset = Beneficiary.objects.all()

        if hasattr(user, 'profile'):
            if user.profile.municipality and user.profile.role not in [UserRole.ADMIN]:
                queryset = queryset.filter(municipality=user.profile.municipality)

        # Contagens por status
        total = queryset.count()
        under_review = queryset.filter(status=ApplicationStatus.UNDER_REVIEW).count()
        approved = queryset.filter(status=ApplicationStatus.APPROVED).count()
        rejected = queryset.filter(status=ApplicationStatus.REJECTED).count()
        draft = queryset.filter(status=ApplicationStatus.DRAFT).count()
        submitted = queryset.filter(status=ApplicationStatus.SUBMITTED).count()
        correction_requested = queryset.filter(status=ApplicationStatus.CORRECTION_REQUESTED).count()

        # Beneficiários com documentos faltando
        pending_docs = DashboardService._count_with_missing_docs(queryset)

        # Contagem por município
        by_municipality = queryset.values(
            'municipality__id', 'municipality__name', 'municipality__uf'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        return {
            'total': total,
            'draft': draft,
            'submitted': submitted,
            'under_review': under_review,
            'correction_requested': correction_requested,
            'approved': approved,
            'rejected': rejected,
            'pending_docs': pending_docs,
            'by_municipality': list(by_municipality),
        }

    @staticmethod
    def _count_with_missing_docs(queryset):
        """Conta beneficiários com documentos obrigatórios faltando"""
        required_types = DocumentType.objects.filter(required=True, active=True)
        count = 0

        for beneficiary in queryset.prefetch_related('documents'):
            uploaded_types = beneficiary.documents.values_list('document_type_id', flat=True)
            for doc_type in required_types:
                if doc_type.id not in uploaded_types:
                    count += 1
                    break

        return count

    @staticmethod
    def get_statistics_by_municipality(municipality_id=None):
        """Estatísticas por município"""
        queryset = Beneficiary.objects.all()

        if municipality_id:
            queryset = queryset.filter(municipality_id=municipality_id)

        return {
            'total': queryset.count(),
            'by_status': queryset.values('status').annotate(count=Count('id')),
            'with_cadunico': queryset.filter(has_cadunico=True).count(),
            'with_elderly': queryset.filter(has_elderly=True).count(),
            'with_children': queryset.filter(has_children=True).count(),
            'with_disability': queryset.filter(has_disability_or_tea=True).count(),
            'paying_rent': queryset.filter(pays_rent=True).count(),
            'no_own_house': queryset.filter(no_own_house=True).count(),
        }

    @staticmethod
    def get_user_assignments(user):
        """Retorna estatísticas de atribuições do usuário"""
        from habitacao.models import ApplicationAssignment

        active_assignments = ApplicationAssignment.objects.filter(
            assigned_to=user,
            active=True
        ).select_related('beneficiary')

        return {
            'active_count': active_assignments.count(),
            'by_status': active_assignments.values(
                'beneficiary__status'
            ).annotate(count=Count('id')),
            'assignments': active_assignments[:10]  # Últimas 10
        }
