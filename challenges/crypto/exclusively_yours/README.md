# [crypto] exclusively_yours

<table><tbody>
<tr><th>Value</th><td>822 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
<tr><th>Files</th><td><a href="./files/encrypted.txt">encrypted.txt</a></td></tr>
</tbody></table>

I encrypted this flag **exclusively** for you... but I lost the key. I'm sure you can figure it out :>

Reminder: The flag format is `jellyCTF{...}`

---

raw notes:

  - challenge text emphasises "exclusively", so think XOR
  - ciphertext hex is `06 1C 2F 38 3F 38 2C 29 09 0A 16 2D 1C 16 2B 31 17 1B 2D 0A 16 0F 18 1C 11`
  - we expect the start and end plaintext to be `jellyCTF{` and `}`, so we can try XORing with the ciphertext to get a partial key: `6C 79 43 54 46 7B 78 6F 72 [15 bytes unknown] 6C`
  - if we look at the partial key in ASCII, we see: `"lyCTF{xor" [15 bytes unknown] "l"`
  - we can now work out more of the key(/plaintext) and ciphertext together
    ```
    ciphertext: 06 1C 2F 38 3F 38 2C 29 09 0A 16 2D 1C 16 2B 31 17 1B 2D 0A 16 0F 18 1C 11
    
           key: 6C 79 43 54 46 7B 78 6F 72 72 79 5F 6E 6F 74 5F 78 6F 72 72 79 7D 6A 65 6C
                l  y  C  T  F  {  x  o  r  r  y  _  n  o  t  _  x  o  r  r  y  }  j  e  l
    
     plaintext: 6A 65 6C 6C 79 43 54 46 7B 78 6F 72 72 79 5F 6E 6F 74 5F 78 6F 72 72 79 7D
                j  e  l  l  y  C  T  F  {  x  o  r  r  y  _  n  o  t  _  x  o  r  r  y  }
    ```
  - flag is `jellyCTF{xorry_not_xorry}`
