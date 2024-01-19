from django.urls import path, include
from .views import *

urlpatterns = [
    path('signup/', RegistrationAPIView.as_view(), name='signup'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
    path('verify-email/', VerifyEmailAPIView.as_view(), name='verify-email'),
    path('set-password/', SetPasswordAPIView.as_view(), name='set-password'),
    path('resend-password-confirm/', ResetPasswordAPIView.as_view(), name='ResetPasswordConfirm'),
    path('signin/', UserLoginView.as_view(), name='signin'),
    path('token/', AccessTokenView.as_view(), name='token_refresh'),

    path('profile/', UserProfileAPIView.as_view(), name='profile'),
    path('profile-private/', UserProfilePrivate.as_view(), name='profile'),

    path('posts-create/', PostCreateAPIView.as_view(), name='posts'),
    path('posts-list/', PostListAPIView.as_view(), name='posts'),
    path('posts-detail/', PostDetailListAPIView.as_view(), name='posts'),

    path('comments-create/', CommentCreateAPIView.as_view(), name='comments'),
    
    

]