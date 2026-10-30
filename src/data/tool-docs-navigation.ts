export const toolDocs = {
  'stem-splitter': {
    title: 'Stem Splitter Docs',
    basePath: '/stem-splitter-docs/',
    appUrl: 'https://stem-splitter.ailab-452.workers.dev/',
    groups: [
      { title: 'Getting Started', pages: [['getting-started', 'Getting Started'], ['splitter-basics', 'Splitter Basics']] },
      { title: 'Listen & Analyze', pages: [['mixer', 'The Mixer'], ['notes', 'Notes'], ['listening-guy', 'Listening Guy'], ['export-and-sharing', 'Export & Sharing']] },
      { title: 'Teach & Share', pages: [['classroom', 'Class Workspace'], ['live-sessions', 'Live Sessions'], ['instructor-console', 'Instructor Console'], ['teaching-tips', 'Teaching Tips'], ['sample-activities', 'Sample Activities'], ['student-onboarding', 'Student Onboarding'], ['use-cases', 'Use Cases']] },
      { title: 'Related', pages: [['privacy-and-limits', 'Privacy & Limits']] },
    ],
  },
  'systems-mapping': {
    title: 'Systems Mapping Docs',
    basePath: '/systems-mapping-docs/',
    appUrl: 'https://systems-mapping.ailab-452.workers.dev/',
    groups: [
      { title: 'Getting Started', pages: [['getting-started', 'Getting Started'], ['workspace-basics', 'Workspace Basics']] },
      { title: 'Build & Interpret', pages: [['levels', 'The Four Levels'], ['memo-and-suggestions', 'Memo & Suggestions'], ['map', 'The Map'], ['evidence-and-field-notes', 'Evidence & Field Notes'], ['export-and-sharing', 'Export & Sharing']] },
      { title: 'Teach & Review', pages: [['course-access', 'Course Access'], ['instructor-console', 'Instructor Console'], ['teaching-tips', 'Teaching Tips'], ['sample-activities', 'Sample Activities'], ['student-onboarding', 'Student Onboarding'], ['use-cases', 'Use Cases']] },
      { title: 'Related', pages: [['privacy-and-limits', 'Privacy & Limits']] },
    ],
  },
};
export type ToolGuide = keyof typeof toolDocs;
