# Contributing

## Branch workflow

This repository uses a **private mirror** (`briefcasebrain/briefcase-ai-usage-examples-internal`) for in-progress work before it is ready to appear in the public repo (`briefcasebrain/briefcase-ai-usage-examples`).

### Setup (one time)

```bash
git clone https://github.com/briefcasebrain/briefcase-ai-usage-examples-internal.git
cd briefcase-ai-usage-examples-internal
git remote add public https://github.com/briefcasebrain/briefcase-ai-usage-examples.git
```

### Day-to-day development

Work on the internal repo as normal. Push to the private remote:

```bash
git push origin <branch>
```

### Publishing changes to the public repo

When a branch is ready to go public:

1. **Fetch the latest public main**
   ```bash
   git fetch public main
   ```

2. **Rebase or merge onto public/main** to ensure a clean history
   ```bash
   git rebase public/main
   ```

3. **Push the branch to the public remote**
   ```bash
   git push public <branch>
   ```

4. **Open a PR** on `github.com/briefcasebrain/briefcase-ai-usage-examples` from `<branch>` → `main`.

5. **After the PR merges**, delete the branch from both remotes:
   ```bash
   git push public --delete <branch>
   git push origin --delete <branch>
   ```

### Access

To grant a team member access to the private mirror:
```bash
gh repo add-collaborator briefcasebrain/briefcase-ai-usage-examples-internal <github-username>
```
