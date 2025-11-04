"""
Serializers para usuários e autenticação
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from habitacao.models import UserProfile
from habitacao.choices import UserRole
from .base import MunicipalitySerializer


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil de usuário"""
    municipality_data = MunicipalitySerializer(source='municipality', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'cpf', 'role', 'role_display',
            'municipality', 'municipality_data',
            'is_active', 'created_at', 'last_login'
        ]
        read_only_fields = ['created_at', 'last_login']


class UserSerializer(serializers.ModelSerializer):
    """Serializer para usuário Django"""
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)  # <-- Adiciona campo

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name',
            'last_name', 'full_name', 'profile', 'is_superuser'  # <-- Inclui campo
        ]
        read_only_fields = ['id', 'username']


class RegisterSerializer(serializers.Serializer):
    """Serializer para registro de novo usuário"""
    full_name = serializers.CharField(max_length=160, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    cpf = serializers.CharField(max_length=14, required=False, allow_blank=True, default='')
    role = serializers.ChoiceField(choices=UserRole.choices, required=False, default='OPERATOR')
    municipality_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_email(self, value):
        """Valida se o email já existe"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        return value

    def validate_cpf(self, value):
        """Valida se o CPF já existe"""
        # Permitir CPF vazio (pre-cadastro)
        if value and UserProfile.objects.filter(cpf=value).exists():
            raise serializers.ValidationError("Este CPF já está cadastrado.")
        return value

    def create(self, validated_data):
        """Cria usuário e perfil"""
        import uuid

        # Separa dados
        full_name = validated_data.pop('full_name')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        cpf = validated_data.pop('cpf', '')
        role = validated_data.pop('role', 'OPERATOR')
        municipality_id = validated_data.pop('municipality_id', None)

        # Se CPF vazio, gerar um temporario usando parte do UUID
        if not cpf:
            # Gerar CPF temporario unico (formato: TEMP-XXXXX)
            temp_id = str(uuid.uuid4())[:8].upper()
            cpf = f'TEMP-{temp_id}'

        # Divide nome
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Cria usuário Django
        user = User.objects.create_user(
            username=email,  # Usa email como username
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        # Cria perfil
        profile = UserProfile.objects.create(
            user=user,
            cpf=cpf,
            role=role,
            municipality_id=municipality_id
        )

        return user


class LoginSerializer(serializers.Serializer):
    """Serializer para login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer para mudança de senha"""
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
