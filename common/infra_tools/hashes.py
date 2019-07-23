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

    # Encode passwords and check if match
    match = bcrypt.checkpw(str.encode(input_pass), str.encode(hashed_pass))

    return match
