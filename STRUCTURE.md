# Library folder guide

The collection is organized **by subject first**. When the books in a subject are specifically about a programming language or platform, use a nested folder; books covering several languages or no language stay directly in the subject folder.

```text
algorithms/                 # general algorithms; language-specific books in java/, javascript/, etc.
architecture/               # architecture and design; language-specific examples nested underneath
career/interviews/
cloud/
databases/                  # oracle/, postgresql/, sql/
data/big-data/
games/                       # game development; language-specific books nested underneath
mobile/                      # android/, ios/, ipad/
networking/                  # language-specific material (such as Java network programming) nested underneath
operating-systems/
programming-languages/       # books primarily teaching a language: java/, python/, etc.
security/                    # language-specific security books nested underneath
software-engineering/        # general programming and development practice
text-processing/regular-expressions/
tools/                       # jira/, velocity/, etc.
web/                         # general web books; javascript/, typescript/, nodejs/, markup/, java/
```

## Apply the reorganization

The migration helper preserves original book filenames and moves tracked files/directories with `git mv`, so Git can recognize renames. It updates existing README links and defaults to a dry run. From a clean checkout on the `reorganize-book-structure` branch:

```bash
python3 scripts/reorganize.py             # preview the moves
python3 scripts/reorganize.py --apply     # move the files
```

Review the resulting changes, then commit and open a pull request. The script intentionally skips untagged root entries and does not delete or alter book contents.
