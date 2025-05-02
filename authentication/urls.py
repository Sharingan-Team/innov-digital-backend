from django.urls import path
from .views import SignupView, LoginView, VerifyEmailCodeView, FaceVerificationView, FaceEnrollmentView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-email/', VerifyEmailCodeView.as_view(), name='verify_email'),
    path('verify-face/', FaceVerificationView.as_view(), name='verify_face'),
    path('enroll-face/', FaceEnrollmentView.as_view(), name='enroll_face'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
