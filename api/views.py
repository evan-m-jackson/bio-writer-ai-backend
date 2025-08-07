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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

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

class ProfileDataView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
            user_data = UsersSerializer(user).data
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        fields = UserFields.objects.filter(user=user)
        
        try:
            achievements = UserAchievements.objects.get(user=user)
            achievements_data = UserAchievementSerializer(achievements).data 
        except UserAchievements.DoesNotExist:
            achievements_data = {}

        try:
            bio = UserBio.objects.get(user=user)
            bio_data = UserBioSerializer(bio).data 
        except UserBio.DoesNotExist:
            bio_data = {}

        data = {
            'user': user_data,
            'fields': UserFieldsSerializer(fields, many=True).data,
            'achievements': achievements_data,
            'bio': bio_data,
        }

        return Response(data, status=status.HTTP_200_OK)

class AllProfileDataView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        users = Users.objects.all()
        profiles_data = []

        for user in users:
            # Get user fields
            fields = UserFields.objects.filter(user=user)
            fields_data = UserFieldsSerializer(fields, many=True).data
            
            # Get achievements (if exists)
            try:
                achievements = UserAchievements.objects.get(user=user)
                achievements_data = UserAchievementSerializer(achievements).data
            except UserAchievements.DoesNotExist:
                achievements_data = {}
            
            # Get bio (if exists)
            try:
                bio = UserBio.objects.get(user=user)
                bio_data = UserBioSerializer(bio).data
            except UserBio.DoesNotExist:
                bio_data = {}

            profile_data = {
                'user': UsersSerializer(user).data,
                'fields': fields_data,
                'achievements': achievements_data,
                'bio': bio_data,
            }
            profiles_data.append(profile_data)

        return Response(profiles_data, status=status.HTTP_200_OK)
