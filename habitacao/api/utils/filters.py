"""
Filtros customizados
"""
import django_filters
from habitacao.models import Beneficiary
from habitacao.choices import ApplicationStatus


class BeneficiaryFilter(django_filters.FilterSet):
    """Filtros para beneficiários"""

    status = django_filters.ChoiceFilter(choices=ApplicationStatus.choices)
    municipality_id = django_filters.NumberFilter(field_name='municipality__id')
    uf = django_filters.CharFilter(field_name='uf', lookup_expr='iexact')
    cpf = django_filters.CharFilter(field_name='cpf', lookup_expr='icontains')
    protocol = django_filters.CharFilter(field_name='protocol_number', lookup_expr='icontains')
    has_cadunico = django_filters.BooleanFilter()
    has_elderly = django_filters.BooleanFilter()
    has_children = django_filters.BooleanFilter()
    has_disability_or_tea = django_filters.BooleanFilter()
    pays_rent = django_filters.BooleanFilter()
    no_own_house = django_filters.BooleanFilter()

    submitted_from = django_filters.DateTimeFilter(field_name='submitted_at', lookup_expr='gte')
    submitted_to = django_filters.DateTimeFilter(field_name='submitted_at', lookup_expr='lte')

    has_missing_docs = django_filters.BooleanFilter(method='filter_missing_docs')

    class Meta:
        model = Beneficiary
        fields = [
            'status', 'municipality_id', 'uf', 'cpf', 'protocol',
            'has_cadunico', 'has_elderly', 'has_children',
            'has_disability_or_tea', 'pays_rent', 'no_own_house',
            'submitted_from', 'submitted_to', 'has_missing_docs'
        ]

    def filter_missing_docs(self, queryset, name, value):
        """Filtra beneficiários com documentos obrigatórios faltando"""
        from habitacao.models import DocumentType

        if value:
            # Pega IDs de tipos obrigatórios
            required_types = DocumentType.objects.filter(required=True, active=True)

            # Filtra beneficiários que não têm todos os docs obrigatórios
            beneficiaries_with_missing = []
            for beneficiary in queryset:
                uploaded_types = beneficiary.documents.values_list('document_type_id', flat=True)
                for doc_type in required_types:
                    if doc_type.id not in uploaded_types:
                        beneficiaries_with_missing.append(beneficiary.id)
                        break

            return queryset.filter(id__in=beneficiaries_with_missing)

        return queryset
