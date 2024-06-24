# [crypto] really_special_awawawas

<table><tbody>
<tr><th>Value</th><td>666 pts</td></tr>
<tr><th>Tags</th><td><code>medium</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
<tr><th>Files</th><td><a href="./files/vals.txt">vals.txt</a></td></tr>
</tbody></table>

A specially chosen modulus for a really special awatistic musical princess. 

dCode couldn't crack it so I'm sure it's secure... right?

Hint: General steps to solution + link to a post

---

raw notes:

  - the "specially chosen modulus" refers to n, which is supposed to be the product of two (or more) large (and sufficiently distant) primes, but…
  - courtesy of <https://www.dcode.fr/prime-factors-decomposition>, the prime factors of n are 5, 23, 460465412038271581, and 757179525420813109550252454787205779901919127
  - we're dealing with multiprime RSA
    ```
         n = 40095322948381328531315369020145890848992927830000776301309425505
           = 5 * 23 * 460465412038271581 * 757179525420813109550252454787205779901919127
         e = 65537
         c = 35622053067320123838840878683947610930876835359945867019927573838
    
    # using Carmichael's totient function
    tot(n) = lcm(5 - 1, 23 - 1, 460465412038271581 - 1, 757179525420813109550252454787205779901919127 - 1)
           = 639200800626369004183531825455472776460656304698122436971104980
         d ≡ e^-1 (mod(tot(n)))
         d = 287458461584463336135331697997301511216944981741119712297623893   // (using <https://www.dcode.fr/modular-inverse>)
    
         m = c^d (mod(n))
           = 667859681674751630937423997247174474842427366359093200105853      // (using <https://www.dcode.fr/modular-exponentiation>)
        c' = m^e (mod(n))
           = 35622053067320123838840878683947610930876835359945867019927573838
           = c                                                                 // (yay!)
    
    # using Euler's totient function
    tot(n) = (5 - 1) * (23 - 1) * (460465412038271581 - 1) * (757179525420813109550252454787205779901919127 - 1)
           = 30681638430065712200809527621862693270111502625509876974613039040
         d ≡ e^-1 (mod(tot(n)))
         d = 20102683281001902465824818287116957581497290427382915258401878273 // (using <https://www.dcode.fr/modular-inverse>)
    
         m = c^d (mod(n))
           = 667859681674751630937423997247174474842427366359093200105853      // same result as above
    ```
    ```pycon
    >>> int(667859681674751630937423997247174474842427366359093200105853).to_bytes(length=25, byteorder='big')
    b'jellyCTF{awawas_4_every1}'
    ```
