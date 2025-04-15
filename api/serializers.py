from rest_framework import serializers
from .models import Users, FieldChoices, UserFields, UserAchievements, UserBio

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'first_name', 'last_name', 'email', 'created_at', 'modified_at']
        read_only_fields = ['created_at', 'modified_at']

class FieldChoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldChoices
        fields = ['field']

class UserFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFields
        fields = ['id', 'user', 'order_num', 'field', 'years']

class UserAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAchievements
        fields = ['id', 'user', 'achievements']

class UserBioSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBio
        fields = ['id', 'user', 'bio']