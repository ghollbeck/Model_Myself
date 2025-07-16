import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { getKnowledgeGraph } from '../utils/api';

interface NodeDatum extends d3.SimulationNodeDatum {
  id: string;
  type?: string;
  question?: string;
  answer?: string;
}

interface LinkDatum {
  source: string;
  target: string;
  relation?: string;
}

interface GraphData {
  nodes: NodeDatum[];
  links: LinkDatum[];
}

const CATEGORY_COLORS: Record<string, string> = {
  Knowledge: '#87ceeb',
  Feelings: '#90ee90',
  Personalities: '#ffa500',
  ImportanceOfPeople: '#ee82ee',
  Preferences: '#ffd700',
  Morals: '#fa8072',
  AutomaticQuestions: '#d3d3d3',
};

const NODE_RADIUS = 28;

const KnowledgeGraphD3: React.FC = () => {
  const svgRef = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    console.log('KnowledgeGraphD3 component mounted, fetching graph...');
    getKnowledgeGraph()
      .then((data: GraphData) => {
        console.log('Knowledge graph data received:', data);
        console.log('Nodes:', data.nodes?.length || 0, 'Links:', data.links?.length || 0);
        renderGraph(data);
      })
      .catch((error) => {
        console.error('Error fetching knowledge graph:', error);
      });
    // eslint-disable-next-line
  }, []);

  const renderGraph = (data: GraphData) => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous
    const width = 800;
    const height = 600;

    svg.attr('viewBox', `0 0 ${width} ${height}`);

    // Zoom and pan
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.2, 2])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });
    svg.call(zoom as any);

    const g = svg.append('g');

    // Simulation
    const simulation = d3.forceSimulation<NodeDatum>(data.nodes)
      .force('link', d3.forceLink<NodeDatum, LinkDatum>(data.links).id(d => d.id).distance(120))
      .force('charge', d3.forceManyBody().strength(-350))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // Draw links
    const link = g.append('g')
      .attr('stroke', '#aaa')
      .attr('stroke-width', 2)
      .selectAll('line')
      .data(data.links)
      .enter().append('line');

    // Draw nodes
    const node = g.append('g')
      .selectAll('circle')
      .data(data.nodes)
      .enter().append('circle')
      .attr('r', NODE_RADIUS)
      .attr('fill', d => CATEGORY_COLORS[d.type || ''] || '#ccc')
      .attr('stroke', '#333')
      .attr('stroke-width', 2)
      .call(drag(simulation));

    // Tooltips
    const tooltip = d3.select('body').append('div')
      .attr('class', 'd3-tooltip')
      .style('position', 'absolute')
      .style('z-index', '10')
      .style('visibility', 'hidden')
      .style('background', '#fff')
      .style('border', '1px solid #ccc')
      .style('padding', '8px')
      .style('border-radius', '6px')
      .style('font-size', '14px');

    node.on('mouseover', (event, d) => {
      tooltip.html(
        `<strong>${d.id}</strong><br/>` +
        (d.question ? `<em>Q:</em> ${d.question}<br/>` : '') +
        (d.answer ? `<em>A:</em> ${d.answer}` : '')
      )
        .style('visibility', 'visible');
    })
      .on('mousemove', (event) => {
        tooltip.style('top', (event.pageY + 10) + 'px')
          .style('left', (event.pageX + 10) + 'px');
      })
      .on('mouseout', () => {
        tooltip.style('visibility', 'hidden');
      });

    // Node labels
    const label = g.append('g')
      .selectAll('text')
      .data(data.nodes)
      .enter().append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', 5)
      .attr('font-size', 13)
      .attr('pointer-events', 'none')
      .text(d => d.type === 'category' ? d.id : (d.question ? d.question.slice(0, 22) + (d.question.length > 22 ? '…' : '') : d.id));

    simulation.on('tick', () => {
      link
        .attr('x1', d => (d.source as any).x)
        .attr('y1', d => (d.source as any).y)
        .attr('x2', d => (d.target as any).x)
        .attr('y2', d => (d.target as any).y);
      node
        .attr('cx', d => d.x as number)
        .attr('cy', d => d.y as number);
      label
        .attr('x', d => d.x as number)
        .attr('y', d => d.y as number);
    });
  };

  function drag(simulation: d3.Simulation<NodeDatum, undefined>) {
    function dragstarted(event: any, d: NodeDatum) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
    function dragged(event: any, d: NodeDatum) {
      d.fx = event.x;
      d.fy = event.y;
    }
    function dragended(event: any, d: NodeDatum) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
    return d3.drag<SVGCircleElement, NodeDatum>()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended);
  }

  return (
    <div style={{ width: '100%', textAlign: 'center', margin: '2rem 0' }}>
      <h2>Knowledge Graph Visualization</h2>
      <svg ref={svgRef} width={800} height={600} style={{ border: '1px solid #ccc', background: '#fafafa' }} />
    </div>
  );
};

export default KnowledgeGraphD3; 