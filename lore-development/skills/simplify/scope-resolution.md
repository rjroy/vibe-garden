# Simplify scope resolution

Load this reference only when resolving a Git or file scope.

- **No arguments:** Prefer an explicit work artifact identified by the invocation/current conversation. Otherwise use an integration/target branch only when authoritative repository metadata or user context identifies it; use its unique merge-base with `HEAD` as the committed boundary and ask if ambiguous. An explicit work-base commit established by user context is also a valid boundary. Never infer scope solely from `HEAD`, the latest commit, or `@{upstream}`: a feature branch may track itself, hiding committed work. Include relevant staged, unstaged, and untracked changes too. If no reliable artifact, target, or explicit base is known, ask for an artifact, Git base/range, or paths; do not default to dirty-only or the whole repository.
- **Explicit artifact:** Use its scope, including committed manifests and replacement/deletion references. Treat old artifacts as context, not authority over current user direction.
- **Git range or paths:** Support explicit user refs, file-pattern inputs, and notes paths as resume inputs. Resolve repo-relative paths against the repository root; inspect the named committed range as well as relevant pending changes.
- **Resolved scope:** Report source artifact/refs and included files, including deleted-file references and necessary adjacent code/tests. Follow replacement references to retained files; never recreate deleted files. Avoid unrelated files, commits, and reverts.
