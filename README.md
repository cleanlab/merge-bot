# merge-bot
This action manages deployments by auto-merging PRs.

PRs are auto-merged after checks for:
- Review approvals by all requested reviewers
- All listed `dependent_checks` are passing
- PR is not labeled with `blocking_label`

PRs can be merged by fast-forwarding or a merge commit.

## Example Workflow
An example workflow is shown below. This workflow runs the `merge-bot` each time one of the below events occurs:

```yaml
name: merge-bot

on:
  pull_request:
    types:
      - labeled
      - ready_for_review
      - review_request_removed
      - review_requested
      - synchronize
      - unlabeled
  pull_request_review:
    types:
      - dismissed
      - submitted

jobs:
  merge-bot:
    runs-on: ubuntu-latest

    steps:
      - uses: cleanlab/merge-bot@v1.1.0
        with:
          dependent_checks: "check1,check2"
          blocking_label: "block-merge"
          merge_type: "fast-forward"
          delete_branch: true
```
