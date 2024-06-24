# [crypto] cipher_check

<table><tbody>
<tr><th>Value</th><td>766 pts</td></tr>
<tr><th>Tags</th><td><code>medium</code></td></tr>
<tr><th>Author</th><td>Meow Mix</td></tr>
<tr><th>Files</th><td><a href="./files/cipher_check.zip">cipher_check.zip</a></td></tr>
</tbody></table>

Let's see if you can decode some common ciphers!
Decoding ciphers may be tricky, especially when you're new to CTFs, but... 

**jellyCTF{ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ \_ } (12 characters)**

-----

**15 point hint:** I have the board completed. Where is the flag?

**20 point hint:** I do not have the board completed. May I have a list of ciphers used to complete the board?

-----

**Note:** The .xlsx file is not required to complete this challenge but it's highly recommended to upload it to Google Drive to collaborate with your team!

---

raw notes:

  - across
    <table><thead>
    <tr><th>#</th><th>Clue</th><th>Answer</th><th>Notes</th></tr>
    </thead><tbody>
    <tr><td>a8</td><td>ARNFSOWLEL</td><td>ANSWERFOLL</td><td>odd letters, then even letters</td></tr>
    <tr><td>a7</td><td>awa awa awa awa awa awa awa awawawa awawa awa awa awawa awawa awa awa awa awa awa awawa awa awa awawa awawawa awa awawa awa awa awa awawa awawawa awa awawa awawa awa awawawa awawawawa awa awa awa awawa</td><td>ANSWERISTD</td><td>AwaSCII</td></tr>
    <tr><td>a6</td><td>65 78 83 87 69 82 81 67 73 78</td><td>ANSWERQCIN</td><td>base 10 → ASCII</td></tr>
    <tr><td>a5</td><td>41 4e 53 57 45 52 49 4c 4f 4e</td><td>ANSWERILON</td><td>hex → ASCII</td></tr>
    <tr><td>a4</td><td>cipher-flags.png</td><td>ANSWERIALL</td><td><a href="https://www.dcode.fr/semaphore-flag">flag semaphore</a></td></tr>
    <tr><td>a3</td><td>cipher-symbols.png</td><td>ANSWERPEVE</td><td><a href="https://www.dcode.fr/pigpen-cipher">pigpen cipher</a></td></tr>
    <tr><td>a2</td><td>AENNWROMSW</td><td>ANSWERWONM</td><td><a href="https://www.dcode.fr/rail-fence-cipher">rail fence cipher</a> (encoded as 3 rails, ↘↗)</td></tr>
    <tr><td>a1</td><td>cipher-pattern.png</td><td>ANSWERN6MO</td><td><a href="https://www.dcode.fr/maritime-signals-code">International Code of Signals</a></td></tr>
    <tr><td>e8</td><td>ZMHDVILDNL</td><td>ANSWEROWMO</td><td><a href="https://www.dcode.fr/atbash-cipher">Atbash cipher</a></td></tr>
    <tr><td>e7</td><td>QFLVTKXTSB</td><td>ANSWERUELX</td><td><a href="https://www.dcode.fr/monoalphabetic-substitution">Monoalphabetic substitution cipher</a> (encoded as <code>ABCDEF…</code> → <code>QWERTY…</code>)</td></tr>
    <tr><td>e6</td><td>.- -. ... .-- . .-. -.. . - .-</td><td>ANSWERDETA</td><td><a href="https://www.dcode.fr/morse-code">Morse code</a></td></tr>
    <tr><td>e5</td><td>1000001 1001110 1010011 1010111 1000101 1010010 1010011 1010000 1000101 1000011</td><td>ANSWERSPEC</td><td>binary → ASCII</td></tr>
    <tr><td>e4</td><td>NAFJREVARH</td><td>ANSWERINEU</td><td><a href="https://www.dcode.fr/rot-cipher">ROT cipher</a> (encoded as <code>[A-Z]+13</code>, a.k.a. ROT13)</td></tr>
    <tr><td>e3</td><td>AJSSENNPHA</td><td>ANSWERNTHE</td><td><a href="https://www.dcode.fr/rot-cipher">ROT cipher</a> (encoded as <code>[A-Z]+22</code>) for even letters only</td></tr>
    <tr><td>e2</td><td>BNTWFRBTFI</td><td>ANSWERATEI</td><td><a href="https://www.dcode.fr/rot-cipher">ROT cipher</a> (encoded as <code>[A-Z]+1</code>) for odd letters only</td></tr>
    <tr><td>e1</td><td>p}$(t#'t$P</td><td>ANSWERVES!</td><td><a href="https://www.dcode.fr/rot-cipher">ROT cipher</a> (encoded as <code>[!-~]+47</code>, a.k.a. ROT47)</td></tr>
    </tbody></table>
  - down
    <table><thead>
    <tr><th>#</th><th>Clue</th><th>Answer</th><th>Notes</th></tr>
    </thead><tbody>
    <tr><td>a8</td><td>UVU1VFYwVlNSa2xSU1E9PQ==</td><td>ANSWERFIQI</td><td>Base64 2×</td></tr>
    <tr><td>b8</td><td>IFHFGV2FKJHVGQ2M</td><td>ANSWEROSCL</td><td><a href="https://www.dcode.fr/base-32-encoding">Base32</a></td></tr>
    <tr><td>c8</td><td>QU5TV0VSTFRJTw==</td><td>ANSWERLTIO</td><td>Base64</td></tr>
    <tr><td>d8</td><td>101 116 123 127 105 122 114 104 116 116</td><td>ANSWERLDNN</td><td>octal → ASCII</td></tr>
    <tr><td>e8</td><td>AAAAA ABBAB BAABA BABBA AABAA BAAAB ABBBA BABAA AAABB BAABA</td><td>ANSWEROUDS</td><td>binary (A=0, B=1) → nth (zero-indexed) letter of the alphabet</td></tr>
    <tr><td>f8</td><td>⠁⠝⠎⠺⠑⠗⠺⠑⠑⠏</td><td>ANSWERWEEP</td><td><a href="https://www.dcode.fr/braille-alphabet">Braille</a></td></tr>
    <tr><td>g8</td><td>1 14 19 23 5 18 13 12 20 5</td><td>ANSWERMLTE</td><td>nth (one-indexed) letter of the alphabet</td></tr>
    <tr><td>h8</td><td>CAXOREWSNA</td><td>ANSWEROXAC</td><td>reverse string</td></tr>
    <tr><td>a4</td><td>✌︎☠︎💧︎🕈︎☜︎☼︎✋︎🏱︎🕈︎☠︎</td><td>ANSWERIPWN</td><td><a href="https://www.dcode.fr/wingdings-font">Wingdings</a></td></tr>
    <tr><td>b4</td><td>0 26 10 1 5 36 0 5 9 48</td><td>ANSWERAEO6</td><td>nth (zero-indexed) letter of AwaSCII alphabet</td></tr>
    <tr><td>c4</td><td>&amp;#65;&amp;#78;&amp;#83;&amp;#87;&amp;#69;&amp;#82;&amp;#76;&amp;#86;&amp;#78;&amp;#77;</td><td>ANSWERLVNM</td><td>HTML character references</td></tr>
    <tr><td>d4</td><td>cipher-boxes.png</td><td>ANSWERLEMO</td><td><a href="https://www.dcode.fr/tic-tac-toe-cipher">tic-tac-toe cipher</a></td></tr>
    <tr><td>e4</td><td>BOTXFSJOBW</td><td>ANSWERINAV</td><td><a href="https://www.dcode.fr/rot-cipher">ROT cipher</a> (encoded as <code>[A-Z]+1</code>)</td></tr>
    <tr><td>f4</td><td>JRDHCYBLAM</td><td>ANSWERNTTE</td><td><a href="https://www.dcode.fr/vigenere-cipher">Vigenère cipher</a> (encoded with the key <code>JELLYHOSHI</code>)</td></tr>
    <tr><td>g4</td><td>2 66 7777 9 33 777 33 44 33 7777</td><td>ANSWEREHES</td><td><a href="https://www.dcode.fr/multitap-abc-cipher">Multi-tap</a></td></tr>
    <tr><td>h4</td><td>414e5357455255454921</td><td>ANSWERUEI!</td><td>hex → ASCII</td></tr>
    </tbody></table>
  - message: `FOLLOW MOIST DUEL XQC IN DETAIL ON SPECIAL LINE UP EVENT HE WON MATE IN 6 MOVES!`
  - game in question: <https://www.chess.com/game/live/4977461657>
  - clip for amusement: <https://www.youtube.com/watch?v=e91M0XLX7Jw>
  - take the coordinates for each of the 12 chess moves, and map to the corresponding letter in crossword coordinates, yielding: `ISTILLLOVEIT`
  - flag is `jellyCTF{ISTILLLOVEIT}`
  - meta: didn't figure out chess coordinates → crossword coordinates transformation until we'd first made the connection between the two stages in the similar [[misc] is_jelly_stuck](../../misc/is_jelly_stuck/README.md)
