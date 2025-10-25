"""
Serializers da API
"""
from .base import (
    MunicipalitySerializer,
    PriorityCriteriaSerializer,
    SocialBenefitTypeSerializer,
    DocumentTypeSerializer,
)

from .user import (
    UserSerializer,
    UserProfileSerializer,
    RegisterSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
)

from .beneficiary import (
    BeneficiaryListSerializer,
    BeneficiaryDetailSerializer,
    BeneficiaryCreateSerializer,
    BeneficiaryUpdateSerializer,
    BeneficiaryPrioritySerializer,
    BeneficiarySocialBenefitSerializer,
    BeneficiaryDocumentSerializer,
    ApplicationActionHistorySerializer,
    WorkflowActionSerializer,
    AssignBeneficiarySerializer,
    AddPrioritySerializer,
    AddSocialBenefitSerializer,
)
