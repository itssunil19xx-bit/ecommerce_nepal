from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import logout
from django.utils.translation import gettext_lazy as _

# for viewsset

from rest_framework import viewsets
from rest_framework.decorators import action


from .models import User
from .serializers import *

from shared.permissions.permissions import IsOwnerOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action == ['update', 'partial-update', 'destroy']:
            permission_classes = [
                permissions.IsAuthenticated, IsOwnerOrReadOnly]

        elif self.action == ['list', 'rertrive']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return (permission() for permission in permission_classes)

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return User.objects.none()
        elif user.is_admin:
            return User.objects.all()
        else:
            return User.objects.filter(id=user.id)

    @action(detail='False', methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({'user': UserSerializer(user, context=self.get_serializer_context()).data,
                         'refresh': str(refresh),
                         'access': str(refresh.access_token),
                         'message': _('User registered successfully'),
                         }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        return Response({'user': UserSerializer(user, context=self.get_serializer_context()).data,
                         "refresh":  str(refresh),
                         'access': str(refresh.access_token),
                         "message": _("login sucessfully"),
                         })


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()

            logout(request)
            return Response({
                'message': _("logout successfully")
            }, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({
                "message": _("invalid Token")
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializzer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password": _("wrong password."),
                                 }, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.data.get("new_password"))
            user.save()

            return Response({"message": _("password updated successfully"),
                             }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetserializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({
            "message": _("password reset email has been sent")
        }, status=status.HTTP_200_OK)


class PasswordResetConformView(generics.GenericAPIView):
    serializer_class = PasswordResetConformSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({
            "message": _("password has been reset sucesssfully")
        }, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'id'
