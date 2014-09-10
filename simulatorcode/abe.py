'''
Created on Jul 29, 2014

@author: parallels
'''




from charm.toolbox.pairinggroup import PairingGroup,GT
from charm.schemes.ibenc.ibenc_sw05 import IBE_SW05

from charm.toolbox.pairinggroup import G1,G2,pair,ZR
import charm.toolbox.pairingcurves

group = PairingGroup('SS512')
g = group.random(G1)
g2 = group.random(G2)
y = group.random(ZR)
Y = pair(g, g) ** y

required_overlap = 1 # the number of attributes required for decryption
max_attributes = 3 # the maximum number of attributes 
ibe = IBE_SW05(group)
(master_public_key, master_key) = ibe.setup(max_attributes, required_overlap)
private_identity = ['id1', 'id2', 'id3',] # set of all the possible identities (it should be time- and beacon-id-dependent strings for our case)
identity_set_for_encryption = ['id1', 'id2', ] # set of identities that are used for encryption
(pub_ID_hashed, secret_key) = ibe.extract(master_key, private_identity, master_public_key, required_overlap, max_attributes) # all the possible (id, key) pairs
msg = group.random(GT)
cipher_text = ibe.encrypt(master_public_key, identity_set_for_encryption, msg, max_attributes)

# virtually creating a set of keys that the client owns
del secret_key['D'][pub_ID_hashed[0]] 
pub_ID_hashed.pop(0) 

decrypted_msg = ibe.decrypt(master_public_key, secret_key, cipher_text, pub_ID_hashed, required_overlap)

print msg
print cipher_text
print decrypted_msg

print msg == decrypted_msg
