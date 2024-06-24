# [crypto] the_brewing_secrets

<table><tbody>
<tr><th>Value</th><td>919 pts</td></tr>
<tr><th>Tags</th><td><code>hard</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
<tr><th>Connection info</th><td><code>nc chals.jellyc.tf 6000</code></td></tr>
<tr><th>Files</th><td><a href="./files/the_brewing_secrets.zip">the_brewing_secrets.zip</a></td></tr>
</tbody></table>

Rumour has it Sakana stores the secret recipes for Phase Connect's coffee blends in his  ~~garage~~  'super secure laboratory'.
Can you hack your way in?

10 point hint: Hints for researching more information \
20 point hint: Link to proof-of-concept

---

raw notes:

  - reading the provided source code, we have 10 phases of 6-digit _binary_ passcodes to generate, but the PRNG is seeded by program start time:
    ```c
    int main(int argc, char **argv) {
        srand(time(NULL));
    ```
  - so what we can do is connect, and brute force times around connection time as seeds. once we complete phase 1, it's very likely we've got the right seed, so the remaining phases are a cakewalk
  - there might be some platform-level differences (arch, libc version) that cause subsequently generated values not to match; I wound up running this on an EC2 instance, and building with the latest `gcc` Docker image
    ```
    [ec2-user@ip-172-30-0-38 ~]$ ./crack
    t = 1718214278
    For phase 1, trying seed = 1718214273 (t-5)... does the passcode [000001] work? (y/n) n
    For phase 1, trying seed = 1718214274 (t-4)... does the passcode [110000] work? (y/n) n
    For phase 1, trying seed = 1718214275 (t-3)... does the passcode [110111] work? (y/n) n
    For phase 1, trying seed = 1718214276 (t-2)... does the passcode [111101] work? (y/n) n
    For phase 1, trying seed = 1718214277 (t-1)... does the passcode [001011] work? (y/n) n
    For phase 1, trying seed = 1718214278 (t+0)... does the passcode [100011] work? (y/n) y
    For phase 2, the passcode should be [000100].
    For phase 3, the passcode should be [000100].
    For phase 4, the passcode should be [110111].
    For phase 5, the passcode should be [101111].
    For phase 6, the passcode should be [000111].
    For phase 7, the passcode should be [000111].
    For phase 8, the passcode should be [011001].
    For phase 9, the passcode should be [100111].
    For phase 10, the passcode should be [100011].
    ```
    ```
    puxlit@kiara:~/Sandbox$ nc chals.jellyc.tf 6000
    
    
    Starting phase_number 1...
    WARNING: System will timeout after 69 entries
    Enter 6-digit binary passcode  
    000001
    Passcode incorrect. Try again!
    110000
    Passcode incorrect. Try again!
    110111
    Passcode incorrect. Try again!
    111101
    Passcode incorrect. Try again!
    001011
    Passcode incorrect. Try again!
    100011
    Phase number 1 - validation result: 1
    
    
    Starting phase_number 2...
    WARNING: System will timeout after 69 entries
    Enter 6-digit binary passcode  
    000100
    Phase number 2 - validation result: 1
    
    
    Starting phase_number 3...
    WARNING: System will timeout after 69 entries
    Enter 6-digit binary passcode  
    000100
    Phase number 3 - validation result: 1
    
    
    Starting phase_number 4...
    WARNING: System will timeout after 69 entries
    Enter 6-digit binary passcode  
    110111
    Phase number 4 - validation result: 1
    
    
    Starting phase_number 5...
    WARNING: System will timeout after 69 entries
    Enter 6-digit binary passcode  
    101111
    Phase number 5 - validation result: 1
    
    
    Starting phase_number 6...
    WARNING: System will timeout after 69 entries
    Enter 6-digit binary passcode  
    000111
    Phase number 6 - validation result: 1
    
    
    Starting phase_number 7...
    WARNING: System will timeout after 69 entries
    Enter 6-digit binary passcode  
    000111
    Phase number 7 - validation result: 1
    
    
    Starting phase_number 8...
    WARNING: System will timeout after 69 entries
    Enter 6-digit binary passcode  
    011001
    Phase number 8 - validation result: 1
    
    
    Starting phase_number 9...
    WARNING: System will timeout after 69 entries
    Enter 6-digit binary passcode  
    100111
    Phase number 9 - validation result: 1
    
    
    Starting phase_number 10...
    WARNING: System will timeout after 69 entries
    Enter 6-digit binary passcode  
    100011
    Phase number 10 - validation result: 1
    Validation successful. Unlocking garage door: jellyCTF{mad3_w1th_99_percent_l0v3_and_1_percent_sad_g1rl_t3ars}
    ```
