const fs = require('fs');
const path = require('path');

const files = [
  {
    path: 'C:/Claude_SPC/online-aps-cps-scheduler/frontend/src/components/common/VersionTag.tsx',
    replacements: [
      ["from '@/components/ui/badge'", "from '../ui/Badge'"],
      ["from '@/components/ui/button'", "from '../ui/Button'"]
    ]
  },
  {
    path: 'C:/Claude_SPC/online-aps-cps-scheduler/frontend/src/components/common/AIResultPanel.tsx',
    replacements: [
      ["from '@/components/ui/card'", "from '../ui/Card'"],
      ["from '@/components/ui/badge'", "from '../ui/Badge'"],
      ["from '@/components/ui/button'", "from '../ui/Button'"]
    ]
  },
  {
    path: 'C:/Claude_SPC/online-aps-cps-scheduler/frontend/src/components/common/AuditLogButton.tsx',
    replacements: [
      ["from '@/components/ui/dialog'", "from '../ui/Dialog'"],
      ["from '@/components/ui/button'", "from '../ui/Button'"],
      ["from '@/components/ui/badge'", "from '../ui/Badge'"],
      ["from '@/components/ui/scroll-area'", "from '../ui/ScrollArea'"]
    ]
  },
  {
    path: 'C:/Claude_SPC/online-aps-cps-scheduler/frontend/src/pages/DashboardPage.tsx',
    replacements: [
      ["from '@/components/ui/card'", "from '../components/ui/Card'"],
      ["from '@/components/ui/button'", "from '../components/ui/Button'"],
      ["from '@/components/ui/badge'", "from '../components/ui/Badge'"],
      ["from '@/components/ui/tabs'", "from '../components/ui/Tabs'"],
      ["from '@/components/common'", "from '../components/common'"]
    ]
  },
  {
    path: 'C:/Claude_SPC/online-aps-cps-scheduler/frontend/src/pages/QCostClassificationPage.tsx',
    replacements: [
      ["from '@/components/ui/card'", "from '../components/ui/Card'"],
      ["from '@/components/ui/button'", "from '../components/ui/Button'"],
      ["from '@/components/ui/badge'", "from '../components/ui/Badge'"],
      ["from '@/components/ui/input'", "from '../components/ui/Input'"],
      ["from '@/components/ui/dialog'", "from '../components/ui/Dialog'"],
      ["from '@/components/ui/select'", "from '../components/ui/Select'"],
      ["from '@/components/common'", "from '../components/common'"]
    ]
  },
  {
    path: 'C:/Claude_SPC/online-aps-cps-scheduler/frontend/src/pages/InspectionProcessDesignPage.tsx',
    replacements: [
      ["from '@/components/ui/card'", "from '../components/ui/Card'"],
      ["from '@/components/ui/button'", "from '../components/ui/Button'"],
      ["from '@/components/ui/badge'", "from '../components/ui/Badge'"],
      ["from '@/components/ui/select'", "from '../components/ui/Select'"],
      ["from '@/components/common'", "from '../components/common'"]
    ]
  },
  {
    path: 'C:/Claude_SPC/online-aps-cps-scheduler/frontend/src/pages/SPCChartPage.tsx',
    replacements: [
      ["from '@/components/ui/card'", "from '../components/ui/Card'"],
      ["from '@/components/ui/button'", "from '../components/ui/Button'"],
      ["from '@/components/ui/badge'", "from '../components/ui/Badge'"],
      ["from '@/components/ui/select'", "from '../components/ui/Select'"],
      ["from '@/components/common'", "from '../components/common'"]
    ]
  }
];

files.forEach(({ path, replacements }) => {
  if (fs.existsSync(path)) {
    let content = fs.readFileSync(path, 'utf8');
    replacements.forEach(([old, newStr]) => {
      content = content.replace(new RegExp(old.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), newStr);
    });
    fs.writeFileSync(path, content, 'utf8');
    console.log(`Updated: ${path}`);
  } else {
    console.log(`Not found: ${path}`);
  }
});

console.log('Done updating import paths!');
