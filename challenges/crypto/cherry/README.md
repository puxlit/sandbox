# [crypto] cherry

<table><tbody>
<tr><th>Value</th><td>856 pts</td></tr>
<tr><th>Tags</th><td><code>hard</code></td></tr>
<tr><th>Author</th><td>Meow Mix</td></tr>
<tr><th>Connection info</th><td><a href="https://cherry.jellyc.tf/">https://cherry.jellyc.tf/</a></td></tr>
<tr><th>Files</th><td><a href="./files/cherry_dist.zip">cherry_dist.zip</a></td></tr>
</tbody></table>

A Starknight hacked an old slot machine and turned it into something strange?!
I heard that you win a secret message if you manage to get triple cherries, but...

---

raw notes:

  - reading the provided source code…
      - "change" button cycles between three starting configurations of reels (i.e. three ciphertexts)
      - "play 0/1/2 coin" + "spin" increment separate counters (which I'll call a/b/c) + advance the reels by differing amounts
      - there are 32,768 values on the reels, and the cherry is at position 0
      - when the reels read cherry, a/b/c should decode to some plaintext
  - basically, we're solving a system of linear congruences (in three variables)
    ```
    # first ciphertext
    10992 + a*19 + b*32 + c*347 ≡ 0 (mod 32768)
    30978 + a*22 + b*27 + c*349 ≡ 0 (mod 32768)
    12520 + a*19 + b*29 + c*353 ≡ 0 (mod 32768)
    --
    - guess a =  4194 (because we expect awascii32 to be "jel")
    - guess b = 29860 (because we expect awascii32 to be "lyC")
    - guess c = 25598 (because we expect awascii32 to be "TF{")
    - solution works!
    
    # second ciphertext
    30983 + a*19 + b*32 + c*347 ≡ 0 (mod 32768)
     7390 + a*22 + b*27 + c*349 ≡ 0 (mod 32768)
      481 + a*19 + b*29 + c*353 ≡ 0 (mod 32768)
    --
    - deferring to Wolfram Alpha: "solve the diophantine equations 30983 + 19a + 32b + 347c = 32768u, 7390 + 22a + 27b + 349c = 32768v, 481 + 19a + 29b + 353c = 32768w"
    - got a = 10469 => "you" in awascii32
    - got b =  7226 => "_wo" in awascii32
    - got c = 14158 => "n_c" in awascii32
    
    # third ciphertext
    25974 + a*19 + b*32 + c*347 ≡ 0 (mod 32768)
    26744 + a*22 + b*27 + c*349 ≡ 0 (mod 32768)
     9122 + a*19 + b*29 + c*353 ≡ 0 (mod 32768)
    ---
    - deferring to Wolfram Alpha: "solve the diophantine equations 25974 + 19a + 32b + 347c = 32768u, 26744 + 22a + 27b + 349c = 32768v, 9122 + 19a + 29b + 353c = 32768w"
    - got a = 20582 => "her" in awascii32
    - got b =  3380 => "rie" in awascii32
    - got c = 26344 => "s!}" in awascii32
    ```
