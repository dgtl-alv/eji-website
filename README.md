# Electra Jaringan Indonesia

Production: <https://www.electrajaringan.co.id>

English is served at `/`, Indonesian at `/id/`. `build.py` and `locations.py`
generate the six HTML pages; `assets/` contains the public styles, fonts and images.
The committed HTML pages also support the existing GitHub Pages publication.

## Change and deploy

1. Update the generators, data or assets. Regenerate the checked-in HTML with
   `python3 build.py .` when changing generated content.
2. Open a pull request. The **Validate and deploy production** workflow tests
   artifact handling, generates the site and checks every local link and anchor.
3. Push or merge to `main`. A successful validation triggers deployment to Jakarta
   and checks the public HTTPS pages. **Run workflow** on `main` can retry a release.

No AWS keys, server SSH keys or Cloudflare tokens are stored in GitHub Actions.
The deployment job uses GitHub OIDC, restricted to this repository's immutable
owner/repository IDs and `main`. Pull requests cannot assume the production role.
Actions are pinned to commit SHAs. Update these pins as part of dependency maintenance.

## Deployment operation

Copy `deploy/config.example.json` to the ignored `deploy/config.json` and fill in
the private production inventory. Store that JSON as the **EJI_PRODUCTION_CONFIG**
repository Actions secret before merging or running a production deployment. The
workflow masks its fields in logs and removes the temporary file when finished.
Production identifiers are not committed to this public repository.

AWS infrastructure is
managed by `deploy/provision.py` (requires boto3 and administrator credentials).
The bucket is private, encrypted, versioned and rejects insecure transport.
Deployment archives expire after 30 days; prior archive versions expire after 7 days.

CI packages only generated HTML, public assets and a release manifest. Each upload
is addressed by commit SHA and archive SHA-256. The CI role can upload these
artifacts and invoke only the configured fixed deployment document on the production instance.
It cannot run arbitrary SSM commands, change IAM, change DNS or install server code.

The administrator-installed `/opt/electrajaringan/deploy/receive.py` verifies the
instance, archive size and checksum, revision, safe file types and every file's
checksum before activation. It never executes artifact contents. Deployments are
serialized by a host lock; `html/current` switches atomically between release
directories. Origin health checks restore the previous symlink on failure.

Nginx serves `html/current` through the existing Cloudflare Tunnel on
the configured local origin; the container has no publicly bound port. Responses require cache
revalidation so deployments do not depend on a separate cache purge.
`/release.json` identifies the deployed commit. The server's
`/opt/electrajaringan/deployment.json` records its artifact digest and previous release.

## Validate locally

```bash
python3 -m unittest discover -s deploy/tests -v
python3 deploy/package.py "$(git rev-parse HEAD)"
```

The build requires only Python's standard library. `dist/site/` is the generated
static site, and `dist/site.tar.gz` is the deterministic deployment archive.

## Roll back

As an administrator, use the previous release's commit and full archive digest
from an earlier workflow log or deployment receipt:

```bash
aws ssm send-command --region "$AWS_REGION" \
  --document-name "$EJI_DEPLOY_DOCUMENT" \
  --instance-ids "$EJI_INSTANCE_ID" \
  --parameters 'Revision=[FULL_COMMIT_SHA],Digest=[FULL_ARCHIVE_SHA256]'
```

Poll the returned command ID with `aws ssm get-command-invocation` and verify
`https://www.electrajaringan.co.id/release.json`. Within the 30-day artifact retention
window, this revalidates and activates the exact archived release. Older retained
server releases can be restored locally by an administrator after checksum verification.
Automatic deployments resume on the next successful `main` push.

Changes to the receiver or Nginx configuration require administrator installation;
ordinary website deployments intentionally cannot modify the receiver.
