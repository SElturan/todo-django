from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *
from .serializers import *

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email',)

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    verification_code = serializers.CharField(required=True, style={'input_type': 'verification_code'})


class SetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            password=validated_data['password'],
            )
        return user
    

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False, allow_null=False)
    password = serializers.CharField(required=True, allow_blank=False, allow_null=False)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        return data



class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'avatar', 
            'bio', 
            'birthday', 
            'city', 
            'country', 
            ]
        
    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.birthday = validated_data.get('birthday', instance.birthday)
        instance.city = validated_data.get('city', instance.city)
        instance.country = validated_data.get('country', instance.country)
        instance.save()
        return instance
        



class PostSerializers(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'id',
            'title', 
            'content', 
            'created_at', 
            ]
        

    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.author = validated_data.get('author', instance.author)
        instance.save()
        return instance
    

class CommentDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id',
            'post', 
            'author', 
            'content', 
            'created_at', 
            ]
        

    
class CommentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id',
            'post',  
            'content', 
            'created_at', 
            ]
        



class PostDetailSerializers(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = [
            'id',
            'title', 
            'content', 
            'created_at', 
            'comments',
            ]
        
    def get_comments(self, obj):
        comments = Comment.objects.filter(post=obj)
        serializer = CommentDetailSerializers(comments, many=True)
        return serializer.data
    

    
class FriendshipSerializers(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = [
            'id',
            'freinds', 
            'created_at', 
            ]
        

    
