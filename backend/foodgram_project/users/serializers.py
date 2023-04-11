from django.contrib.auth import get_user_model
from rest_framework import serializers

# try:
# from api.serializers import RecipeMinifiedSerializer
# except ImportError:
#     raise ImportError('Can not import RecipeMinifiedSerializer from '
#                       'api.serializers module. Simply comment this '
#                       'import and "recipe" field in '
#                       'UserSubscribeSerilizer. '
#                       'Also you probably might comment '
#                       '"count recipe" field.')


User = get_user_model()


class UserManageSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username',
                  'first_name', 'last_name', "password",
                  'is_subscribed']
        extra_kwargs = {'first_name': {'required': True},
                        'last_name': {'required': True},
                        'password': {'write_only': True},
                        'id': {'read_only': True}}

    def get_is_subscribed(self, obj):
        request = self.context.get('request', None)
        print(self.context)
        if not request:
            return None
        user = request.user
        if not user.is_authenticated:
            return None
        if obj in user.follow.all():
            return True
        return False

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
