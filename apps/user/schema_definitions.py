from drf_spectacular.utils import OpenApiExample, extend_schema_serializer

user_serializer_schema = extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Client User Registration",
            description="Successful Client Registration",
            value={
                "id": 1,
                "email": "customer@mail.com",
                "name": "Customer Name",
                "date_of_birth": "2024-04-30",
                "avatar": "null",
                "tokens": {
                    "refresh": "supersecretrefreshtoken",
                    "access": "supersecretaccesstoken"
                }
            },
            response_only=True
        ),
        OpenApiExample(
            name="Client User Registration",
            description="Failed Client Registration (email duplicate)",
            value={
                "email": [
                    "This field must be unique."
                ]
            },
            response_only=True
        ),
        OpenApiExample(
            name="Client User Login",
            description="Successful Client Login",
            value={
                "refresh": "supersecretrefreshtoken",
                "access": "supersecretaccesstoken",
                "id": 1,
                "email": "customer@mail.com",
                "name": "null",
                "role": "client",
                "max_establishments": 1
            },
            request_only=True
        ),
        OpenApiExample(
            name="Partner User Login",
            description="Successful Partner Login",
            value={
                "refresh": "supersecretrefreshtoken",
                "access": "supersecretaccesstoken",
                "id": 1,
                "email": "partner@mail.com",
                "name": "null",
                "role": "partner",
                "max_establishments": 1
            },
            request_only=True
        ),
        OpenApiExample(
            name="Client/Partner User Token Refresh",
            description="Successful Client/Partner Login",
            value={
                "refresh": "supersecretrefreshtoken",
                "access": "supersecretaccesstoken",
            },
            request_only=True
        ),
        OpenApiExample(
            name="Client/Partner User Token Refresh",
            description="Failed Client/Partner Login",
            value={
                "detail": "Token is invalid or expired",
                "code": "token_not_valid"
            },
            request_only=True
        ),
        OpenApiExample(
            name="Client/Partner User Login",
            description="Failed Client/Partner Login",
            value={
                "detail": "No active account found with the given credentials"
            },
            request_only=True
        ),
        OpenApiExample(
            name="Client/Partner User Login",
            description="Failed Client/Partner Login (blocked)",
            value={
                "non_field_errors": [
                    "busta straight busta"
                ]
            },
            request_only=True
        ),
        OpenApiExample(
            name="Client/Partner Logout",
            description="Successful Client/Partner Logout",
            value={
            },
            request_only=True
        ),
        OpenApiExample(
            name="Client/Partner Logout",
            description="Failed Client/Partner Logout",
            value={
                "detail": "Token is invalid or expired",
                "code": "token_not_valid"
            },
            request_only=True
        ),
        OpenApiExample(
            name="Client Profile Retrieve",
            description="Successful Client Profile Retrieve",
            value={
                "id": 1,
                "email": "customer@mail.com",
                "name": "null",
                "role": "client",
                "max_establishments": 1
            },
            request_only=True
        ),
        OpenApiExample(
            name="Client Profile Update",
            description="Successful Client Profile Update",
            value={
                "id": 1,
                "email": "customer@mail.com",
                "name": "null",
                "role": "client",
                "max_establishments": 1
            },
            request_only=True
        ),
        OpenApiExample(
            name="Client Logout Delete",
            description="Successful Client Profile Delete",
            value={
            },
            request_only=True
        ),
        OpenApiExample(
            name="User Password Forgot",
            description="Successful User Password Forgot",
            value={
                "Success"
            },
            request_only=True
        ),
        OpenApiExample(
            name="User Password Forgot",
            description="Failed User Password Forgot",
            value={
                "non_field_errors": [
                    "User does not exists"
                ]
            },
            request_only=True
        ),
        OpenApiExample(
            name="User Password Reset",
            description="Successful User Password Reset",
            value={
                "Success"
            },
            request_only=True
        ),
        OpenApiExample(
            name="User Password Reset",
            description="Failed User Password Reset",
            value={
                "non_field_errors": [
                    "User does not exists"
                ]
            },
            request_only=True
        ),
        OpenApiExample(
            name="User Password Change",
            description="Success User Password Change",
            value={
                "Password successfully changed"
            },
            request_only=True
        ),
        OpenApiExample(
            name="User Password Change",
            description="Failed User Password Change",
            value={
                "non_field_errors": [
                    "Passwords do not match"
                ]
            },
            request_only=True
        ),
        OpenApiExample(
            name="Client List",
            description="Successful Client List",
            value={
                "count": 1,
                "next": "http://api.example.org/accounts/?offset=400&limit=100",
                "previous": "http://api.example.org/accounts/?offset=200&limit=100",
                "results": [
                    {
                        "id": 1,
                        "email": "customer@example.com",
                        "name": "Customer Name",
                        "date_of_birth": "2024-04-30",
                        "avatar": "http://api.example.com/media/client_avatars/customer_photo.jpg",
                        "is_blocked": "false"
                    }
                ]
            },
            request_only=True
        ),
        OpenApiExample(
            name="Client List",
            description="Failed Client List",
            value={
                "detail": "Authentication credentials were not provided."
            },
            request_only=True
        ),
        OpenApiExample(
            name="Partner Create",
            description="Successful Partner Create",
            value={
                "id": 1,
                "email": "partner@example.com",
                "name": "Partner",
                "max_establishments": 3
            },
            request_only=True
        ),
        OpenApiExample(
            name="Partner Create",
            description="Failed Partner Create",
            value={
                "detail": "Authentication credentials were not provided."
            },
            request_only=True
        ),
        OpenApiExample(
            name="Partner List",
            description="Successful Partner List",
            value={
                "count": 1,
                "next": "http://api.example.org/accounts/?offset=400&limit=100",
                "previous": "http://api.example.org/accounts/?offset=200&limit=100",
                "results": [
                    {
                        "id": 0,
                        "email": "partner@example.com",
                        "name": "Partner",
                        "max_establishments": 3,
                        "is_blocked": "false"
                    }
                ]
            },
            request_only=True
        ),
        OpenApiExample(
            name="Partner List",
            description="Failed Partner List",
            value={
                "detail": "Authentication credentials were not provided."
            },
            request_only=True
        ),
        OpenApiExample(
            name="Admin Login",
            description="Successful Admin Login",
            value={
                "refresh": "supersecretrefreshtoken",
                "access": "supersecretaccesstoken",
                "id": 1,
                "email": "admin@mail.com"
            },
            request_only=True
        ),
        OpenApiExample(
            name="Admin Login",
            description="Failed Admin Login",
            value={
                "non_field_errors": [
                    "Not admin user"
                ]
            },
            request_only=True
        ),
        OpenApiExample(
            name="Admin Block User",
            description="Failed Admin Block User",
            value={
                "non_field_errors": [
                    "User does not exists"
                ]
            },
            request_only=True
        ),
        OpenApiExample(
            name="Admin Block User",
            description="Successful Admin Block User",
            value={
                "Successful"
            },
            request_only=True
        ),
    ]
)
