from rest_framework import generics, status
from rest_framework.response import Response
from .models import KeyValue
from .serializers import KeyValueSerializer
import requests
from django.conf import settings
from rest_framework.views import APIView

class KeyValueListCreateView(generics.ListCreateAPIView):
    queryset = KeyValue.objects.all()
    serializer_class = KeyValueSerializer

class KeyValueDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = KeyValue.objects.all()
    serializer_class = KeyValueSerializer
    lookup_field = 'key'


class KeyValueQuorumWrite(APIView):
    def post(self, request):
        key = request.data.get('key')
        value = request.data.get('value')
        data = {'key': key, 'value': value}
        success_count = 0

        for node in settings.CLUSTER_NODES:
            try:
                response = requests.post(f'{node}/kv/replica/', json=data)
                if response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
                    success_count += 1
            except requests.exceptions.RequestException:
                pass  # Handle node failure gracefully

        if success_count >= settings.QUORUM:
            return Response({'message': 'Write successful'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Write failed'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class KeyValueReplicaView(APIView):
    def post(self, request):
        serializer = KeyValueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, key):
        try:
            kv = KeyValue.objects.get(key=key)
            serializer = KeyValueSerializer(kv)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except KeyValue.DoesNotExist:
            return Response({'message': 'Key not found'}, status=status.HTTP_404_NOT_FOUND)


class KeyValueQuorumRead(APIView):
    def get(self, request, key):
        responses = []
        for node in settings.CLUSTER_NODES:
            try:
                response = requests.get(f'{node}/kv/replica/{key}/')
                if response.status_code == status.HTTP_200_OK:
                    responses.append(response.json())
            except requests.exceptions.RequestException:
                pass

        if len(responses) >= settings.QUORUM:
            # Simple conflict resolution: return the first response
            return Response(responses[0], status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Read failed'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)