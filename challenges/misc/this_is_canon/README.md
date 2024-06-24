# [misc] this_is_canon

<table><tbody>
<tr><th>Value</th><td>766 pts</td></tr>
<tr><th>Tags</th><td><code>medium</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
<tr><th>Files</th><td><a href="./files/flag.txt">flag.txt</a></td></tr>
</tbody></table>

Is this meme still relevant?
![](./files/canon_meme.jpg)

Note: Flag format for this challenge is all lowercase: `jellyctf{lowercase_letters}`

---

raw notes:

  - Huffman coding! 😩
  - first line is number of symbols with prefix length i (where i is the one-based index), the second line are the symbols, and the third line is the encoded message
    ```
    # 0 symbols with length 1
    # 0 symbols with length 2
    # 4 symbols with length 3
    000 => _
    001 => e
    010 => l
    011 => y
    # 3 symbols with length 4
    1000 => j
    1001 => o
    1010 => r
    # 7 symbols with length 5
    10110 => a
    10111 => c
    11000 => d
    11001 => s
    11010 => t
    11011 => u
    11100 => w
    # 6 symbols with length 6
    111010 => f
    111011 => h
    111100 => k
    111101 => m
    111110 => {
    111111 => }
    
    # decoding
    1000   => j
    001    => e
    010    => l
    010    => l
    011    => y
    10111  => c
    11010  => t
    111010 => f
    111110 => {
    1000   => j
    001    => e
    010    => l
    010    => l
    011    => y
    000    => _
    011    => y
    1001   => o
    11011  => u
    1010   => r
    000    => _
    111011 => h
    1001   => o
    111101 => m
    001    => e
    11100  => w
    1001   => o
    1010   => r
    111100 => k
    000    => _
    11100  => w
    10110  => a
    11001  => s
    000    => _
    11000  => d
    11011  => u
    001    => e
    000    => _
    011    => y
    001    => e
    11001  => s
    11010  => t
    001    => e
    1010   => r
    11000  => d
    10110  => a
    011    => y
    111111 => }
    ```
  - flag is `jellyctf{jelly_your_homework_was_due_yesterday}`
  - meta: this is one of the handful of challenges that deviates from the `jellyCTF{}` flag wrapper
