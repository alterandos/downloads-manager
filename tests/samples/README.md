# Test Samples

Place real-world sample files here for manual or exploratory testing.
Files in this folder are not automatically used by the test suite —
the logic tests create their own temporary files programmatically.

## Suggested files

| Filename pattern                     | Tests                                 |
|--------------------------------------|---------------------------------------|
| `physio_invoice_*.pdf`               | Invoice classification (physio)       |
| `invoice_unknown.pdf`                | Invoice with no keyword hints         |
| `ES########_######_*.pdf`            | Rosemary bank statement routing       |
| `heroes_*.zip`                       | ZIP → HeroesMapHandler                |
| `plain.zip`                          | ZIP with no .h3m (should do nothing)  |
| `song.gpx` / `tab.gp5`              | Guitar Pro routing                    |
| `weird.xyz`                          | DefaultFileHandler prompt             |
| `downloading.crdownload`             | Ignored extension (no prompt)         |

## Running a sample file manually

```python
# From a Python shell in the project root:
import sys; sys.path.insert(0, '.')
from main import _dispatch_file
_dispatch_file(r'tests\samples\physio_invoice_jan.pdf')
```

## Note
Do not commit real financial documents (invoices, bank statements) to this folder.
