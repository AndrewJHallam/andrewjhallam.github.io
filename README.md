# Andrew Hallam — academic website

Personal academic website for Andrew Hallam, Quantum Fellow at EPCC, University of Edinburgh.

Website address: <https://andrewjhallam.github.io/>

## Edit the website

The website is one plain HTML page with a separate stylesheet. A small Python script generates it from two editable data files. No framework, package manager, JavaScript, or Python packages are needed to build the website.

- `profile.json`: biography, current role, email addresses, research summaries, appointments, education, teaching, and selected talks.
- `publications.json`: publication titles, authors, years, journal citations, and paper links.
- `styles.css`: colours, typography, spacing, mobile layouts, and print styles.
- `andrew-hallam.jpg`: the website portrait, resized from the supplied photograph with permission.

After editing the data, regenerate the website:

```sh
python3 build.py
```

The script writes `index.html`, `404.html`, `sitemap.xml`, `robots.txt`, and `.nojekyll`. Commit the generated files along with your source changes. Changes made directly to generated HTML will be overwritten the next time the script runs.

The page includes the complete numbered bibliography, ordered by year. Publications within a year follow the order in `publications.json`, so move entries to change that order.

## Update the downloadable CV

`make_public_cv.py` generates the public PDF using ReportLab:

```sh
python3 -m pip install reportlab
python3 make_public_cv.py
```

The PDF uses the bibliography in `publications.json`. Its other professional details are embedded in `make_public_cv.py`; update them alongside `profile.json` when a role or contact detail changes. The original supplied CV is not needed to rebuild the public version.

The public CV intentionally excludes the home address, phone number, and obsolete Leeds email. The Edinburgh appointment's start date and the Leeds appointment's end date were not supplied; the current role is undated and Leeds is marked as a previous appointment starting in 2020. Add exact dates to both source files when available.

## Preview locally

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open <http://127.0.0.1:8000/>. Stop the server with Ctrl+C.

## GitHub Pages

Repository: `AndrewJHallam/andrewjhallam.github.io`.

Keep the website files at the repository root; no additional directories are required. In **Settings → Pages**, use **Deploy from a branch**, with branch **main** and folder **/(root)**. The generated website is committed directly, so no custom build workflow is required. `.nojekyll` tells GitHub to serve the static files directly.

For local updates after cloning the repository:

```sh
python3 build.py
git status --short
git add .
git commit -m "Update academic website"
git push
```

Run `python3 make_public_cv.py` too whenever the downloadable CV needs updating. GitHub Pages publishes commits to the configured source automatically.

When uploading through GitHub in a browser, upload the rebuilt files to the root of `main`. Include `index.html`, `styles.css`, the portrait, public CV PDF, favicon, and the generated support files. Keep the editable sources in the repository so future changes can be rebuilt.

If you add a custom domain, update `site_url` in `profile.json`, rebuild, and configure the domain in GitHub Pages settings.

## Content sources

Initial content was adapted from the supplied 2026 CV, current role and contact details supplied directly by Andrew, and primary publication records checked on 21 October 2026. The bibliography has 23 distinct works and links to journal/DOI and arXiv records. It includes three newer works absent from the supplied CV, and updates several preprints to their journal versions. It excludes duplicate Scholar entries and does not display citation counts.

Research summaries are drafted for this site and should be reviewed as you refine your academic profile. Google Scholar, LinkedIn, and GitHub links use the profiles supplied by Andrew. The LinkedIn page was not accessible during drafting, so it was used only as a profile link.

## Files and privacy

The hosted files contain professional information only. Keep original CVs and other private documents outside this repository. The resized portrait has no EXIF metadata. There are no analytics, contact forms, external fonts, third-party scripts, or cookies added by this website. Hosting providers may have their own logging policies.
