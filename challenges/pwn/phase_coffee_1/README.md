# [pwn] phase_coffee_1

<table><tbody>
<tr><th>Value</th><td>100 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
<tr><th>Connection info</th><td><code>nc chals.jellyc.tf 5000</code></td></tr>
<tr><th>Files</th><td><a href="./files/phase_coffee_1.zip">phase_coffee_1.zip</a></td></tr>
</tbody></table>

> **Phase Connect Coffee Shop**
> 
>Limited Jelly Hoshiumi coffee for sale now!
>
>-- *insert Jelly coffee description here* --

I really gotta get my balance up for this... maybe I should try meal replacements

This challenge is **part 1** out of 3 challenges.

Completing this challenge will unlock 1 challenge.

---

raw notes:

  - reading the provided source code, we can exploit a logic error and buy negative quantities to increase our balance
  - we want some quantity q such that:
    ```
    100 - (35 * q) ≥ 1000000
        - (35 * q) ≥ 999900
                q  ≲ -28568.5714285714 (e.g. -28569)
    ```
    ```
    Currently on sale
    1. Kaneko Lumi Inspired - $35 each (100 in stock)
    2. Jelly Hoshiumi Inspired (Limited Edition) - $1,000,000 each (1 in stock)
    Please make a selection: 1
    
    Enter desired quantity: -28569
    
    Current balance: 100
    Total cost: -999915
    -28569 coffees purchased! Your coffee is being packaged and will be delivered in 2028!
    
    Current balance: 1000015
    ```
    ```
    Currently on sale
    1. Kaneko Lumi Inspired - $35 each (28669 in stock)
    2. Jelly Hoshiumi Inspired (Limited Edition) - $1,000,000 each (1 in stock)
    Please make a selection: 2
    You have chosen the deluxe, premium, limited edition seiso idol princess Jelly Hoshiumi inspired coffee.
    This coffee costs $1,000,000. Press 1 to confirm purchase: 1
    YOUR FLAG IS: jellyCTF{sakana_your_C04433_shop_broke}
    ```
