from django.shortcuts import render
from drf_yasg import openapi
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from drf_yasg2.utils import swagger_auto_schema
from rest_framework import (exceptions, filters, generics, mixins, status,
                            viewsets)
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from .serializers import *
from django.template.loader import render_to_string
from random import randint
from django.contrib.auth import authenticate, login
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken

User = get_user_model()

def send_custom_email(email, subject, template_name, context):
    html_message = render_to_string(template_name, context)
    send_mail(
        subject,
        None,
        'kalmanbetovnurislam19@gmail.com', 
        [email],
        html_message=html_message,
        fail_silently=False,
    )
    print("Письмо отправлено")


class RegistrationAPIView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer  # Используйте свой сериализатор

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        if user is not None and not user.is_verified_email:
            verification_code = randint(10000, 99999)
            user.verification_code = verification_code
            user.verification_code_created_at = timezone.now()
            user.save()

            context = {
                'verification_code': verification_code,
            }

            send_custom_email(
                user.email,
                'Подтверждение регистрации',
                'email_template.html',
                context
            )

            return Response({
                "user": user.email,
                "role": user.role,
                "status": status.HTTP_200_OK
            })

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.filter(email=serializer.validated_data['email']).first()

            if user is not None and user.is_verified_email:
                return Response({"error": "Пользователь уже существует"}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create(
                email=serializer.validated_data['email'],
                role=serializer.validated_data['role'],
            )

            verification_code = randint(10000, 99999)
            user.verification_code = verification_code
            user.verification_code_created_at = timezone.now()
            user.save()

            context = {
                'verification_code': verification_code,
            }

            send_custom_email(
                user.email,
                'Подтверждение регистрации',
                'email_template.html',
                context
            )

            return Response({
                "user": user.email,
                "role": user.role,
                "status": status.HTTP_201_CREATED
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordAPIView(APIView):
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        if user is None:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        verification_code = randint(10000, 99999)
        user.verification_code = verification_code
        user.verification_code_created_at = timezone.now()
        user.save()
        context = {
            'verification_code': verification_code,
        }

        send_custom_email(
            user.email,
            'Сброс пароля',
            'password_reset_email.html',
            context
        )

        return Response({
            "user": user.email,
            "role": user.role,
            "status": status.HTTP_200_OK
        })

        
class VerifyEmailAPIView(APIView):
    serializer_class = VerifyEmailSerializer
    
    @swagger_auto_schema(request_body=VerifyEmailSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            verification_code = serializer.data['verification_code']
            user = User.objects.filter(email=email).first()
            if user is None:
                return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
            if user.verification_code != verification_code:
                return Response({"error": "Неверный код"}, status=status.HTTP_400_BAD_REQUEST)
            if user.verification_code_created_at + timezone.timedelta(minutes=5) < timezone.now():
                return Response({"error": "Код истек"}, status=status.HTTP_400_BAD_REQUEST)
            
            user.is_active = True
            
            user.verification_code = None
            user.save()
            return Response({
                "status": status.HTTP_200_OK,
                "user": user.email,
                "role": user.role

            })
        return Response(serializer.error, status=status.HTTP_404_NOT_FOUND)
    
        
class SetPasswordAPIView(APIView):
    serializer_class = SetPasswordSerializer

    @swagger_auto_schema(request_body=SetPasswordSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            email = serializer.data['email']
            password = serializer.data['password']
            password_confirm = serializer.data['password_confirm']
            user = User.objects.filter(email=email).first()
            if password != password_confirm:
                return Response({"error": "Пароли не совпадают"}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.filter(email=serializer.data['email']).first()
            if user is None:
                return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

            
            user.set_password(password)
            user.is_verified_email = True
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "status": status.HTTP_200_OK,
                "id": user.id,
                "user": user.email,
                "role": user.role,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        
        return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)



class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=email, password=password)
        if user:  
            if not user.is_verified_email:
                return Response({"error": "Почта не подтверждена"}, status=status.HTTP_400_BAD_REQUEST)
            
            refresh = RefreshToken.for_user(user)
            return Response({
                
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Неправильный Email или пароль"}, status=status.HTTP_401_UNAUTHORIZED)





class AccessTokenView(ObtainAuthToken):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user  
        return Response({
            "status": status.HTTP_200_OK,
            "id": user.id,
            "email": user.email, 
            "role": user.role,
        })


class UserProfileAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = request.user.id

        user_profile = UserProfile.objects.select_related('user').filter(user__id=user_id)
        serializer = UserProfileSerializer(user_profile, many=True, context={'request': request})
        return Response(serializer.data)
    
    @swagger_auto_schema(request_body=UserProfileSerializer)
    def post(self, request, *args, **kwargs):
        serializers = UserProfileSerializer(data=request.data)
        if serializers.is_valid():
            user = request.user
            serializers.save(user=user)
            return Response(serializers.data, status=status.HTTP_201_CREATED)
       
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(request_body=UserProfileSerializer)
    def patch(self, request, *args, **kwargs):
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
        serializers = UserProfileSerializer(user_profile, data=request.data, partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserProfilePrivate(ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('profile_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
    ])
    def get(self, request, *args, **kwargs):
        profile_id = self.request.query_params.get('profile_id')
        if not profile_id:
            return Response({"detail": "Profile ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset(profile_id=profile_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self, profile_id):
        return UserProfile.objects.filter(id=profile_id).select_related('user')
    
        

class PostCreateAPIView(CreateAPIView):
    serializer_class = PostSerializers
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializers = PostSerializers(data=request.data)
        if serializers.is_valid():
            #проверка заполнен ли у него профиль
            user = request.user
            user_profile = UserProfile.objects.filter(user=user).first()
            if not user_profile:
                return Response({"error": "Заполните профиль"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializers.save(author=request.user)
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class PostListAPIView(ListAPIView):
    serializer_class = PostSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        queryset = Post.objects.all().select_related('author')
        return queryset
    

class PostDetailListAPIView(ListAPIView):
    serializer_class = PostDetailSerializers
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('post_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
    ])
    def get(self, request, *args, **kwargs):
        post_id = self.request.query_params.get('post_id')
        if not post_id:
            return Response({"detail": "Post ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset(post_id=post_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self, post_id):
        return Post.objects.filter(id=post_id).select_related('author')
    


class CommentCreateAPIView(CreateAPIView):
    serializer_class = CommentSerializers
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializers = CommentSerializers(data=request.data)
        if serializers.is_valid():
            #проверка заполнен ли у него профиль
            user = request.user
            user_profile = UserProfile.objects.filter(user=user).first()
            if not user_profile:
                return Response({"error": "Заполните профиль"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializers.save(author=request.user)
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    

