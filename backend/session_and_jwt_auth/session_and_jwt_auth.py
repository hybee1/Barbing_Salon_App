from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):

        print("CookieJWTAuthentication 1")
        header = self.get_header(request)

        print("CookieJWTAuthentication 2")
        if header is None:
            print("CookieJWTAuthentication 2a")
            raw_token = request.COOKIES.get("accessToken")
        else:
            print("CookieJWTAuthentication 2b")
            raw_token = self.get_raw_token(header)

        print("CookieJWTAuthentication 3")
        if raw_token is None:
            print("CookieJWTAuthentication 3a")
            return None

        print("CookieJWTAuthentication 4")
        print("raw_token = ", raw_token)
        validated_token = self.get_validated_token(raw_token)

        print("validated_token = ", validated_token)

        print("CookieJWTAuthentication 5")
        return self.get_user(validated_token), validated_token
