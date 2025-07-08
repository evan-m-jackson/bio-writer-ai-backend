# api/tests.py
import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Users, FieldChoices, UserFields, UserAchievements, UserBio
from .serializers import (
    UsersSerializer, FieldChoicesSerializer, UserFieldsSerializer,
    UserAchievementSerializer, UserBioSerializer, ProfileDataSerializer,
    CustomTokenObtainPairSerializer
)

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_data():
    return {
        'email': 'test@example.com',
        'password': 'testpass123',
        'first_name': 'John',
        'last_name': 'Doe'
    }

@pytest.fixture
def create_user(user_data):
    return Users.objects.create_user(**user_data)

@pytest.fixture
def create_superuser():
    return Users.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )

@pytest.fixture
def field_choice():
    return FieldChoices.objects.create(field='Software Engineering')

@pytest.fixture
def authenticated_client(api_client, create_user):
    refresh = RefreshToken.for_user(create_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client

@pytest.fixture
def admin_client(api_client, create_superuser):
    refresh = RefreshToken.for_user(create_superuser)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client

class TestCustomUserManager:
    @pytest.mark.django_db
    def test_create_user_success(self, user_data):
        user = Users.objects.create_user(**user_data)
        assert user.email == user_data['email']
        assert user.first_name == user_data['first_name']
        assert user.last_name == user_data['last_name']
        assert user.check_password(user_data['password'])
        assert not user.is_staff
        assert not user.is_superuser

    @pytest.mark.django_db
    def test_create_user_without_email(self):
        with pytest.raises(ValueError, match='The Email field must be set'):
            Users.objects.create_user(email='', password='testpass123')

    @pytest.mark.django_db
    def test_create_superuser_success(self):
        user = Users.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        assert user.is_staff
        assert user.is_superuser

    @pytest.mark.django_db
    def test_create_superuser_without_staff_flag(self):
        with pytest.raises(ValueError, match='Superuser must have is_staff=True'):
            Users.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_staff=False
            )

    @pytest.mark.django_db
    def test_create_superuser_without_superuser_flag(self):
        with pytest.raises(ValueError, match='Superuser must have is_superuser=True'):
            Users.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_superuser=False
            )

class TestUsersModel:
    @pytest.mark.django_db
    def test_user_str_representation(self, create_user):
        assert str(create_user) == f"{create_user.first_name} {create_user.last_name}"

    @pytest.mark.django_db
    def test_email_uniqueness(self, user_data):
        Users.objects.create_user(**user_data)
        with pytest.raises(IntegrityError):
            Users.objects.create_user(**user_data)

    @pytest.mark.django_db
    def test_username_field_is_email(self):
        assert Users.USERNAME_FIELD == 'email'

    @pytest.mark.django_db
    def test_required_fields(self):
        assert Users.REQUIRED_FIELDS == ['first_name', 'last_name']

class TestFieldChoicesModel:
    @pytest.mark.django_db
    def test_field_choice_str_representation(self, field_choice):
        assert str(field_choice) == field_choice.field

    @pytest.mark.django_db
    def test_field_choice_primary_key(self, field_choice):
        assert field_choice.pk == field_choice.field

class TestUserFieldsModel:
    @pytest.mark.django_db
    def test_user_fields_creation(self, create_user, field_choice):
        user_field = UserFields.objects.create(
            user=create_user,
            order_num=1,
            field=field_choice,
            years=5
        )
        assert user_field.user == create_user
        assert user_field.order_num == 1
        assert user_field.field == field_choice
        assert user_field.years == 5

    @pytest.mark.django_db
    def test_unique_together_constraint(self, create_user, field_choice):
        UserFields.objects.create(
            user=create_user,
            order_num=1,
            field=field_choice,
            years=5
        )
        with pytest.raises(IntegrityError):
            UserFields.objects.create(
                user=create_user,
                order_num=1,
                field=field_choice,
                years=3
            )

class TestUserAchievementsModel:
    @pytest.mark.django_db
    def test_user_achievements_creation(self, create_user):
        achievement = UserAchievements.objects.create(
            user=create_user,
            achievements='Won coding competition'
        )
        assert achievement.user == create_user
        assert achievement.achievements == 'Won coding competition'

    @pytest.mark.django_db
    def test_user_achievements_str_representation(self, create_user):
        achievement = UserAchievements.objects.create(
            user=create_user,
            achievements='Won coding competition'
        )
        expected = f"{create_user.first_name}'s achievement: Won coding competition"
        assert str(achievement) == expected

