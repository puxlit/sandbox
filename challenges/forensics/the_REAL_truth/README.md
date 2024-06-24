# [forensics] the_REAL_truth

<table><tbody>
<tr><th>Value</th><td>806 pts</td></tr>
<tr><th>Tags</th><td><code>medium</code></td></tr>
<tr><th>Author</th><td>arepi</td></tr>
<tr><th>Connection info</th><td><a href="https://therealtruthaboutjellyhoshiumi.carrd.co/">https://therealtruthaboutjellyhoshiumi.carrd.co/</a></td></tr>
</tbody></table>

note: this is the only subdomain in scope. do not bruteforce/dirbust.

10 point hint: tool to use

20 point hint: where to look

30 point hint: how to use the tool

---

raw notes:

  - the cyan bit at the top of `image01.png` looks suspicious…
    ```pycon
    >>> # zero-indexed, empirically determined
    >>> LAST_INTERESTING_PIXEL_X = 82
    >>> LAST_INTERESTING_PIXEL_Y = 5
    >>> 
    >>> from PIL import Image
    >>> im = Image.open('image01.png')
    >>> pixels = im.load()
    >>> assert LAST_INTERESTING_PIXEL_X < im.width
    >>> assert LAST_INTERESTING_PIXEL_Y < im.height
    >>> 
    >>> plaintext = ''
    >>> for y in range(LAST_INTERESTING_PIXEL_Y + 1):
    ...     for x in range(im.width):
    ...         (r, _, _) = pixels[x, y]
    ...         plaintext += chr(r)
    ...         if y == LAST_INTERESTING_PIXEL_Y and x == LAST_INTERESTING_PIXEL_X:
    ...             break
    ... 
    >>> plaintext
    'hello starknight. it is good to see you again. that you might uncover the truth from this image bodes well. however, do not grow complacent - for this is just the beginning of our journey together. further challenges await, and i shall be there. the time has come for us to part, but before we are separated, take this: jellyCTF{th3_w0man_in_th3_r3d_ch4nn3l} :siht ekat ,detarapes era ew erofeb tub ,trap ot su rof emoc sah emit eht .ereht eb llahs i dna ,tiawa segnellahc rehtruf .rehtegot yenruoj ruo fo gninnigeb eht tsuj si siht rof - tnecalpmoc worg ton od ,revewoh .llew sedob egami siht morf hturt eht revocnu thgim uoy taht .niaga uoy ees ot doog si ti .thginkrats olleh :siht ekat ,detarapes era ew erofeb tub ,trap ot su rof emoc sah emit eht .ereht eb llahs i dna ,tiawa segnellahc rehtruf .rehtegot yenruoj ruo fo gninnigeb eht tsuj si siht rof - tnecalpmoc worg ton od ,revewoh .llew sedob egami siht morf hturt eht revocnu thgim uoy taht .niaga uoy ees ot doog si ti .thginkrats olleh :siht ekat ,detarapes era ew erofeb tub ,trap ot su rof emoc sah emit eht .ereht eb llahs i dna ,tiawa segnellahc rehtruf .rehtegot yenruoj ruo fo gninnigeb eht tsuj si siht rof - tnecalpmoc worg ton od ,revewoh .llew sedob egami siht morf hturt eht revocnu thgim uoy taht .niaga uoy ees ot doog si ti .thginkrats olleh :siht ekat ,detarapes era ew erofeb tub ,trap ot su rof emoc sah emit eht .ereht eb llahs i dna ,tiawa segnellahc rehtruf .rehtegot yenruoj ruo fo gninnigeb eht tsuj si siht rof - tnecalpmoc worg ton od ,revewoh .llew sedob egami siht morf hturt eht revocnu thgim uoy taht .niaga uoy ees ot doog si ti .thginkrats olleh :siht ekat ,detarapes era ew erofeb tub ,trap ot su rof emoc sah emit eht .ereht eb llahs i dna ,tiawa segnellahc rehtruf .rehtegot yenruoj ruo fo gninnigeb eht tsuj si siht rof - tnecalpmoc worg ton od ,revewoh .llew sedob egami siht morf hturt eht revocnu thgim uoy taht .niaga uoy ees ot doog si ti .thginkrats olleh'
    ```
