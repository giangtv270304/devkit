.PHONY: test lint

test:
	cd tests && python3 -m unittest discover -v

lint:
	@for f in hooks/*.sh hooks/lib/*.sh git-local/*.sh git-local/commit-msg git-local/pre-push .githooks/* bin/herdr-task; do \
		bash -n $$f || exit 1; \
	done
	@python3 -m py_compile install.py hooks/*.py skills/*/*.py tests/*.py
	@find . -name __pycache__ -not -path './.git/*' -prune -exec rm -rf {} +
	@cd tests && python3 -m unittest test_skills
	@if command -v shellcheck >/dev/null 2>&1; then \
		shellcheck -S warning hooks/*.sh hooks/lib/*.sh git-local/*.sh git-local/commit-msg git-local/pre-push; \
	else echo "warning: shellcheck not installed, skipped"; fi
	@if command -v ruff >/dev/null 2>&1; then ruff check .; \
	else echo "warning: ruff not installed, skipped"; fi
