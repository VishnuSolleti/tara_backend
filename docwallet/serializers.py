from rest_framework import serializers
from .models import DocWallet, Folder, Document
from usermanagement.models import Context


class DocWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocWallet
        fields = ['id', 'context', 'created_at']


class FolderSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Folder.objects.all(), required=False)

    class Meta:
        model = Folder
        fields = ['id', 'name', 'wallet', 'parent', 'created_at']


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'name', 'file', 'folder', 'uploaded_at']
