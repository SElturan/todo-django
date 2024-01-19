from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email=None, password=None, is_staff=False, is_superuser=False, **extra_fields):
        if not password:
            raise ValueError('User must have a password.')

        if not email:
            raise ValueError('User must have an email.')

        model_data = {'is_staff': is_staff, 'is_superuser': is_superuser}

        if email:
            model_data['email'] = self.normalize_email(email)


        user = self.create(**model_data, **extra_fields)
        user.set_password(password)  # Здесь пароль захеширован
        user.save(using=self._db)
        return user

    
    def create_superuser(self, email=None,  password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        user = self.create_user(email, password, **extra_fields)

     
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('Email адрес'), unique=True, db_index=True)
    phone = models.CharField(_('Номер телефона'), max_length=50, blank=True, db_index=True)
    is_staff = models.BooleanField(_('Сотрудник'), default=False)
    is_superuser = models.BooleanField(_('Суперпользователь'), default=False)
    is_active = models.BooleanField(_('Активен'), default=False)
    is_delete = models.BooleanField(_('Удален'), default=False)
    is_verified_email = models.BooleanField('Почта подтверждена', default=False)
    verification_code = models.CharField('Код подтверждения', max_length=6, blank=True, null=True)
    verification_code_created_at = models.DateTimeField('Дата создания кода подтверждения', blank=True, null=True)
    registered_at = models.DateTimeField(_('Дата регистрации'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.email:
            raise ValueError('User must have an email')
        # if self.pk is None:  # если это новый объект
        #     self.set_password(self.password)
        super(User, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if not self.is_superuser:
            self.is_delete = True
            self.save()
        else:
            self.delete()
            
    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.email
    
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'



class Post(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.content
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Friendship(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_users')
    freinds = models.ManyToManyField(User, related_name='friends')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.from_user} -> {self.to_user}'
    
    
    class Meta:
        verbose_name = 'Дружба'
        verbose_name_plural = 'Дружбы'