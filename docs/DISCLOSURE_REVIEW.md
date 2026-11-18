# Static-site review and ownership

Owner: Erdal Kilic. Review date: 2026-11-18.

This review covers only the existing public information site's wording, HTML structure, links and review metadata. The previously published Google Sheets/dashboard information remains its scope. Private application capabilities, source, configuration and data are outside this public update. No private implementation review details are published here.

The original policy update date is retained. The new review date does not assert a full application/data-flow audit, security certification or legal compliance. The owner should check the accuracy of the applicable public statements when those disclosed functions change. No broader notice is inferred for undisclosed workflows.

## Change process

1. Confirm the intended public scope and compare proposed wording against authorized public facts.
2. Keep credentials, account settings, private documents and application source outside this repository.
3. Record what was reviewed and preserve the original policy date unless its substance changes.
4. Run `python3 -m unittest discover -s tests -v` and `python3 scripts/check_site.py`.
5. Inspect the published home/privacy/terms pages after deployment.

Review when the disclosed integration or its public wording changes. CI checks a limited HTML subset, internal links and required public sections; it cannot verify runtime behavior or policy truth. It is not a compliance badge.
