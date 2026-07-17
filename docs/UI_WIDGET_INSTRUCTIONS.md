# 🎨 NitroStack UI Widget Mapping Specifications

This document outlines the frontend UI rendering directives for **Domain 3 (Design & UI)**. These instructions are tailored specifically for the **NitroStack Compose Model** to compile interactive React widgets from the tool execution outputs.

> [!IMPORTANT]
> **DO NOT alter the backend Python logic.** Only render the frontend UI by parsing the structured JSON output payloads returned by the tools.

---

## 🛠️ 1. Framework Health Dashboard (Tool: `check_repo_health`)

When rendering the health telemetry and supply chain risk scorecards, map the payload directly to a custom dashboard widget:

```tsx
import { Widget, Grid, Card, Gauge, List, Item, Badge } from '@nitrostack/widgets';

export default function FrameworkHealthDashboard({ data }) {
  // Expected JSON structure:
  // {
  //   "health_score": number (0-100),
  //   "status": string,
  //   "metrics": { "cve_count": number, "last_commit_date": string, "contributors_count": number },
  //   "flags": string[]
  // }
  
  const isHealthy = data.health_score > 70;
  const cveSeverity = data.metrics.cve_count > 0 ? "critical" : "success";

  return (
    <Widget title={`Framework Health: ${data.metrics.repo}`} icon="pulse">
      <Grid columns={3} gap={4}>
        
        {/* Score Gauge */}
        <Card title="Maintenance score" value={`${data.health_score}/100`}>
          <Gauge value={data.health_score} min={0} max={100} color={isHealthy ? "green" : "red"} />
          <Badge type={isHealthy ? "success" : "warning"} label={data.status} />
        </Card>
        
        {/* Critical Metrics */}
        <Card title="Vulnerability Count">
          <Gauge value={data.metrics.cve_count} min={0} max={20} color={data.metrics.cve_count > 0 ? "red" : "green"} />
          <Badge type={cveSeverity} label={`${data.metrics.cve_count} Known CVEs`} />
        </Card>
        
        {/* Vital Stats */}
        <Card title="Vital Metrics">
          <List>
            <Item icon="calendar" label="Last Commit" value={data.metrics.last_commit_date} />
            <Item icon="people" label="Active Contributors" value={`${data.metrics.contributors_count}+`} />
            <Item icon="archive" label="Archived State" value={data.metrics.archived ? "Yes" : "No"} />
          </List>
        </Card>
        
      </Grid>
      
      {/* Risk Alerts */}
      {data.flags && data.flags.length > 0 && (
        <Card title="🚨 Critical Risk Flags" style={{ marginTop: '16px', border: '1px solid red' }}>
          <List>
            {data.flags.map((flag, idx) => (
              <Item key={idx} icon="warning" text={flag} />
            ))}
          </List>
        </Card>
      )}
    </Widget>
  );
}
```

---

## 🎨 2. Design Moodboard & Analogies (Tool: `breed_concepts`)

When cross-pollinating architectural frameworks or mapping cross-domain biology/materials-science analogies, build a multi-dimensional Moodboard displaying lineage, LaTeX code equations, and prompt catalysts:

```tsx
import { Widget, Tab, TabList, TabPanel, Text, Code, Button } from '@nitrostack/widgets';

export default function DesignMoodboard({ data }) {
  // Expected JSON structure:
  // {
  //   "status": "hybridization_complete",
  //   "lineage": { "parent_primary": string, "parent_secondary": string },
  //   "synthesis_payload": {
  //     "paradigm_name": string,
  //     "structural_bridge": string,
  //     "hybrid_mechanics": string,
  //     "mathematical_grafting_formula": string,
  //     "critical_tradeoffs": string[],
  //     "bridge_catalyst_prompt": string
  //   }
  // }
  
  const payload = data.synthesis_payload;

  return (
    <Widget title={`Design Moodboard: ${payload.paradigm_name}`} icon="palette">
      <Text variant="h2" style={{ marginBottom: '8px' }}>Lineage Link: {data.lineage.parent_primary} 🧬 {data.lineage.parent_secondary}</Text>
      <Text variant="body" style={{ marginBottom: '16px', color: '#666' }}>{payload.structural_bridge}</Text>
      
      <TabList>
        
        {/* Tab 1: Hybrid Mechanics */}
        <Tab label="⚙️ Mechanics">
          <TabPanel>
            <Text variant="h3">Mechanics & Integration Flow</Text>
            <Text variant="body">{payload.hybrid_mechanics}</Text>
            <Text variant="h4" style={{ marginTop: '12px' }}>Critical Tradeoffs:</Text>
            <ul>
              {payload.critical_tradeoffs.map((item, idx) => (
                <li key={idx}><Text variant="body">{item}</Text></li>
              ))}
            </ul>
          </TabPanel>
        </Tab>
        
        {/* Tab 2: Mathematical Formula */}
        <Tab label="🧮 Math Formula">
          <TabPanel>
            <Text variant="h3">LaTeX Equation Matrix</Text>
            <Code language="latex" style={{ display: 'block', padding: '16px', backgroundColor: '#fafafa', borderRadius: '8px' }}>
              {payload.mathematical_grafting_formula}
            </Code>
            <Text variant="caption" style={{ marginTop: '8px', display: 'block' }}>
              Formula maps the vector density transfer weights between systems.
            </Text>
          </TabPanel>
        </Tab>
        
        {/* Tab 3: Catalyst Prompt */}
        <Tab label="⚡ Catalyst Prompt">
          <TabPanel>
            <Text variant="h3">Prompt Template for LLM Generation</Text>
            <Code language="markdown" style={{ display: 'block', padding: '16px', backgroundColor: '#f0f4f8', borderRadius: '8px', marginBottom: '12px' }}>
              {payload.bridge_catalyst_prompt}
            </Code>
            <Button 
              label="Copy Prompt to Clipboard" 
              onClick={() => navigator.clipboard.writeText(payload.bridge_catalyst_prompt)}
              icon="copy"
            />
          </TabPanel>
        </Tab>
        
      </TabList>
    </Widget>
  );
}
```
