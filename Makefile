build: update-readme
	python -m build --sdist --wheel --outdir dist/ .

update-readme:
	cog -r README.md
