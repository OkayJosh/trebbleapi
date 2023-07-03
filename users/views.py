import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


LOG = logging.getLogger(__name__)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Remove the device from the user's logged_devices list
        device_name = request.headers.get("Device-Name")
        device_id = request.headers.get("Device-Id")
        device = request.user.logged_devices.filter(device_name=device_name, device_id=device_id).first()
        if device:
            device.delete()
            return Response({"message": "Device successfully logged out."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Device not found."}, status=status.HTTP_404_NOT_FOUND)
