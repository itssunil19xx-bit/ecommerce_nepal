from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'date_of_birth', 'company_name',
            'pan_vat_number', 'seller_license',
            'facebook_url', 'twitter_url',
            'receive_marketing_emails', 'receive_sms_notifications'
        ]
        read_only_field = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True, required=True, style={
                                     'input_type': 'passwprd'})

    confirm_password = serializers.CharField(
        write_only=True, required=True, style={'input_typr': "password"})

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number',
            'role', 'province', 'district', 'municipality', 'ward_no',
            'is_email_verified', 'is_phone_verified',
            'password', 'confirm_password', 'profile',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_email_verified', 'is_phone_verified',
            'created_at', 'updated_at'
        ]

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError(
                {
                    'conform password': _("password do not match")
                }
            )

        if data.get('role') == 'seller' and not data.get('phone_number'):
            raise serializers.ValidationError(
                {
                    'phone_number': _("phone number is required for seller ")
                }
            )
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user)

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('confirm_password', None)
        for attr, value in validated_data.items():
            setattr(input, attr, value)

        if password:
            instance.set_password('password')

        instance.save()
        return instance


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_style': "password"},
                                     trim_whitespace=False
                                     )

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)
            if not user:
                raise serializers.ValidationError(_("unable to login with provided credentials"),
                                                  code="authorization")

            data['user'] = user
            return data
        else:
            raise serializers.ValidationError(
                _("must include email and password"), code="authorization")


class ChangePasswordSerializzer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({
                "confirm_new_password": _("password do not match")
            })
        return data


class PasswordResetserializer(serializers.Serializer):
    email = serializers.CharField(required=True)


class PasswordResetConformSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    uidb64 = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['comform_new_password']:
            raise serializers.ValidationError(
                {"confirm_new_password": _("password do not match")})

        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number',
                  'province', 'district', 'municipality', 'ward_no', 'profile']
        read_only_fields = ['id', 'email']

    def update(self, instance, **validated_data):
        profile_data = validated_data.pop('profile', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # to update profile

        if profile_data and hasattr(instance, 'profile'):
            profile = instance.profile
            profile_serializer = UserProfileSerializer(
                profile, data=profile_data, partial=True)

            if profile_serializer.is_valid():
                profile_serializer.save()
            else:
                raise serializers.ValidationError(
                    {'profile': profile_serializer.errors})

        return instance
