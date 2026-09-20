from pathlib import Path
import subprocess, tempfile, uuid, json
repo=Path('/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-019-DATABASE-001')
out=Path(tempfile.mkdtemp(prefix='arch019-pg15-'))
db='arch019_rehearsal_'+uuid.uuid4().hex[:16]
base=['docker','exec','-i','-u','postgres','local_postgres']
created=False
code=1
print(str(out),flush=True)
with (out/'full.log').open('w') as log:
 def run(args,sql=None):
  log.write('\nCOMMAND: '+ ' '.join(args)+'\n');log.flush()
  subprocess.run(args,input=sql,stdout=log,stderr=subprocess.STDOUT,check=True,cwd=repo)
 def psql(sql): run(base+['psql','-X','-U','postgres','-d',db,'-v','ON_ERROR_STOP=1'],sql)
 try:
  run(['git','rev-parse','HEAD']);run(['git','status','--porcelain'])
  run(['docker','inspect','--format','{{.Id}} {{.Image}} {{.Config.Image}}','local_postgres'])
  run(base+['createdb','-U','postgres','--template=template0',db]);created=True
  psql(b'SELECT version();')
  target=repo/'prisma/migrations/20260920120000_arch019_merchant_recovery_read_indexes/migration.sql'
  for f in sorted((repo/'prisma/migrations').glob('*/migration.sql')):
   if f==target: break
   log.write('\nMIGRATION '+f.parent.name+'\n');psql(f.read_bytes())
  else: raise RuntimeError('Target migration absent')
  psql((repo/'scripts/fixtures/arch019-recovery-indexes-seed.sql').read_bytes())
  log.write('\nBEFORE PLANS\n');psql((repo/'scripts/fixtures/arch019-recovery-indexes-plans.sql').read_bytes())
  run(base+['psql','-X','-U','postgres','-d',db,'-v','ON_ERROR_STOP=1','--single-transaction'],target.read_bytes())
  psql((repo/'scripts/fixtures/arch019-recovery-indexes-assert.sql').read_bytes())
  log.write('\nAFTER PLANS\n');psql((repo/'scripts/fixtures/arch019-recovery-indexes-plans.sql').read_bytes())
  code=0
 finally:
  if created:
   try: run(base+['dropdb','-U','postgres',db])
   except Exception: code=1;raise
  log.write('\nEXIT CODE: '+str(code)+'\n')
  (out/'result.json').write_text(json.dumps({'exit_code':code,'database':db,'container':'local_postgres','evidence':str(out),'temporary_database_removed':created},indent=2))
print('Exit code: '+str(code),flush=True)
raise SystemExit(code)
