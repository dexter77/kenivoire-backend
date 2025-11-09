from rest_framework import serializers
from .models import Ad, Categorie
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'city')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'name', 'icon']

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'city']

class AdSerializer(serializers.ModelSerializer):
    owner = UserSimpleSerializer(read_only=True)
    categorie = CategorySerializer(read_only=True)
    categorie_id = serializers.PrimaryKeyRelatedField(
        queryset=Categorie.objects.all(),
        source='categorie',
        write_only=True
    )
    class Meta:
        model = Ad
        fields = '__all__'
        read_only_fields = ('owner', 'created_at')
