# [crypto] you're_bababased?

<table><tbody>
<tr><th>Value</th><td>884 pts</td></tr>
<tr><th>Tags</th><td><code>medium</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
<tr><th>Files</th><td><a href="./files/list_of_safe_unicode_chars.txt">list_of_safe_unicode_chars.txt</a></td></tr>
</tbody></table>

nerd is you \
BABA is based \
flag is win

`ʿ蛧鸩ઞ假备㮝螖𐱇𓉺澟嬚ᱸ芋ᗋޥ𒒽瀏即𑠌獀ʞ`

10 point hint: What base to use \
30 point hint: Code snippet

---

raw notes:

  - initial thoughts: Base131072 (i.e. next one up from Base65536)? or… Base134513? (🤢)
    ```pycon
    >>> mapping = open('list_of_safe_unicode_chars.txt', 'r').read()
    >>> base = len(mapping)
    >>> base
    134513
    ```
  - we'd expect more coverage if that were the case…
    ```pycon
    >>> encoded_text = 'ʿ蛧鸩ઞ假备㮝螖𐱇𓉺澟嬚ᱸ芋ᗋޥ𒒽瀏即𑠌獀ʞ'
    >>> decoded_digits = [mapping.find(code_point) for code_point in encoded_text]
    >>> max(decoded_digits)
    44935
    ```
  - maybe we should take "bababased" literally, and the full `list_of_safe_unicode_chars.txt` is somewhat of a red herring
    ```pycon
    >>> base = 0xbaba
    >>> base
    47802
    ```
  - that looks promising!
    ```pycon
    >>> decoded_value = 0
    >>> for digit in decoded_digits:
    ...     decoded_value *= base
    ...     decoded_value += digit
    ... 
    >>> decoded_value
    58178783552345343101038105573060047959794449193621248458089508840762606751758689159191938580988908157
    >>> decoded_value.to_bytes(length=42, byteorder='big')
    b'jellyCTF{baba_is_cool_but_j3lly_i5_COOLER}'
    ```
