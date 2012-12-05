from binascii import hexlify
import json
import M2Crypto
from jwkest import jwe
from jwkest.jwk import dumps
from jwkest.jwk import kspec_rsa
from jwkest.jwk import kspec
from jwkest.jwk import loads
from jwkest.jwk import base64_to_long
from jwkest.jwk import long_to_mpi
from jwkest.jwk import x509_rsa_loads
from jwkest.jwk import rsa_load
from jwkest.jwk import rsa_loads
from jwkest.jwk import dump_jwk

__author__ = 'rohe0002'

CERT = "certs/cert.pem"
KEY = "certs/server.key"

JWK = {"keys":[{'alg': 'RSA',
                'use': 'foo',
                'xpo': 'AQAB',
                'mod': 'wf-wiusGhA-gleZYQAOPQlNUIucPiqXdPVyieDqQbXXOPBe3nuggtVzeq7pVFH1dZz4dY2Q2LA5DaegvP8kRvoSB_87ds3dy3Rfym_GUSc5B0l1TgEobcyaep8jguRoHto6GWHfCfKqoUYZq4N8vh4LLMQwLR6zi6Jtu82nB5k8'}]}

def _eq(l1, l2):
    return set(l1) == set(l2)

def test_x509_rsa_loads():
    _ckey = x509_rsa_loads(open(CERT).read())
    assert isinstance(_ckey, M2Crypto.RSA.RSA_pub)

def test_x509_rsa_loads_2():
    _ckey = x509_rsa_loads(open(CERT).read())
    _jwk = kspec_rsa(_ckey)

    print _jwk
    e = base64_to_long(_jwk["xpo"])
    n = base64_to_long(_jwk["mod"])

    _jkey = M2Crypto.RSA.new_pub_key((long_to_mpi(e), long_to_mpi(n)))

    cn = jwe.hd2ia(hexlify(_ckey.n))
    jn = jwe.hd2ia(hexlify(_jkey.n))

    assert cn == jn

def test_kspec():
    _ckey = x509_rsa_loads(open(CERT).read())
    _jwk = kspec(_ckey)
    print _jwk
    assert _jwk["alg"] == "RSA"
    assert _jwk["xpo"] == JWK["keys"][0]["xpo"]
    assert _jwk["mod"] == JWK["keys"][0]["mod"]

def test_loads_0():

    keys = loads(json.dumps(JWK))
    assert len(keys) == 1
    (type,key) = keys[0]
    assert type == "rsa"

    _ckey = x509_rsa_loads(open(CERT).read())

    print key
    assert key.n == _ckey.n
    assert key.e == _ckey.e

def test_loads_1():
    JWK = {"keys":[{'alg': 'RSA',
                    'use': 'foo',
                    'xpo': 'AQAB',
                    'mod': 'wf-wiusGhA-gleZYQAOPQlNUIucPiqXdPVyieDqQbXXOPBe3nuggtVzeq7pVFH1dZz4dY2Q2LA5DaegvP8kRvoSB_87ds3dy3Rfym_GUSc5B0l1TgEobcyaep8jguRoHto6GWHfCfKqoUYZq4N8vh4LLMQwLR6zi6Jtu82nB5k8',
                    'kid': "1"},
                   {'alg': 'RSA',
                    'use': 'bar',
                    'xpo': 'AQAB',
                    'mod': 'wf-wiusGhA-gleZYQAOPQlNUIucPiqXdPVyieDqQbXXOPBe3nuggtVzeq7pVFH1dZz4dY2Q2LA5DaegvP8kRvoSB_87ds3dy3Rfym_GUSc5B0l1TgEobcyaep8jguRoHto6GWHfCfKqoUYZq4N8vh4LLMQwLR6zi6Jtu82nB5k8',
                    'kid': "2"}
                   ]}

    keys = loads(json.dumps(JWK))
    print keys
    assert len(keys) == 2
    key_ids = [id for id,key in keys]
    assert _eq(key_ids, ["rsa:1", "rsa:2"])

def test_dumps():
    _ckey = x509_rsa_loads(open(CERT).read())
    jwk = dumps(_ckey)
    assert _eq(jwk.keys(), ["alg", "xpo", "mod"])

def test_dump_jwk():
    _ckey = x509_rsa_loads(open(CERT).read())
    jwk = dump_jwk([{"key":_ckey}])
    print jwk
    _wk = json.loads(jwk)
    assert _wk.keys() == ["keys"]
    assert len(_wk["keys"]) == 1
    assert _eq(_wk["keys"][0].keys(), ["alg", "xpo", "mod"])

def test_load_jwk():
    _ckey = x509_rsa_loads(open(CERT).read())
    jwk = dump_jwk([{"key":_ckey}])
    wk = loads(jwk)
    print wk
    assert len(wk) == 1
    (typ, key) = wk[0]
    assert typ == "rsa"
    assert isinstance(key, M2Crypto.RSA.RSA)

def test_rsa_load():
    _ckey = rsa_load(KEY)
    assert isinstance(_ckey, M2Crypto.RSA.RSA)
    jwk = dumps(_ckey)
    print jwk
    assert _eq(jwk.keys(), ["alg", "xpo", "mod"])
    assert jwk["mod"] == '5zbNbHIYIkGGJ3RGdRKkYmF4gOorv5eDuUKTVtuu3VvxrpOWvwnFV-NY0LgqkQSMMyVzodJE3SUuwQTUHPXXY5784vnkFqzPRx6bHgPxKz7XfwQjEBTafQTMmOeYI8wFIOIHY5i0RWR-gxDbh_D5TXuUqScOOqR47vSpIbUH-nc'
    assert jwk['xpo'] == 'AQAB'

def test_rsa_loads():
    _ckey = rsa_loads(open(KEY).read())
    assert isinstance(_ckey, M2Crypto.RSA.RSA)
    jwk = dumps(_ckey)
    print jwk
    assert _eq(jwk.keys(), ["alg", "xpo", "mod"])
    assert jwk["mod"] == '5zbNbHIYIkGGJ3RGdRKkYmF4gOorv5eDuUKTVtuu3VvxrpOWvwnFV-NY0LgqkQSMMyVzodJE3SUuwQTUHPXXY5784vnkFqzPRx6bHgPxKz7XfwQjEBTafQTMmOeYI8wFIOIHY5i0RWR-gxDbh_D5TXuUqScOOqR47vSpIbUH-nc'
    assert jwk['xpo'] == 'AQAB'
