# [osint] stalknights_4

<table><tbody>
<tr><th>Value</th><td>584 pts</td></tr>
<tr><th>Tags</th><td><code>medium</code></td></tr>
<tr><th>Author</th><td>Sheepiroo</td></tr>
</tbody></table>

What is the real name of this starknight?

15 point hint: Search keywords

Flag format: `jellyCTF{firstname_lastname}`

---

raw notes:

  - tweet <https://x.com/starknight1337/status/1797980712014061965> reads:
    > Oh gosh nearly exposed myself, bless git push --force 🙏🙏🙏
  - guess they have a GitHub account → <https://github.com/starknight1337>
  - they've only one repo: <https://github.com/starknight1337/rustlings_practice>
  - we can view all activity on a branch (including commits that should be dangling after a force push): <https://github.com/starknight1337/rustlings_practice/activity?ref=main>
  - first commit of theirs is borked: <https://github.com/starknight1337/rustlings_practice/commit/2d52f1b3d6b7d63735a9e932fa049eb835753df8.patch>
    ```
    From 2d52f1b3d6b7d63735a9e932fa049eb835753df8 Mon Sep 17 00:00:00 2001
    From: Luke Ritterman <lritterman03@gmail.com>
    Date: Tue, 4 Jun 2024 02:06:57 +1000
    Subject: [PATCH] Finally starting to learn Rust
    ```
  - flag is `jellyCTF{luke_ritterman}`
