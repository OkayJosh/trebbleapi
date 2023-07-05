from copy import copy

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from contentgen.serializers import ContentGeneratorSerializer
from contentgen.templates import OpenAIPromptEngine, PromptTemplate
from trebbleapi.throttles import CustomThrottle


class ContentGeneratorView(CustomThrottle, APIView):
    serializer_class = ContentGeneratorSerializer
    template = PromptTemplate
    engine = OpenAIPromptEngine
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': self.request})
        if serializer.is_valid():
            data = copy(serializer.validated_data)
            data.pop('number')
            template = self.template(**data)
            engine = self.engine(template=template)
            return Response(engine.stream(), status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)