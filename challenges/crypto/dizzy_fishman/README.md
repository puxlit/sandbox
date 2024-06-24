# [crypto] dizzy_fishman

<table><tbody>
<tr><th>Value</th><td>896 pts</td></tr>
<tr><th>Tags</th><td><code>hard</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
<tr><th>Connection info</th><td><code>nc chals.jellyc.tf 4000</code></td></tr>
<tr><th>Files</th><td><a href="./files/dizzy_fishman.zip">dizzy_fishman.zip</a></td></tr>
</tbody></table>

Sakana is sending some suspicious looking messages to Dizzy - looks like they're exchanging a shared secret key to encrypt the messages.

Alice has hacked into their key exchange system but needs more help with the exploit. Can you find a way to reveal their secret key and decrypt the message?

10 point hint: Algorithm/Area to focus on \
20 point hint: Example that could work if it wasn't validated by the challenge

---

raw notes:

  - cute pun, dizzy fishman → Diffie–Hellman
  - reading the provided source code, the secrets A and B are tiny (2 ≤ A, B ≤ 10,000), so we can brute force 'em
    ```
    $ nc chals.jellyc.tf 4000
    Intercepting communications...
    Randomly selected prime p =  105151773691284501367908040288984047453584122963028769865385830327263592615439
    Inject a generator g: 3
    Dizzy's public key (integer) :  58402797610660316034951212841302152215802936825458311428521819400961757846573
    Sakana's public key (integer):  51401755871926019916610072848250739109299635410755239388343970996115258093065
    Dizzy and Sakana are calculating their secret keys...
    Encrypting flag with AES-256 using shared secret key
    Encrypted flag received:  b24f2b3301a723cb71c45950a189afa9ce45567e28d0e3b73ee78bf2532589a85f277b1f817074dff3d7792ed8fb2ffe5f277b1f817074dff3d7792ed8fb2ffe
    ```
    ```pycon
    >>> MAX_INT = 10000
    >>> p = 105151773691284501367908040288984047453584122963028769865385830327263592615439
    >>> g = 3
    >>> public_key_A = 58402797610660316034951212841302152215802936825458311428521819400961757846573
    >>> public_key_B = 51401755871926019916610072848250739109299635410755239388343970996115258093065
    >>> 
    >>> for i in range(2, MAX_INT + 1):
    ...     if pow(g, i, p) == public_key_A:
    ...         secret_A = i
    ...         print("Dizzy's private key (integer) : ", secret_A)
    ...         # let loop continue, in case g generates a subgroup?
    ... 
    Dizzy's private key (integer) :  4717
    >>> for i in range(2, MAX_INT + 1):
    ...     if pow(g, i, p) == public_key_B:
    ...         secret_B = i
    ...         print("Sakana's private key (integer): ", secret_B)
    ...         # let loop continue, in case g generates a subgroup?
    ... 
    Sakana's private key (integer):  5589
    >>> secret_dizzy = pow(public_key_B, secret_A, p)
    >>> secret_sakana = pow(public_key_A, secret_B, p)
    >>> # The secret key should be the same for both parties
    >>> assert(secret_dizzy == secret_sakana)
    >>> 
    >>> from binascii import a2b_hex
    >>> ciphertext = a2b_hex('b24f2b3301a723cb71c45950a189afa9ce45567e28d0e3b73ee78bf2532589a85f277b1f817074dff3d7792ed8fb2ffe5f277b1f817074dff3d7792ed8fb2ffe')
    >>> 
    >>> from Crypto.Cipher import AES
    >>> from Crypto.Util.Padding import unpad
    >>> encoded_key = secret_sakana.to_bytes(32, byteorder='big')
    >>> cipher = AES.new(encoded_key, AES.MODE_ECB)
    >>> flag = unpad(cipher.decrypt(ciphertext), 32)
    >>> print(flag)
    b'jellyCTF{SOS_stuck_in_warehouse}'
    ```
