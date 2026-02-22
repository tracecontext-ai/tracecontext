import fs from 'fs';
import path from 'path';

export const initCommand = () => {
    const gitDir = path.join(process.cwd(), '.git');
    if (!fs.existsSync(gitDir)) {
        console.error('Error: Not a git repository.');
        return;
    }

    const hooksDir = path.join(gitDir, 'hooks');
    const postCommitHook = path.join(hooksDir, 'post-commit');

    const hookScript = `#!/bin/bash
# TraceContext Git Hook
MESSAGE=$(git log -1 --pretty=%B)
DIFF=$(git diff HEAD~1 HEAD)
REPO_URL=$(git config --get remote.origin.url)

curl -X POST http://localhost:8000/events \\
  -H "Content-Type: application/json" \\
  -d "{
    \\"type\\": \\"git_commit\\",
    \\"data\\": {
      \\"message\\": \\"$MESSAGE\\",
      \\"diff\\": \\"$DIFF\\"
    },
    \\"metadata\\": {
      \\"repo\\": \\"$REPO_URL\\",
      \\"user\\": \\"$(whoami)\\"
    }
  }" 2>/dev/null &
`;

    fs.writeFileSync(postCommitHook, hookScript);
    fs.chmodSync(postCommitHook, '755');

    console.log('TraceContext initialized. Git hook installed.');
};
