from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, Post, Comment, Friendship

class UserAdmin(BaseUserAdmin):
    # fields = ['email', 'phone', 'whatsapp_phone', 'password','is_staff','is_employer', 'is_student', 'is_delete', 'is_active', 'is_superuser', ]
    fieldsets = (
        (None, {'fields': ('email', 'phone', 'verification_code','is_verified_email', 'password' 'is_delete',)}),
        (('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser','user_permissions')}),
        (('Important dates'), {'fields': ('last_login',)}),
            )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1','password2', 'is_delete', 'is_active', 'is_superuser', ),
        }),
    )
    list_display = ['id','email','verification_code', 'phone',  'is_staff', 'is_delete', 'is_active', 'is_superuser', ]
    search_fields = ['email', 'phone',  ]
    list_editable = ['is_staff', 'is_delete', 'is_active', 'is_superuser',]
    ordering = ('id',)
    filter_horizontal = ('groups', 'user_permissions')


    class Meta:
        model = User


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'avatar', 'bio', 'birthday', 'city', 'country', )
    list_display_links = ('id','user', )
    search_fields = ('user__email', )


class PostAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'content', 'author', 'created_at', )
    list_display_links = ('id','title', )
    search_fields = ('title', 'content', 'author__email', )

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','post', 'author', 'content', 'created_at', )
    list_display_links = ('id','post', )
    search_fields = ('post__title', 'author__email', )

class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('id','from_user', 'created_at', )
    list_display_links = ('id','from_user', )
    search_fields = ('from_user__email', )
    filter_horizontal = ('freinds', )

admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Friendship, FriendshipAdmin)

