import React, { useEffect, useRef, useImperativeHandle, forwardRef } from 'react';
import * as d3 from 'd3';
import { getKnowledgeGraph } from '../utils/api';

interface NodeDatum extends d3.SimulationNodeDatum {
  id: string;
  type?: string;
  question?: string;
  answer?: string;
  question_id?: string;
  training_category?: string;
  answer_type?: string;
  timestamp?: string;
  filename?: string;
  document_id?: string;
}

interface LinkDatum {
  source: string;
  target: string;
  relation?: string;
}

interface GraphData {
  nodes: NodeDatum[];
  links: LinkDatum[];
  training_summary?: any;
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

const TRAINING_MAIN_COLOR = '#4169e1'; // Blue color for main Training node
const TRAINING_CATEGORY_COLOR = '#87ceeb'; // Light blue for training category subnodes
const TRAINING_NODE_COLOR = '#ff6b6b'; // Red for individual training Q&A nodes
const NODE_RADIUS = 28;

export interface KnowledgeGraphHandle {
  refresh: () => void;
}

const KnowledgeGraphD3 = forwardRef<KnowledgeGraphHandle>((props, ref) => {
  const svgRef = useRef<SVGSVGElement | null>(null);

  const fetchAndRenderGraph = async () => {
    try {
      console.log('Fetching knowledge graph from backend...');
      const data: GraphData = await getKnowledgeGraph();
      console.log('Knowledge graph data received:', data);
      console.log('Nodes:', data.nodes?.length || 0, 'Links:', data.links?.length || 0);
      if (data.training_summary) {
        console.log('Training data:', data.training_summary);
      }
      renderGraph(data);
    } catch (error) {
      console.error('Error fetching knowledge graph:', error);
    }
  };

  useImperativeHandle(ref, () => ({
    refresh: fetchAndRenderGraph
  }));

  useEffect(() => {
    console.log('KnowledgeGraphD3 component mounted, fetching graph...');
    fetchAndRenderGraph();
    // eslint-disable-next-line
  }, []);

  // Re-render graph on window resize for mobile optimization
  useEffect(() => {
    const handleResize = () => {
      if (svgRef.current) {
        getKnowledgeGraph()
          .then((data: GraphData) => {
            renderGraph(data);
          })
          .catch((error) => {
            console.error('Error re-rendering graph on resize:', error);
          });
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const renderGraph = (data: GraphData) => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous
    
    // Get container dimensions for responsive sizing
    const container = svgRef.current?.parentElement;
    const containerWidth = container?.clientWidth || 800;
    const isMobile = containerWidth < 480;
    
    const width = Math.min(800, containerWidth);
    const height = isMobile ? 500 : containerWidth < 768 ? 350 : 600;

    // Set viewBox for responsive scaling
    svg.attr('viewBox', `0 0 ${width} ${height}`)
       .attr('preserveAspectRatio', 'xMidYMid meet');

    // Zoom and pan with constraints (less zoom on mobile)
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([isMobile ? 0.5 : 0.3, isMobile ? 1.5 : 2])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });
    svg.call(zoom as any);

    const g = svg.append('g');

    // Simulation with responsive forces optimized for mobile
    const linkDistance = isMobile ? 60 : Math.min(120, width * 0.15);
    const chargeStrength = isMobile ? -150 : -Math.min(350, width * 0.4);
    const collisionRadius = isMobile ? NODE_RADIUS + 2 : NODE_RADIUS + 5;
    
    const simulation = d3.forceSimulation<NodeDatum>(data.nodes)
      .force('link', d3.forceLink<NodeDatum, LinkDatum>(data.links).id(d => d.id).distance(linkDistance))
      .force('charge', d3.forceManyBody().strength(chargeStrength))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide(collisionRadius));

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
      .attr('fill', d => {
        if (d.type === 'document_main' || d.type === 'document_instance') {
          return '#4169e1'; // Blue for document nodes
        }
        if (d.type === 'training_main' || d.type === 'training_category' || d.type === 'training_qa') {
          return '#ff6b6b'; // Red for all training-related nodes
        }
        return '#808080'; // Gray for all other nodes
      })
      .attr('stroke', '#333')
      .attr('stroke-width', 2)
      .call(drag(simulation));

    // Tooltips
    const tooltip = d3.select('body').append('div')
      .attr('class', 'd3-tooltip');

    node.on('mouseover', (event, d) => {
      let tooltipContent = `<strong>${d.id}</strong><br/>`;
      
      if (d.type === 'training_main') {
        tooltipContent += `<em>Main training hub containing all training categories</em>`;
      } else if (d.type === 'training_category') {
        tooltipContent += `<em>Training Category:</em> ${d.training_category}<br/>`;
        tooltipContent += `<em>Contains training questions and answers for this category</em>`;
      } else if (d.type === 'training_qa') {
        tooltipContent += `<em>Category:</em> ${d.training_category}<br/>`;
        tooltipContent += `<em>Type:</em> ${d.answer_type}<br/>`;
        tooltipContent += `<em>Q:</em> ${d.question}<br/>`;
        tooltipContent += `<em>A:</em> ${d.answer}`;
        if (d.timestamp) {
          const date = new Date(d.timestamp).toLocaleDateString();
          tooltipContent += `<br/><em>Date:</em> ${date}`;
        }
      } else {
        tooltipContent += (d.question ? `<em>Q:</em> ${d.question}<br/>` : '');
        tooltipContent += (d.answer ? `<em>A:</em> ${d.answer}` : '');
      }
      
      tooltip.html(tooltipContent)
        .style('visibility', 'visible');
    })
      .on('mousemove', (event) => {
        tooltip.style('top', (event.pageY + 10) + 'px')
          .style('left', (event.pageX + 10) + 'px');
      })
      .on('mouseout', () => {
        tooltip.style('visibility', 'hidden');
      });

    // Node labels with mobile optimization
    const fontSize = isMobile ? 10 : 13;
    const maxLabelLength = isMobile ? 15 : 22;
    
    const label = g.append('g')
      .selectAll('text')
      .data(data.nodes)
      .enter().append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', 5)
      .attr('font-size', fontSize)
      .attr('pointer-events', 'none')
      .text(d => {
        if (d.type === 'category') {
          return d.id;
        } else if (d.type === 'training_main') {
          return 'Training';
        } else if (d.type === 'training_category') {
          // Extract the category name from Training_CategoryName format
          const categoryName = d.id.replace('Training_', '');
          return categoryName;
        } else if (d.type === 'training_qa') {
          return d.question ? d.question.slice(0, maxLabelLength) + (d.question.length > maxLabelLength ? '…' : '') : d.id;
        } else {
          return d.question ? d.question.slice(0, maxLabelLength) + (d.question.length > maxLabelLength ? '…' : '') : d.id;
        }
      });

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
    <div className="knowledge-graph-container">
      <h2>Knowledge Graph Visualization</h2>
      <div className="knowledge-graph-svg-container">
        <svg ref={svgRef} />
      </div>
    </div>
  );
});

export default KnowledgeGraphD3; 