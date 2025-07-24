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
  file_type?: string;
  file_size?: number;
  upload_date?: string;
  analysis_timestamp?: string;
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

    // Enhanced simulation with better clustering and positioning
    const linkDistance = isMobile ? 40 : 280; // Reduced base distance
    const chargeStrength = isMobile ? -100 : -2000; // Reduced repulsion for tighter clustering
    const collisionRadius = isMobile ? NODE_RADIUS + 1 : NODE_RADIUS + 3; // Smaller collision for tighter groups
    
    // Create positioning zones for different node types
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.25; // Zone radius
    
    // Define positions for main hubs in a circular arrangement
    const hubPositions: Record<string, {x: number, y: number}> = {
      'Documents': { x: centerX, y: centerY - radius * 0.8 }, // Top
      'Training': { x: centerX - radius * 0.7, y: centerY + radius * 0.4 }, // Bottom left
      'Knowledge': { x: centerX + radius * 0.3, y: centerY - radius * 0.3 }, // Top right
      'Feelings': { x: centerX - radius * 0.8, y: centerY - radius * 0.1 }, // Left
      'Personalities': { x: centerX + radius * 0.8, y: centerY + radius * 0.1 }, // Right
      'Preferences': { x: centerX + radius * 0.5, y: centerY + radius * 0.6 }, // Bottom right
      'Morals': { x: centerX - radius * 0.3, y: centerY + radius * 0.7 }, // Bottom
      'ImportanceOfPeople': { x: centerX - radius * 0.6, y: centerY - radius * 0.6 }, // Top left
      'AutomaticQuestions': { x: centerX + radius * 0.7, y: centerY - radius * 0.2 } // Right middle
    };
    
    const simulation = d3.forceSimulation<NodeDatum>(data.nodes)
      .force('link', d3.forceLink<NodeDatum, LinkDatum>(data.links)
        .id(d => d.id)
        .distance(d => {
          // Variable link distances based on relationship type
          if (d.relation === 'contains') return linkDistance * 0.6; // Tighter connection for document contents
          if (d.source === 'Documents' || d.target === 'Documents') return linkDistance * 1.8; // Medium distance to document hub
          if (d.source === 'Training' || d.target === 'Training') return linkDistance * 0.8; // Medium distance to training hub
          return linkDistance; // Default distance
        })
        .strength(1.2) // Stronger links for better clustering
      )
      .force('charge', d3.forceManyBody().strength(chargeStrength))
      .force('center', d3.forceCenter(centerX, centerY))
      .force('collision', d3.forceCollide(collisionRadius))
      // Add positioning forces for main hub nodes
      .force('positioning', d3.forceX<NodeDatum>()
        .x(d => {
          if (hubPositions[d.id]) return hubPositions[d.id].x;
          // For category nodes, position them closer to center
          if (d.type === 'category') return centerX + (Math.random() - 0.5) * radius * 0.5;
          return centerX;
        })
        .strength(d => {
          if (hubPositions[d.id]) return 0.3; // Strong positioning for main hubs
          if (d.type === 'category') return 0.1; // Moderate positioning for categories  
          return 0.05; // Weak positioning for other nodes
        })
      )
      .force('positioning-y', d3.forceY<NodeDatum>()
        .y(d => {
          if (hubPositions[d.id]) return hubPositions[d.id].y;
          // For category nodes, position them closer to center
          if (d.type === 'category') return centerY + (Math.random() - 0.5) * radius * 0.5;
          return centerY;
        })
        .strength(d => {
          if (hubPositions[d.id]) return 0.3; // Strong positioning for main hubs
          if (d.type === 'category') return 0.1; // Moderate positioning for categories
          return 0.05; // Weak positioning for other nodes
        })
      )
      // Add radial clustering force to group node types
      .force('radial', d3.forceRadial<NodeDatum>()
        .radius(d => {
          if (d.type === 'document_main' || d.type === 'training_main') return radius * 0.6; // Main hubs at medium distance
          if (d.type === 'category') return radius * 0.4; // Categories closer to center
          if (d.type === 'document_instance') return radius * 0.3; // Document instances close to center
          if (d.type === 'training_category') return radius * 0.5; // Training categories at medium distance
          return radius * 0.8; // QA nodes further out but contained
        })
        .x(centerX)
        .y(centerY)
        .strength(0.1) // Gentle radial clustering
      );

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
        if (d.type === 'training_main') {
          return TRAINING_MAIN_COLOR; // Blue for main training hub
        }
        if (d.type === 'training_category') {
          return TRAINING_CATEGORY_COLOR; // Light blue for training categories
        }
        if (d.type === 'training_qa') {
          return TRAINING_NODE_COLOR; // Red for training Q&A nodes
        }
        if (d.type === 'category') {
          return CATEGORY_COLORS[d.id] || '#808080'; // Use defined category colors
        }
        // For Q&A nodes, inherit color from parent category
        for (const [category, color] of Object.entries(CATEGORY_COLORS)) {
          if (d.id.startsWith(category + ':')) {
            return color;
          }
        }
        return '#808080'; // Gray for other nodes
      })
      .attr('stroke', '#333')
      .attr('stroke-width', 2)
      .call(drag(simulation));

    // Tooltips
    const tooltip = d3.select('body').append('div')
      .attr('class', 'd3-tooltip');

    node.on('mouseover', (event, d) => {
      let tooltipContent = `<strong>${d.id}</strong><br/>`;
      
      if (d.type === 'document_main') {
        tooltipContent += `<em>📁 Documents Hub</em><br/>`;
        tooltipContent += `<em>Contains all analyzed documents and their extracted knowledge</em>`;
      } else if (d.type === 'document_instance') {
        tooltipContent += `<em>📄 Document:</em> ${d.filename || 'Unknown file'}<br/>`;
        if (d.file_type) {
          tooltipContent += `<em>Type:</em> ${d.file_type}<br/>`;
        }
        if (d.file_size) {
          const sizeKB = Math.round(d.file_size / 1024);
          tooltipContent += `<em>Size:</em> ${sizeKB} KB<br/>`;
        }
        if (d.upload_date) {
          const uploadDate = new Date(d.upload_date).toLocaleDateString();
          tooltipContent += `<em>Uploaded:</em> ${uploadDate}<br/>`;
        }
        if (d.analysis_timestamp) {
          const analysisDate = new Date(d.analysis_timestamp).toLocaleDateString();
          tooltipContent += `<em>Analyzed:</em> ${analysisDate}<br/>`;
        }
        tooltipContent += `<em>Contains extracted knowledge from document analysis</em>`;
      } else if (d.type === 'training_main') {
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