# Demo pack (fictional)

A tiny, made-up pack that shows the file layout, the document format and the markers, and lets you try
the build script. **Tidyhome, Examplia and every law named here are fictional.** Nothing in this folder is
legal advice or a statement of any real law.

Build it from the repository root:

```
pip install markdown
python scripts/build_pack.py examples/demo-pack
```

The script writes `drafts/questions-for-counsel.md`, `drafts/app-changes-needed.md`,
`drafts/law-research.md` and `review.html` (open it in a browser). Add `--check-publish` to see the go-live
check fail, as it should for drafts.
