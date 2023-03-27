from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'id', 'username',
                  'first_name', 'last_name', "password"]
        extra_kwargs = {'first_name': {'required': True},
                        'last_name': {'required': True},
                        'password': {'write_only': True},
                        'id': {'read_only': True}}

    # def get_queryset():
    #     pass

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
