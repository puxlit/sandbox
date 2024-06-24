# [crypto] you're_based

<table><tbody>
<tr><th>Value</th><td>757 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
</tbody></table>

Here's a **basic** encoding challenge to start with:
`VGhhdCB3YXMganVzdCBhIHdhcm0gdXAuIEhlcmUgaXMgdGhlIGFjdHVhbCBmbGFnLCB0aG91Z2ggeW91IG1heSBuZWVkIGEgYmFzZSB0aGF0J3MgJ0EnIGJpdCBsYXJnZXI6CumpquqNrOehueetlPCTibvmmajpkbPmqanqhZ/wk4W16ZG06ZGh5qWi5pmz6ZGj8JSVofCUlaHwlJWh8JOBofCTja3woI2w`

---

raw notes:

  - I spy Base64…
    ```pycon
    >>> l0ct = 'VGhhdCB3YXMganVzdCBhIHdhcm0gdXAuIEhlcmUgaXMgdGhlIGFjdHVhbCBmbGFnLCB0aG91Z2ggeW91IG1heSBuZWVkIGEgYmFzZSB0aGF0J3MgJ0EnIGJpdCBsYXJnZXI6CumpquqNrOehueetlPCTibvmmajpkbPmqanqhZ/wk4W16ZG06ZGh5qWi5pmz6ZGj8JSVofCUlaHwlJWh8JOBofCTja3woI2w'
    >>> import binascii
    >>> l0pt = binascii.a2b_base64(l0ct)
    >>> l0pt
    b"That was just a warm up. Here is the actual flag, though you may need a base that's 'A' bit larger:\n\xe9\xa9\xaa\xea\x8d\xac\xe7\xa1\xb9\xe7\xad\x94\xf0\x93\x89\xbb\xe6\x99\xa8\xe9\x91\xb3\xe6\xa9\xa9\xea\x85\x9f\xf0\x93\x85\xb5\xe9\x91\xb4\xe9\x91\xa1\xe6\xa5\xa2\xe6\x99\xb3\xe9\x91\xa3\xf0\x94\x95\xa1\xf0\x94\x95\xa1\xf0\x94\x95\xa1\xf0\x93\x81\xa1\xf0\x93\x8d\xad\xf0\xa0\x8d\xb0"
    >>> 
    >>> l1ct = l0pt[l0pt.find(b'\n') + 1:]
    >>> l1ct.decode()
    '驪ꍬ硹答𓉻晨鑳橩ꅟ𓅵鑴鑡楢晳鑣𔕡𔕡𔕡𓁡𓍭𠍰'
    ```
  - I spy CJK characters, which reminds me of the shitpost [Base65536](https://github.com/qntm/base65536?tab=readme-ov-file#why)…
    ```pycon
    >>> import base65536  # <https://github.com/Parkayun/base65536/tree/0.1.1>
    >>> l1pt = base65536.decode(l1ct.decode())
    >>> l1pt
    b'jellyCTF{th1s_i5_just_a_b4s1c_awawawarmup}'
    ```
