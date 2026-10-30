# Shupeng Ning — academic homepage

An English academic website based on the Academic Pages / Minimal Mistakes layout and stylesheet. The original MIT notice is retained in `LICENSE.academicpages`. This is a portable static adaptation: Markdown and JSON are rendered with Python rather than the upstream Jekyll engine. The complete site has no browser-side package dependencies or third-party analytics.

## Edit content

- `content/profile.json`: name, role, contact links, canonical domain.
- `content/about.md`: biography, research interests, and selected publications.
- `content/research.md`: research narrative and figures.
- `content/publications.json`: 30 publications, authors, and original links.
- `content/teaching.md`: teaching, mentoring, and reviewing (currently hidden from the navigation).
- `content/cv.md`: web CV.
- `assets/images/portrait.jpg`: user-supplied portrait, displayed using CSS only.
- `assets/images/duet-architecture.png` and `cirptc-chip.jpg`: user-supplied illustrations for the two featured photonic-computing papers.
- `assets/images/peic_review_thumb.svg`: author-supplied SVG illustration for the JLT review, showing a neural network above a photonic tensor core and electronic control and memory. The supplied artwork is preserved unchanged.
- `assets/files/Shupeng_Ning_CV.pdf`: unchanged copy of the user-provided CV.
- `assets/css/custom.css`: appearance and mobile layout.

## Build and preview

```sh
python -m pip install -r requirements.txt
python scripts/build.py
python -m http.server 8765 --directory dist --bind 127.0.0.1
```

Visit http://127.0.0.1:8765/. `dist/` is self-contained and can be served by any static host. The build does not delete source files. To publish on a different domain, update `site_url` in the profile or pass `--site-url https://your-domain.example` when building.

## Publish on GitHub Pages

This project is connected to **https://github.com/spning0623/spning0623.github.io** on the `main` branch. GitHub Actions builds and deploys the website whenever a commit is pushed. The public URL is **https://spning0623.github.io/**.

From this project folder, publish local changes with:

```sh
python scripts/publish.py "Update academic homepage"
```

The helper builds locally, commits changed files, and pushes to GitHub. It stops on build or Git errors. GitHub then builds the committed source and deploys `dist/`. Check the [Actions page](https://github.com/spning0623/spning0623.github.io/actions) for deployment status.

Standard Git commands also work:

```sh
git add .
git commit -m "Update academic homepage"
git push
```

Under **Settings → Pages → Build and deployment**, the source must be **GitHub Actions**. `dist/`, the private Sites `.openai/` directory, and local `.env` files are ignored by Git. Edit files under `content/`, `assets/`, and `templates/`; `dist/` is generated output and should not be edited directly.

## Source and editorial notes

The biography and research descriptions were prepared from `Ning, Shupeng_CV.pdf` and the 4-page and 5-page research statements supplied in the TTAP workspace. Research images were rendered from the supplied figure PDFs. Original source documents remain unchanged.

- At the user's request, the downloadable CV is an unchanged copy of the original. The publication list describes the DUET manuscript as a preprint.
- arXiv ID `2605.23051`, the ASP-DAC DOI, and the PACE paper title were corrected using source links and official records.
- The website does not claim a first-author publication count because the CV list and RS count differ.
- Research efficiency projections are explicitly identified as projections.
- The full research statement, application letters, grant plans, and reference documents are not included in the website.
- The portrait was supplied by the user for this homepage. Research content and portrait are not offered under the template's software license.
