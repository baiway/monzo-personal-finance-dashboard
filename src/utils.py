import random
import string

def gen_rand_str(length=16):
    """Generates a random string of letters and numbers to create an
    unguessable state token for use in authentication. This protects
    against cross-site request forgery attacks.
    See: https://docs.monzo.com/#acquire-an-access-token"""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
