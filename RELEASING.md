# Release candidate acceptance

The current source version is **0.2.0rc1**, an unpublished candidate. It adds the
opt-in strict allowlist API without changing default required/forbidden checks.
This document does not authorize creating a tag, uploading assets or publishing
to an index.

The previous public distribution is the GitHub **v0.1.2** release. The public
PyPI JSON endpoint returned HTTP 404 on 2026-10-31; a PyPI upgrade or adoption
claim would be incorrect. Its wheel has SHA-256:

```text
6715bff608e1256299e10ecbdf4711e03e5afe032ac43aaf3ac8a61ba0ff58f4
```

## Build and external consumer

Run the ordinary core/example tests, Ruff, formatting and mypy checks first.
Then build both artifacts from the reviewed source with the declared Hatchling
backend, and retain their SHA-256 and source revision:

```bash
python -m build
```

Create a fresh virtual environment **outside the checkout**, install the built
wheel and mypy there, and copy `tests/fixtures/typed_release_consumer.py` to that
external directory. With that environment's Python, run:

```bash
python -m pip check
python -m mypy --strict --no-incremental typed_release_consumer.py
python typed_release_consumer.py
```

The consumer asserts its import comes from the environment's site-packages,
checks package/public version parity, and executes both strict entry points and
the compatible open-world default. CI also requires a deliberately mistyped
consumer call to fail with an argument-type diagnostic. Merely shipping
`py.typed`, importing from the checkout or running mypy without strict mode does
not replace this installed-consumer acceptance.

## Previous-version upgrade

Use a separate fresh environment and the actual v0.1.2 GitHub wheel, verified
against the digest above. Before upgrading, record its version and execute the
legacy contract: required/forbidden structured failures, default acceptance of
undeclared tools, synchronous/asynchronous factories and profile checks, CLI
exit codes and pytest plugin discovery. Save the baseline result and installed
package versions. Do not request strict mode from v0.1.2: it does not provide it.

Install the explicit local candidate wheel in the same environment with
`python -m pip install --upgrade /absolute/path/to/mcp_capguard-0.2.0rc1-py3-none-any.whl`.
Run the same legacy consumer and compare results. Then run the strict consumer,
CLI negative controls and `pip check`. The candidate must retain old public
parameters/defaults; new strict parameters must remain optional. Record the
actual commands, artifacts, interpreter/platform, output and failures.

## Publication handoff

The reviewer should receive the source revision/diff, wheel and sdist hashes,
core/example and installed-consumer results, upgrade baseline comparison,
dependency-profile evidence and known limitations. Keep candidate version,
`__version__`, changelog and artifact metadata aligned. A final version requires
its own explicit version selection and acceptance; never overwrite the v0.1.2
assets or present this candidate as an already published final release.

After separate publication authorization, use the selected immutable artifacts
and release version, verify the newly published download digest, and repeat a
clean install from that published URL. PyPI onboarding, trusted publishing and
credentials are separate actions. No such settings, upload or release occurs
as part of candidate preparation.

These checks establish software compatibility and client-visible tool exposure.
They do not invoke upstream tools, enforce runtime authorization, demonstrate
independent adoption or qualify a production deployment.
