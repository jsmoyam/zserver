import jwt
from datetime import datetime, timedelta

secret_key = '12345'
token_expiration = 3600


def generate_token(id_user: int):
    # Create token with user_id and secret_key
    exp_date = datetime.now() + timedelta(0, token_expiration)
    token_bytes = jwt.encode({'id': id_user, 'exp': exp_date}, secret_key, algorithm='HS256')
    token_decode = token_bytes.decode('utf-8')

    return token_decode


def get_user_id_from_token(token_user: str) -> int:
    # Recover user_id from token
    try:
        payload = jwt.decode(token_user, secret_key, algorithms='HS256')
        return payload
    except Exception as e:
        print("ERROR: {}".format(e))


token = generate_token(1)

print(token)

user_id = get_user_id_from_token(token)

print(user_id)
