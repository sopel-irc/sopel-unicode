build: update-readme
	python3 -m build

update-readme:
	cog -r README.md
