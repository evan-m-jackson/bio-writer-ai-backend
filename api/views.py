from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Users, FieldChoices, UserFields, UserAchievements, UserBio
from .serializers import (
    UsersSerializer,
    FieldChoicesSerializer,
    UserFieldsSerializer,
    UserAchievementSerializer,
    UserBioSerializer
)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UsersSerializer(data=request.data)
        if serializer.is_valid():
            user = Users.objects.create_user(
                email=serializer.validated_data['email'],
                password=request.data['password'],
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name']
            )
            return Response(UsersSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # For security, users can only see their own profile
        if not self.request.user.is_staff:
            return Users.objects.filter(id=self.request.user.id)
        return Users.objects.all()

class FieldChoicesViewSet(viewsets.ModelViewSet):
    queryset = FieldChoices.objects.all()
    serializer_class = FieldChoicesSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserFieldsViewSet(viewsets.ModelViewSet):
    queryset = UserFields.objects.all()
    serializer_class = UserFieldsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own fields
        if not self.request.user.is_staff:
            return UserFields.objects.filter(user_id=self.request.user.id)
        return UserFields.objects.all()

class UserAchievementsViewSet(viewsets.ModelViewSet):
    queryset = UserAchievements.objects.all()
    serializer_class = UserAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own achievements
        if not self.request.user.is_staff:
            return UserAchievements.objects.filter(user_id=self.request.user.id)
        return UserAchievements.objects.all()

class UserBioViewSet(viewsets.ModelViewSet):
    queryset = UserBio.objects.all()
    serializer_class = UserBioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own bio
        if not self.request.user.is_staff:
            return UserBio.objects.filter(user_id=self.request.user.id)
        return UserBio.objects.all()
