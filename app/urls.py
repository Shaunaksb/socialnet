from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ExampleView, OtherView

urlpatterns = [
        path('register/', RegisterView.as_view(), name='register'),
        path('login/', LoginView.as_view(), name='login'),
        path('logout/', LogoutView.as_view(), name='logout'),
        path('example/', ExampleView.as_view(), name='example'),
        path('other/', OtherView.as_view(), name='other'),
]