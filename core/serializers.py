from rest_framework import serializers
from .models import Estate, Block, Apartment, Amenity, Furnishing

class EstateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estate
        fields = '__all__'

class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = '__all__'

class ApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = '__all__'

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = '__all__'

class FurnishingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Furnishing
        fields = '__all__'