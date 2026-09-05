"""Explicit-whitelist successor archive. Never overwrites the reviewed v1 ZIP."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent
FILES = ['README.md','PROOF.md','NOVELTY.md','REVIEW_RESPONSE.md','LICENSE.md','LICENSE-CODE',
         'verify.py','test_verify.py','witness.py','test_witness.py','scout.py','cover_scout.py',
         'freeze_certificates.py','requirements-discovery.txt','build_release.py','build_paper.py',
         'paper.tex','paper-body.tex','paper.pdf','references.bib','CITATION.cff','CLAIMS.json',
         'ENVIRONMENT.md','BUILD_INFO.json','verification.json','verification.stdout.txt',
         'tests.stdout.txt','examples/channel-witness.json','.gitignore','.github/workflows/replay.yml']
FILES += [f'certificates/{name}.json' for name in ('two','three','four','parity','five','six')]
EDITORIAL = ['editor-in-chief','methodology-specialist','domain-specialist','applications-specialist','devils-advocate','DECISION','RESPONSE']


def check_manifest():
    lines = (ROOT/'MANIFEST.sha256').read_text().splitlines()
    for line in lines:
        digest,name = line.split('  ',1)
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != digest:
            raise ValueError(f'manifest mismatch: {name}')
    print(f'{len(lines)} manifest hashes PASS')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--name', default='rbm31-exact-kl-radius-0.1.0-candidate')
    args = ap.parse_args()
    if args.check:
        check_manifest()
        return
    transcript = []
    for flags in ([],['-O']):
        for script in ('verify.py','test_verify.py','test_witness.py'):
            command = [sys.executable,*flags,script]
            if script == 'verify.py' and not flags:
                command += ['--out','verification.json']
            run = subprocess.run(command,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            transcript.append(' '.join(['python',*flags,script])+'\n'+run.stdout)
            if run.returncode:
                print(run.stdout)
                raise SystemExit(run.returncode)
            if script == 'verify.py' and not flags:
                (ROOT/'verification.stdout.txt').write_text(run.stdout)
    (ROOT/'tests.stdout.txt').write_text('\n'.join(transcript))
    info = {'status':'PRODUCER_REPLAY_PASS', 'problem':'AIM-PROBABILITY-0002', 'python':sys.version,
            'platform':platform.platform(),'version':'0.1.0-candidate','doi':'10.5281/zenodo.22339153',
            'normal_and_optimized':True,'formal_verification':False,'unaffiliated_review':False,
            'original_review_archive_sha256':'c9031bc194d6e165f563e3a67bd3658c7b419667b44d3e21233eb81ae5b19e66'}
    (ROOT/'BUILD_INFO.json').write_text(json.dumps(info,indent=2)+'\n')
    names = sorted(FILES + [f'editorial/{n}.md' for n in EDITORIAL if (ROOT/f'editorial/{n}.md').is_file()])
    for name in names:
        if not (ROOT/name).is_file():
            raise FileNotFoundError(name)
    manifest = ''.join(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in names)
    (ROOT/'MANIFEST.sha256').write_text(manifest)
    destination = ROOT.parent/(args.name+'.zip')
    if destination.name == 'AIM-PROBABILITY-0002-full-proof-review-v1.zip':
        raise ValueError('historical archive is protected')
    with ZipFile(destination,'w',compression=ZIP_DEFLATED,compresslevel=9) as archive:
        for name in [*names,'MANIFEST.sha256']:
            entry = ZipInfo('rbm31-exact-kl-radius/'+name, date_time=(2026,9,5,0,0,0))
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry,(ROOT/name).read_bytes())
    check_manifest()
    print(json.dumps({'archive':destination.name,'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'files':len(names)+1}))


if __name__ == '__main__':
    main()
