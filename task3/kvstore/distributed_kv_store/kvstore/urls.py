from django.urls import path
from .views import KeyValueListCreateView, KeyValueDetailView, KeyValueQuorumRead
from .views import KeyValueQuorumWrite, KeyValueReplicaView

urlpatterns = [
    path('kv/', KeyValueQuorumWrite.as_view(), name='kv_quorum_write'),
    path('kv/replica/', KeyValueReplicaView.as_view(), name='kv_replica_write'),
    path('kv/replica/<str:key>/', KeyValueReplicaView.as_view(), name='kv_replica_read'),
    path('kv/<str:key>/', KeyValueQuorumRead.as_view(), name='kv_quorum_read'),
]