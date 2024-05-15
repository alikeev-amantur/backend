from rest_framework import serializers


class SerializerRepresentationService(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = instance.user.email
        return representation
