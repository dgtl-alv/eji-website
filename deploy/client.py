"""Upload a content-addressed artifact and invoke the fixed production receiver."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def aws(*args):
    return json.loads(subprocess.check_output(['aws', *args, '--output', 'json'], text=True))


def public_request(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'EJI-DeploymentCheck/1.0'}), timeout=15)


def main():
    config = json.loads((ROOT / 'deploy/config.json').read_text())
    artifact = json.loads((ROOT / 'dist/artifact.json').read_text())
    revision, digest = artifact['revision'], artifact['digest']
    head = subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/main'], text=True).split()[0]
    assert revision == head, 'A newer main revision exists; refusing a stale deployment'
    archive = ROOT / 'dist/site.tar.gz'
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == digest
    key = f'releases/{revision}/{digest}.tar.gz'
    aws('s3api', 'put-object', '--region', config['region'], '--bucket', config['bucket'], '--key', key, '--body', str(archive), '--server-side-encryption', 'AES256')
    command = aws('ssm', 'send-command', '--region', config['region'], '--instance-ids', config['instance'], '--document-name', config['document'], '--parameters', json.dumps({'Revision': [revision], 'Digest': [digest]}), '--comment', f'EJI production {revision}')['Command']['CommandId']
    print('SSM deployment command:', command, flush=True)
    for _ in range(120):
        try:
            result = aws('ssm', 'get-command-invocation', '--region', config['region'], '--command-id', command, '--instance-id', config['instance'])
        except subprocess.CalledProcessError:
            time.sleep(2)
            continue
        if result['Status'] == 'Success':
            print(result.get('StandardOutputContent', ''))
            break
        if result['Status'] in {'Cancelled', 'TimedOut', 'Failed', 'Cancelling'}:
            raise RuntimeError(json.dumps(result))
        time.sleep(2)
    else:
        raise TimeoutError('SSM deployment did not finish in four minutes')
    for attempt in range(20):
        try:
            with public_request(config['url'] + '/release.json?revision=' + revision) as response:
                assert json.load(response)['revision'] == revision
            for path in ('/', '/id/', '/terms.html', '/privacy.html', '/id/syarat-ketentuan.html', '/id/kebijakan-privasi.html', '/assets/style.css'):
                with public_request(config['url'] + path) as response:
                    assert response.status == 200
            print('Verified public HTTPS deployment:', config['url'], revision)
            return
        except Exception:
            if attempt == 19:
                raise
            time.sleep(3)


if __name__ == '__main__':
    main()
