# [misc] this_is_canon

<table><tbody>
<tr><th>Value</th><td>935 pts</td></tr>
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

addendum:

  - if we didn't feel like decoding by hand…
    ```pycon
    >>> from typing import Optional
    >>> def create_huffman_table(symbols_per_length: list[int], symbols: list[str]) -> list[Optional[tuple[str, int]]]:
    ...     assert sum(symbols_per_length) == len(symbols)
    ...     max_symbol_length = len(symbols_per_length)
    ...     huffman_table: list[Optional[tuple[str, int]]] = [None] * (2 ** max_symbol_length)
    ...     code_value = 0
    ...     for (symbol_length, num_symbols) in enumerate(symbols_per_length, start=1):
    ...         for symbol in symbols[:num_symbols]:
    ...             shift_amount = max_symbol_length - symbol_length
    ...             entries_to_fill = 2 ** shift_amount
    ...             for lookup_value in range(code_value << shift_amount, (code_value << shift_amount) + entries_to_fill):
    ...                 assert huffman_table[lookup_value] is None
    ...                 huffman_table[lookup_value] = (symbol, symbol_length)
    ...             code_value += 1
    ...         symbols = symbols[num_symbols:]
    ...         code_value <<= 1
    ...     assert not symbols
    ...     return huffman_table
    ... 
    >>> def is_power_of_two(n: int) -> bool:
    ...     return (n != 0) and ((n & (n - 1)) == 0)
    ... 
    >>> def decode(huffman_table: list[Optional[tuple[str, int]]], encoded_string: tuple[int, int]) -> str:
    ...     assert len(huffman_table) >= 2 and is_power_of_two(len(huffman_table))
    ...     max_symbol_length = len(huffman_table).bit_length() - 1
    ...     (encoded_length, encoded_bits) = encoded_string
    ...     decoded_string = ''
    ...     while encoded_length > 0:
    ...         shift_amount = encoded_length - max_symbol_length
    ...         lookup_value = encoded_bits >> shift_amount if shift_amount >= 0 else encoded_bits << -shift_amount
    ...         result = huffman_table[lookup_value]
    ...         assert result is not None
    ...         (symbol, symbol_length) = result
    ...         decoded_string += symbol
    ...         encoded_length -= symbol_length
    ...         encoded_bits &= ((2 ** encoded_length) - 1)
    ...     assert encoded_length == 0
    ...     return decoded_string
    ... 
    >>> symbols_per_length = [0, 0, 4, 3, 7, 6]
    >>> symbols = ['_', 'e', 'l', 'y', 'j', 'o', 'r', 'a', 'c', 'd', 's', 't', 'u', 'w', 'f', 'h', 'k', 'm', '{', '}']
    >>> encoded_bits = 0b1000001010010011101111101011101011111010000010100100110000111001110111010000111011100111110100111100100110101111000001110010110110010001100011011001000011001110011101000110101100010110011111111
    >>> encoded_length = encoded_bits.bit_length()
    >>> huffman_table = create_huffman_table(symbols_per_length, symbols)
    >>> decode(huffman_table, (encoded_length, encoded_bits))
    'jellyctf{jelly_your_homework_was_due_yesterday}'
    ```
