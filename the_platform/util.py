def gen_secret_key():
    import os
    from base64 import b64encode

    random_bits = os.urandom(128)
    random_encoded = b64encode(random_bits)

    return random_encoded
