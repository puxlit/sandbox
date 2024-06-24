# [crypto] cult_classic_2

<table><tbody>
<tr><th>Value</th><td>860 pts</td></tr>
<tr><th>Tags</th><td><code>easy</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
</tbody></table>

See `cult_classic_1` for challenge files.
Enter the second flag into this challenge.

Clarifications for Stage 5:
- Make sure you're using the original source without modification (otherwise you may notice larger numbers than expected)
- If using online decoders but it's not working, try a quick manual check to see if the decoders doing what you expect

Please open a ticket in Discord if you believe you have the correct password and are running into unzipping issues

- First hint is for Stage 4
- Second hint is for Stage 5
- Third hint is for stage 6

---

raw notes:

  - in `04.txt`, ciphertext is `LBPTTULD`, and clue ("Cheating is not tolerated. We hope you play fair and square.") hints at Playfair cipher, which we can decrypt at <https://www.dcode.fr/playfair-cipher> (using the previously obtained key `ALIEN`) into the plaintext `ACOUSTIC`, which is the password to `04.zip`
  - in `05.txt`, searching for "🌠Don't Look Away... 🌠" gives us <https://www.youtube.com/watch?v=1x6oPy3Hwcw>. if we then interpret each pair of numbers as `line.column` coordinates into the lyrics in the video's description, we get `Capitalise 'megalencephaly' for the next password`, so `MEGALENCEPHALY` is the password to `05.zip`
  - dCode [identified](https://www.dcode.fr/cipher-identifier) `06.txt` as using Bacon's cipher. using <https://www.dcode.fr/bacon-cipher>, we get `THEFINALPASSWORDISSADGIRL`, so `SADGIRL` is the password to `flag.zip`
  - mojibake aside, the flag is `jellyctf{jelly_was_probably_older_than_these_ciphers}`
  - meta: this is one of the handful of challenges that deviates from the `jellyCTF{}` flag wrapper
