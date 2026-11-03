// Self-contained prepare hook for git-installed packages.
//
// pnpm runs this after `dsh plugin add "github:owner/repo#<sha>"` once the
// user allowlists the build (allowBuilds in the profile pnpm-workspace.yaml).
// pnpm installs devDependencies for git dependencies, so typescript is
// normally resolvable; there are no committed build artifacts to fall back
// to, so a missing compiler is a hard failure.
import { existsSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const root = dirname(dirname(fileURLToPath(import.meta.url)))
const tsc = join(root, 'node_modules', 'typescript', 'bin', 'tsc')

if (existsSync(tsc)) {
  const result = spawnSync(process.execPath, [tsc, '-p', 'tsconfig.json', '--noEmitOnError'], {
    cwd: root,
    stdio: 'inherit',
  })
  if (result.status !== 0) {
    process.exit(typeof result.status === 'number' ? result.status : 1)
  }
  // TS 5.9 does not rewrite `.ts` specifiers in declaration emit; fix them so
  // NodeNext declaration consumers can resolve lib.
  const fix = spawnSync(process.execPath, [join(root, 'scripts', 'fix-dts.mjs')], {
    cwd: root,
    stdio: 'inherit',
  })
  if (fix.status !== 0) {
    process.exit(typeof fix.status === 'number' ? fix.status : 1)
  }
  const bundle = spawnSync(process.execPath, [join(root, 'scripts', 'bundle-client.mjs')], {
    cwd: root,
    stdio: 'inherit',
  })
  if (bundle.status !== 0) {
    process.exit(typeof bundle.status === 'number' ? bundle.status : 1)
  }
  process.exit(0)
}

console.error('dsh-github prepare: no TypeScript compiler available — build failed')
process.exit(1)