class TestUserBioModel:
    @pytest.mark.django_db
    def test_user_bio_creation(self, create_user):
        bio = UserBio.objects.create(
            user=create_user,
            bio='Software developer with 5 years experience'
        )
        assert bio.user == create_user
        assert bio.bio == 'Software developer with 5 years experience'

    @pytest.mark.django_db
    def test_user_bio_str_representation(self, create_user):
        bio = UserBio.objects.create(
            user=create_user,
            bio='Software developer'
        )
        expected = f"{create_user.first_name}'s bio"
        assert str(bio) == expected

class TestUsersSerializer:
    @pytest.mark.django_db
    def test_users_serializer_valid_data(self, user_data):
        serializer = UsersSerializer(data=user_data)
        assert serializer.is_valid()

    @pytest.mark.django_db
    def test_users_serializer_invalid_email(self):
        data = {
            'email': 'invalid-email',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        serializer = UsersSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    @pytest.mark.django_db
    def test_users_serializer_returns_read_only_fields(self, user_data):
        serializer = UsersSerializer(data=user_data)
        assert serializer.data['created_at'] is not None
        assert serializer.data['modified_at'] is not None

class TestFieldChoicesSerializer:
    @pytest.mark.django_db
    def test_field_choices_serializer(self):
        data = {'field': 'Data Science'}
        serializer = FieldChoicesSerializer(data=data)
        assert serializer.is_valid()

class TestUserFieldsSerializer:
    @pytest.mark.django_db
    def test_user_fields_serializer(self, create_user, field_choice):
        data = {
            'user': create_user, 
            'order_num': 1, 
            'field': field_choice
        }
        serializer = UserFieldsSerializer(data=data)
        assert serializer.is_valid()

class TestUserAchievementsSerializer:
    @pytest.mark.django_db
    def test_user_achievements_serializer(self, create_user):
        data = {
            'user': create_user,
            'achievements': 'Won a number of awards'
        }
        serializer = UserAchievementSerializer(data=data)
        assert serializer.is_valid()

class TestUserBioSerializer:
    @pytest.mark.django_db
    def test_user_bio_serializer(self, create_user):
        data = {
            'user': create_user,
            'bio': 'User has been an award winning developer for 5 years'
        }
        serializer = UserBioSerializer(data=data)
        assert serializer.is_valid()

class TestProfileDataSerializer:
    @pytest.mark.django_db
    def test_profile_data_serializer(self, create_user, field_choice):
        user_fields_serializer = UserFieldsSerializer(data={
            'user': create_user,
            'order_num': 1,
            'field': field_choice
        })
        user_achievement_serializer = UserAchievementSerializer(data={
            'user': create_user,
            'achievements': 'Won a number of awards'
        })
        user_bio_serializer = UserBioSerializer(data={
            'user': create_user,
            'bio': 'User has been an award winning developer for 5 years'
        })
        data = {
            'fields': [user_fields_serializer.data],
            'achievement': user_achievement_serializer.data,
            'bio': user_bio_serializer.data
        }
        serializer = ProfileDataSerializer(data=data)
        assert serializer.is_valid()

class TestCustomerTokenObtainPairSerializer:
    @pytest.mark.django_db
    def test_custom_token_serializer(self, create_user):
        token = CustomTokenObtainPairSerializer.get_token(create_user)
        assert token['email'] == create_user.email
        assert token['first_name'] == create_user.first_name
        assert token['last_name'] == create_user.last_name

class TestRegisterView:
    @pytest.mark.django_db
    def test_register_success(self, api_client, user_data):
        response = api_client.post('/api/register/', user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Users.objects.filter(email=user_data['email']).exists()

    @pytest.mark.django_db
    def test_register_invalid_data(self, api_client):
        data = {'email': 'invalid-email'}
        response = api_client.post('/api/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_register_duplicate_email(self, api_client, user_data, create_user):
        response = api_client.post('/api/register/', user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

class TestUsersViewSet:
    @pytest.mark.django_db
    def test_list_users_authenticated(self, authenticated_client, create_user):
        response = authenticated_client.get('/api/users/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1  # User can only see their own profile

    @pytest.mark.django_db
    def test_list_users_admin(self, admin_client, create_user, create_superuser):
        response = admin_client.get('/api/users/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # Admin can see all users

    @pytest.mark.django_db
    def test_list_users_unauthenticated(self, api_client):
        response = api_client.get('/api/users/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestFieldChoicesViewSet:
    @pytest.mark.django_db
    def test_get_field_choices_when_authenticated(self, authenticated_client):
        FieldChoices.objects.create(field=field_choice)
        response = authenticated_client.get('/api/fields/')
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_get_field_choices_fails_when_not_authenticated(self, api_client):
        FieldChoices.objects.create(field=field_choice)
        response = api_client.get('/api/fields/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestUserFieldsViewSet:
    @pytest.mark.django_db
    def test_create_user_field(self, authenticated_client, create_user, field_choice):
        data = {
            'user': create_user.id,
            'order_num': 1,
            'field': field_choice.field,
            'years': 5
        }
        response = authenticated_client.post('/api/user-fields/', data)
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_list_user_fields_filtered(self, authenticated_client, create_user, field_choice):
        UserFields.objects.create(
            user=create_user,
            order_num=1,
            field=field_choice,
            years=5
        )
        response = authenticated_client.get('/api/user-fields/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    @pytest.mark.django_db
    def test_get_user_fields_when_user_is_authenticated(self, authenticated_client, create_user, field_choice):
        UserFields.objects.create(
            user=create_user,
            order_num=1,
            field=field_choice,
            years=5
        )
        url = f"/api/user-fields/{create_user.id}"
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_get_user_fields_fails_when_user_is_not_authenticated(self, api_client, create_user, field_choice):
        UserFields.objects.create(
            user=create_user,
            order_num=1,
            field=field_choice,
            years=5
        )
        url = f"/api/user-fields/{create_user.id}"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestUserAchievementsViewSet:
    @pytest.mark.django_db
    def test_create_user_achievements(self, authenticated_client, create_user):
        data = {
            'user': create_user.id,
            'achievements': 'Won a bunch of awards.'
        }
        response = authenticated_client.post('/api/achievements', data)
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_get_user_achievements_when_authenticated(self, authenticated_client, create_user):
        UserAchievements.objects.create(
            user=create_user,
            achievements='Won a bunch of awards.'
        )
        url = f"/api/achievements/{create_user.id}"
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_get_user_achievements_fails_when_not_authenticated(self, api_client, create_user):
        UserAchievements.objects.create(
            user=create_user,
            achievements='Won a bunch of awards.'
        )
        url = f"/api/achievements/{create_user.id}"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestUserBioViewSet:
    @pytest.mark.django_db
    def test_create_user_bio(self, authenticated_client, create_user):
        data = {
            'user': create_user.id,
            'bio': 'User has been an award winning developer for 5 years'
        }
        response = authenticated_client.post('/api/bios', data)
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_get_user_bio_when_authenticated(self, authenticated_client, create_user):
        UserBio.objects.create(
            user=create_user,
            bio='User has been an award winning developer for 5 years'
        )
        url = f"/api/bios/{create_user.id}"
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_get_user_bio_fails_when_not_authenticated(self, api_client, create_user):
        UserBio.objects.create(
            user=create_user,
            bio='User has been an award winning developer for 5 years'
        )
        url = f"/api/bios/{create_user.id}"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestProfileDataView:
    @pytest.mark.django_db
    def test_get_profile_data_success(self, api_client, create_user, field_choice):
        # Create test data
        UserFields.objects.create(
            user=create_user,
            order_num=1,
            field=field_choice,
            years=5
        )
        UserAchievements.objects.create(
            user=create_user,
            achievements='Test achievement'
        )
        UserBio.objects.create(
            user=create_user,
            bio='Test bio'
        )

        response = api_client.get(f'/profile-data/{create_user.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert 'fields' in response.data
        assert 'achievements' in response.data
        assert 'bio' in response.data
        assert len(response.data['fields']) == 1

    @pytest.mark.django_db
    def test_get_profile_data_user_not_found(self, api_client):
        response = api_client.get('/profile-data/999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'error' in response.data

    @pytest.mark.django_db
    def test_get_profile_data_no_achievements_or_bio(self, api_client, create_user):
        response = api_client.get(f"/profile-data/{create_user.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data['achievements'] == {}
        assert response.data['bio'] == {}
        assert response.data['fields'] == []

class TestDataIntegrity:
    @pytest.mark.django_db
    def test_cascade_delete_user_fields(self, create_user, field_choice):
        UserFields.objects.create(
            user=create_user,
            order_num=1,
            field=field_choice,
            years=5
        )
        user_id = create_user.id
        create_user.delete()
        assert not UserFields.objects.filter(user_id=user_id).exists()

    @pytest.mark.django_db
    def test_cascade_delete_user_achievements(self, create_user):
        UserAchievements.objects.create(
            user=create_user,
            achievements='Test achievement'
        )
        user_id = create_user.id
        create_user.delete()
        assert not UserAchievements.objects.filter(user_id=user_id).exists()

    @pytest.mark.django_db
    def test_cascade_delete_user_bio(self, create_user):
        UserBio.objects.create(
            user=create_user,
            bio='Test bio'
        )
        user_id = create_user.id
        create_user.delete()
        assert not UserBio.objects.filter(user_id=user_id).exists()