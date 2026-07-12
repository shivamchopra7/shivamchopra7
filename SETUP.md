# Profile maintenance

The root README embeds the light or dark card from `assets/` according to the viewer's theme.
The scheduled GitHub Actions workflow refreshes public statistics every day at 03:17 UTC.

## Refresh locally

```bash
python3 -m pip install -r requirements.txt
python3 scripts/update_profile.py
```

`GITHUB_TOKEN` is optional locally and improves API rate limits. Never store it in this repository.

## Regenerate the portrait

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/make_ascii.py /path/to/avatar.png
```

The source photograph is intentionally not retained.
