import bcrypt


def hash_password(password) -> str:
    """
    Generate the hash from the password and return it

    :param password: Password to encrypt

    :return: Password encrypted
    :rtype: str
    """

    # Encode password and hash
    hashed = bcrypt.hashpw(str.encode(password), bcrypt.gensalt(13))

    return hashed


def check_password_hashed(input_pass, hashed_pass) -> bool:
    """
    Check that a unhashed password matches one that has previously been hashed

    :param input_pass: unhashed password
    :param hashed_pass: password

    :return: True if match
    :rtype: bool
    """

    # Check if this match
    match = bcrypt.checkpw(str.encode(input_pass), hashed_pass)

    return match


print('Input a password: ')
input_password = input()

hashed_password = hash_password(input_password)
match_password = check_password_hashed(input_password, hashed_password)

print('Password: {}.\nHashed password: {}'.format(input_password, hashed_password))
print('Password 1: {}'.format(match_password))

print('Input other password: ')
bad_password = input()

match_bad = check_password_hashed(bad_password, hashed_password)

print('Password 2: {}'.format(match_bad))
