from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.utils import timezone
from datetime import timedelta
from .models import LoginAttempt, BlacklistedToken
from .utils import get_client_ip, is_ip_logged_in, set_ip_logged_in, clear_ip_logged_in

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ip = get_client_ip(request)
        if is_ip_logged_in(ip):
            return Response({"error": "You are already logged in"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            set_ip_logged_in(ip)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ip = get_client_ip(request)
        if is_ip_logged_in(ip):
            return Response({"error": "You are already logged in"}, status=status.HTTP_403_FORBIDDEN)
        username = request.data.get('username')
        password = request.data.get('password')
        ip_address = request.META.get('REMOTE_ADDR')
        
        if not username:
            LoginAttempt.objects.create(
                ip_address=ip_address,
                success=False
            )
            return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(username=username).first()
        
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            LoginAttempt.objects.create(
                user=user,
                username=username,
                ip_address=ip_address,
                success=True
            )
            set_ip_logged_in(ip)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            LoginAttempt.objects.create(
                username=username,
                ip_address=ip_address,
                success=False
            )
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                token = RefreshToken(refresh_token)
            except TokenError:
                return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if token is already blacklisted
            jti = token.payload['jti']
            token_obj = OutstandingToken.objects.filter(token=str(refresh_token)).first()
            
            if not token_obj:
                return Response({"error": "Token not found"}, status=status.HTTP_404_NOT_FOUND)

            if BlacklistedToken.objects.filter(token=token_obj).exists():
                return Response({"error": "Token is already blacklisted"}, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the token
            BlacklistedToken.objects.create(token=token_obj)
            
            ip = get_client_ip(request)
            clear_ip_logged_in(ip)

            return Response({"success": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ExampleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is a protected example endpoint"})
    
class OtherView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "This is an unprotected example endpoint"})