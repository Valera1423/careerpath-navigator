import { useEffect, useMemo, useState } from 'react';
import {
  Background,
  Controls,
  ReactFlow,
  type Edge,
  type Node,
} from '@xyflow/react';
import dagre from '@dagrejs/dagre';
import { api } from '../api/client';
import type { CompassGraph } from '../types';
import '@xyflow/react/dist/style.css';

const NODE_W = 160;
const NODE_H = 50;

function layout(nodes: Node[], edges: Edge[]): Node[] {
  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: 'LR', nodesep: 40, ranksep: 80 });

  nodes.forEach((n) => g.setNode(n.id, { width: NODE_W, height: NODE_H }));
  edges.forEach((e) => g.setEdge(e.source, e.target));
  dagre.layout(g);

  return nodes.map((n) => {
    const pos = g.node(n.id);
    return { ...n, position: { x: pos.x - NODE_W / 2, y: pos.y - NODE_H / 2 } };
  });
}

export function CareerCompass() {
  const [graph, setGraph] = useState<CompassGraph | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.compass().then(setGraph).catch((e) => setError(String(e)));
  }, []);

  const styledNodes = useMemo(() => {
    if (!graph) return [];
    const laid = layout(
      graph.nodes.map((n) => ({ ...n, position: { x: 0, y: 0 } })) as Node[],
      graph.edges as Edge[],
    );
    return laid.map((n) => {
      const status = (n.data as { status: string }).status;
      return {
        ...n,
        style: {
          background: status === 'done' ? '#e3f6e8' : '#ffe3e3',
          border: `2px solid ${status === 'done' ? '#1f7a3d' : '#b3261e'}`,
          borderRadius: 12,
          fontSize: 13,
          padding: 8,
          width: NODE_W,
        },
      };
    });
  }, [graph]);

  if (error) return <p className="error">{error}</p>;
  if (!graph) return <p className="muted">Строим карту…</p>;

  return (
    <div className="screen">
      <h2>Карьерный компас</h2>
      <p className="muted small">
        Зелёные — уже освоено, красные — в плане. Стрелки — зависимости навыков.
      </p>
      <div style={{ height: 480, background: '#fff', borderRadius: 14 }}>
        <ReactFlow
          nodes={styledNodes}
          edges={graph.edges as Edge[]}
          fitView
          nodesDraggable={false}
          nodesConnectable={false}
        >
          <Background />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}