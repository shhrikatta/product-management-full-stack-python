# GitHub Actions Workflows

## Test Coverage CI

### Overview
Automated testing workflow that runs on every push to `develop` or `main` branches and on pull requests. Ensures code quality and maintains 100% test coverage.

### Workflow: `test-coverage.yml`

#### Triggers
- **Push** to `develop` or `main` branches
- **Pull Requests** targeting `develop` or `main` branches

#### Jobs

##### 1. test-and-coverage
Runs the complete test suite with coverage analysis.

**Matrix Strategy:**
- Python versions: 3.11, 3.12, 3.13
- OS: Ubuntu Latest

**Steps:**
1. **Checkout code** - Fetches the latest code from repository
2. **Set up Python** - Configures Python environment with specified version
3. **Cache dependencies** - Caches pip packages for faster builds
4. **Install dependencies** - Installs all packages from requirements.txt
5. **Run linting** - Optional code quality checks with flake8
6. **Run unit tests** - Executes all unit tests (11 tests)
7. **Run integration tests** - Executes all integration tests (51 tests)
8. **Run all tests with coverage** - Full test suite with coverage reporting
9. **Check coverage threshold** - Enforces 100% coverage requirement
10. **Upload to Codecov** - Sends coverage data to Codecov (Python 3.13 only)
11. **Upload HTML report** - Saves coverage HTML report as artifact
12. **Comment on PR** - Posts coverage comment on pull requests
13. **Generate badge** - Creates coverage badge for develop branch
14. **Test Summary** - Generates workflow summary
15. **Notify on failure** - Alerts if tests fail or coverage drops

##### 2. coverage-enforcement
Secondary job that validates the test results.

**Purpose:**
- Ensures the test-and-coverage job completed successfully
- Provides clear failure messages if coverage drops below 100%

### Success Criteria ✅

The workflow succeeds when:
- ✅ All 62 tests pass (11 unit + 51 integration)
- ✅ Code coverage remains at 100%
- ✅ Tests pass on all Python versions (3.11, 3.12, 3.13)
- ✅ No critical linting errors

### Failure Scenarios ❌

The workflow fails when:
- ❌ Any test fails
- ❌ Coverage drops below 100%
- ❌ Tests fail on any Python version
- ❌ Coverage enforcement check fails

### Coverage Enforcement

**Current Threshold:** 100%

The workflow uses two mechanisms to enforce coverage:
1. `pytest --cov-fail-under=100` - Pytest fails if coverage < 100%
2. `coverage report --fail-under=100` - Additional coverage check

### Artifacts

Generated artifacts (available for 30 days):
- **coverage-report** - HTML coverage report (accessible from workflow run)

### Badges

You can add these badges to your README.md:

```markdown
![Test Coverage](https://github.com/shhrikatta/product-management-full-stack-python/workflows/Test%20Coverage%20CI/badge.svg)
![Coverage](coverage.svg)
```

### Local Testing

Before pushing, test locally to ensure CI will pass:

```bash
# Run all tests with coverage
pytest --cov=products --cov-report=term-missing --cov-fail-under=100

# Run unit tests only
pytest -m unit -v

# Run integration tests only
pytest -m integration -v

# Check linting
flake8 products.py
```

### Troubleshooting

#### Coverage drops below 100%
```bash
# Check which lines are missing coverage
pytest --cov=products --cov-report=term-missing

# Add tests for uncovered lines
# Run tests again to verify
```

#### Tests fail in CI but pass locally
- Check Python version compatibility
- Ensure all dependencies are in requirements.txt
- Check for environment-specific issues

#### Workflow fails to run
- Check YAML syntax
- Verify branch names in triggers
- Check GitHub Actions permissions

### Configuration

#### Enable Codecov (Optional)
1. Sign up at [codecov.io](https://codecov.io)
2. Add your repository
3. Get Codecov token
4. Add token to GitHub Secrets as `CODECOV_TOKEN`

#### Modify Coverage Threshold
Edit line 60 and 64 in `test-coverage.yml`:
```yaml
pytest --cov=products --cov-fail-under=90  # Change to desired %
coverage report --fail-under=90            # Change to desired %
```

#### Add More Python Versions
Edit matrix strategy (line 19):
```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12', '3.13', '3.14']
```

### Best Practices

1. **Always run tests locally before pushing**
2. **Keep coverage at 100%** - Add tests for new code
3. **Fix failing tests immediately** - Don't commit broken code
4. **Monitor workflow runs** - Check for failures
5. **Update dependencies regularly** - Keep requirements.txt current

### Workflow Status

Check workflow status:
- Go to repository → Actions tab
- View latest workflow runs
- Click on a run to see detailed logs
- Download artifacts (coverage reports)

### Integration with Pull Requests

When creating a PR:
1. Workflow runs automatically
2. Coverage comment is posted on PR
3. PR cannot merge if workflow fails (if branch protection enabled)
4. Review coverage report before merging

### Performance

Typical workflow execution time:
- **Setup & Dependencies**: ~30 seconds
- **Unit Tests**: ~1 second
- **Integration Tests**: ~1 second
- **Coverage Report**: ~1 second
- **Total**: ~1-2 minutes per Python version

With 3 Python versions running in parallel: **~2 minutes total**

### Notifications

GitHub automatically notifies on:
- Workflow failures
- First workflow run on a branch
- Workflow status changes

Configure notifications:
1. Go to GitHub Settings → Notifications
2. Configure Actions notifications
3. Choose email/web/mobile notifications

### Maintenance

Regular maintenance tasks:
- Update GitHub Actions versions when new releases available
- Update Python versions in matrix as new versions release
- Review and update coverage thresholds if needed
- Clean up old workflow runs (keep last 30 days)

### Support

For issues with the workflow:
1. Check workflow logs in Actions tab
2. Review this documentation
3. Check GitHub Actions documentation
4. Consult the project team
