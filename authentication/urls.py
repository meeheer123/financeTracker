from .views import *
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register/', registration_view, name='register'),
    path('login/', login_view, name='login'),  # Corrected this line to use login_view
    path('logout/', logout_view, name='logout'),  # Corrected this line to use login_view
    path('validate-username/', csrf_exempt(username_validation_view), name='validate-username'),
    path('validate-email/', csrf_exempt(email_validation_view), name='validate-email'),
    path('activate/<uidb64>/<token>/', verification_view, name='activate'),  # Added trailing slash for consistency
    path('set-new-password/<uidb64>/<token>/', completePasswordReset, name='reset-user-password'),  # Added trailing slash for consistency
    path('request-reset-link/', RequestPasswordResetEmail, name='request-password'),  # Added trailing slash for consistency
    
]
